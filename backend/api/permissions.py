from rest_framework import permissions


class IsAuthorOrStuffOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение, позволяющее доступ только автору, персоналу или для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user == obj.author
                or request.user.is_staff)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение, позволяющее доступ только администраторам или для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user and request.user.is_staff)
