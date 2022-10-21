from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from recipes.models import Ingredient, IngredientsInRecipe, Recipe, Tag

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки на пользователя."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscribe.filter(id=obj.id).exists()


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов с ограничееным набором полей."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__', )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор подписок пользователей."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count',
            'recipes'
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        """Получение рецептов пользователя."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipesShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Подсчёт рецептов пользователя."""
        return obj.recipes.count()


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор Тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов."""

    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

        read_only_fields = (
            'id',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):
        """Проверка данных при создании/изменении рецепта."""

        name = self.initial_data.get('name')
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if tags:
            self.check_data_as_list(tags)
            for tag in tags:
                self.check_value_for_validate(tag, Tag)
            data['tags'] = tags

        if ingredients:
            self.check_data_as_list(ingredients)
            valid_ingredients = []
            for ing in ingredients:
                ing_id = ing.get('id')
                ingredient = self.check_value_for_validate(ing_id, Ingredient)
                ingredient = ing.get('id')

                amount = ing.get('amount')
                self.check_value_for_validate(amount)

                valid_ingredients.append(
                    {'ingredient': ingredient, 'amount': amount}
                )
            data['ingredients'] = valid_ingredients

        if name:
            data['name'] = str(name).strip().capitalize()
        else:
            name = str(Recipe.objects.filter(id=self.context.get('id')))

        data['author'] = self.context.get('request').user
        return data

    def check_data_as_list(self, value):
        """Проверка формата параметров ingridients и tags."""
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f'{value} должен быть в формате списка!'
            )

    def check_value_for_validate(self, value, klass=None) -> None:
        """Проверяет корректность переданного значения."""

        if not str(value).isdecimal():
            raise ValidationError(
                f'Вместо {value} должно быть цифровое значение!'
            )
        if klass:
            obj = klass.objects.filter(id=value)
            if not obj:
                raise ValidationError(
                    f'{klass._meta.verbose_name} {value} не существует!'
                )
            return obj[0]

    def get_ingredients(self, obj):
        """Получить список ингридиентов рецепта."""
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientsinrecipe__amount')
        )

    def get_is_favorited(self, obj):
        """Проверка - добавлен ли рецеп в избранное."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка - добавлен ли рецеп в список покупок."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def create(self, validated_data):
        """Создание рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    def create_ingredients_amounts(self, ingredients, recipe):
        """
        Создание записи о количестве ингридиентов рецепта в сквозной таблице.
        """

        IngredientsInRecipe.objects.bulk_create(
            [IngredientsInRecipe(
                ingredients=Ingredient.objects.get(
                    id=ingredient['ingredient']
                ),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def update(self, recipe, validated_data):
        """Изменение рецепта."""

        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)

        if tags:
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients_amounts(
                recipe=recipe,
                ingredients=ingredients
            )
        recipe.save()
        return recipe
