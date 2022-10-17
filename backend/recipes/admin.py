from django.contrib import admin
from django.utils.safestring import mark_safe
from recipes.models import Ingredient, IngredientsInRecipe, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    """Отображение модели тегов в админ-панели."""

    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )

    list_display_links = (
        'id',
        'name',
    )


class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели ингридиентов в админ-панели."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_display_links = (
        'id',
        'name',
    )
    list_filter = (
        'name',
    )


class IngredientsInRecipeInLine(admin.TabularInline):
    """Отображение модели ингридиентов в админ-модели рецептов."""

    model = IngredientsInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели рецептов в админ-панели."""

    model = Recipe
    inlines = (IngredientsInRecipeInLine, )
    search_fields = ('name',)
    list_filter = (
        'name',
        'author',
        'tags',
    )

    def get_num_of_uses(self, obj):
        """Подсчёт количества добавления рецепта в избранное."""
        return obj.favorite_recipes.count()

    get_num_of_uses.short_description = (
        'Количество добавления рецепта в избранное'
    )

    list_display = (
        'id',
        'name',
        'author',
        'preview_images',
    )

    list_display_links = (
        'id',
        'name',
    )

    fields = (
        'author',
        'name',
        'get_num_of_uses',
        'image',
        'preview_image',
        'text',
        'tags',
        'cooking_time',
    )

    readonly_fields = (
        'get_num_of_uses',
        'preview_image'
    )

    def preview_images(self, obj):
        """Превью картинки на странице модели."""

        return mark_safe(f'<img src="{obj.image.url}" width=50>')

    def preview_image(self, obj):
        """Превью картинки на странице экземпляра модели."""

        return mark_safe(f'<img src="{obj.image.url}" width=200>')

    preview_images.short_description = "Миниатюра"
    preview_image.short_description = "Миниатюра"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
