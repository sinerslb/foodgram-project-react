from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from recipes.validators import validate_min_amount

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    """Теги."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=100,
        unique=True,
        blank=False,
    )

    color = models.CharField(
        'Цвет', help_text=('Введите код цвета в шестнадцетиричном формате '
                           '(#ABCDEF)'),
        max_length=7, validators=(
            RegexValidator(
                regex='^#[a-ef-F0-9]{6}$', code='wrong_hex_code',
                message='Неправильный формат цвета'), ))

    slug = models.SlugField(
        unique=True,
        verbose_name='slug тега',
        blank=False,
    )

    class Meta:
        ordering = ['name', ]
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
        ordering = ['name', ]
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
        verbose_name='Изображение'
    )

    text = models.TextField(
        verbose_name='Описание рецепта',
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        blank=False,
    )

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!'),
        ],
        blank=False,
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    favorite = models.ManyToManyField(
        User,
        blank=True,
        related_name='favorites',
        verbose_name='Любимые рецепты',
    )

    cart = models.ManyToManyField(
        User,
        blank=True,
        related_name='carts',
        verbose_name='Список покупок',
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """Количество ингредиента в рецепте."""

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Количество',
        blank=False,
        validators=(
            validate_min_amount,
        )

    )

    class Meta:
        verbose_name = 'Количество ингридиентов в рецепте'
        verbose_name_plural = 'Количество ингридиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='unique_ingredient_in_recipes'
            )
        ]
