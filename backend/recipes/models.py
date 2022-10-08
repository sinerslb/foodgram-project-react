from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    """Теги."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=100,
        unique=True,
        blank=False,
    )

    color_code = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        unique=True,
        blank=False,
    )

    slug = models.SlugField(
        unique=True,
        max_length=30,
        verbose_name='slug тега',
        blank=False,
    )

    class Meta:
        ordering = ['id', ]
        verbose_name_plural = 'Теги'
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100,
        blank=False,
    )

    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=10,
        blank=False,
    )

    class Meta:
        ordering = ['id', ]
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=100,
    )

    image = models.ImageField(
        upload_to='recipes/',
        # blank=True,
        verbose_name='Изображение'
    )

    description = models.TextField(
        verbose_name='Описание рецепта',
    )

    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='QuantityIngredientsInRecipe',
        blank=False,
    )

    class Meta:
        ordering = ['id', ]
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class QuantityIngredientsInRecipe(models.Model):
    """Количество ингредиента в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='base_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    quantity = models.FloatField(
        blank=False,
        null=False,
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингридиентов в рецепте'
        verbose_name_plural = 'Количество ингридиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipes'
            )
        ]


class FavoritesList(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        User,
        related_name='fan',
        on_delete=models.CASCADE,
        blank=False,
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipes'
            )
        ]


class ShoppingList(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        User,
        related_name='shopper',
        on_delete=models.CASCADE,
        blank=False,
    )

    recipe = models.ForeignKey(
        Recipe,
        related_name='shopper_recipes',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopper_recipes'
            )
        ]


class Follow(models.Model):
    """Подписки."""

    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )

    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
