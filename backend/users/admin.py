from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """Отображение модели пользователей в админ-панели."""

    list_display = (
        'pk',
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email'
    )
    list_filter = (
        'username',
        'email',
    )
    list_display_links = (
        'pk',
        'username',
        'email',
    )
    empty_value_display = '-пусто-'
    save_on_top = True


admin.site.register(User, CustomUserAdmin)
