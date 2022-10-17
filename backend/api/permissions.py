from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Разрешение на создание/изменение контента только для админов,
    остальным только чтение.
    """
    def has_permission(self, request, view):
        return (
            request.method in ('GET',)
            or request.user.is_staff
        )


class IsAdminOrAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение на создание/изменение контента только для админов и авторов,
    либо только чтение.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in ('GET',)
                or obj.author == request.user
                or request.user.is_staff)
