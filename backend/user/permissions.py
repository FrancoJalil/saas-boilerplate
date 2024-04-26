from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsVerifiedPermission(permissions.BasePermission):
    
    message = 'User account must be verified to make this action.'
    def has_permission(self, request, view):
        if bool(request.user and request.user.verified):
            return True
        raise PermissionDenied(detail=self.message, code="user_not_verified")

    def has_object_permission(self, request, view, obj):
        if bool(request.user and request.user.verified):
            return True
        raise PermissionDenied(detail=self.message, code="user_not_verified")
    
