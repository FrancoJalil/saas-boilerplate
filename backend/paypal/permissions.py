from rest_framework import permissions

class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to edit the object.
    """

    def has_permission(self, request, view):
        # Solo permite el acceso a superusuarios para operaciones de escritura
        return request.user and request.user.is_superuser

