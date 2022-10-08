from django.contrib import admin
from django.utils.safestring import mark_safe
from recipes.models import Ingredient, QuantityIngredientsInRecipe, Recipe, Tag


class TagAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'color_code',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


class QuantityIngredientsInRecipeInLine(admin.TabularInline):

    model = QuantityIngredientsInRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):

    model = Recipe
    inlines = (QuantityIngredientsInRecipeInLine, )
    search_fields = ('name',)
    list_filter = (
        'name',
        'author',
        'tags',
    )

    def get_num_of_uses(self, obj):
        """
        Подсчёт количества добавления рецепта в избранное.
        """
        return obj.favorite_recipes.count()

    get_num_of_uses.short_description = (
        'Количество добавления рецепта в избранное'
    )

    list_display = (
        'name',
        'author',
        'preview_images',
    )

    fields = (
        'author',
        'name',
        'get_num_of_uses',
        'image',
        'preview_image',
        'description',
        'tags',
    )

    readonly_fields = (
        'get_num_of_uses',
        'preview_image'
    )

    def preview_images(self, obj):
        """
        Превью картинки на странице модели.
        """
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width=50>')

    def preview_image(self, obj):
        """
        Превью картинки на странице экземпляра модели.
        """
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width=300>')

    preview_images.short_description = "Миниатюра"
    preview_image.short_description = "Миниатюра"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
