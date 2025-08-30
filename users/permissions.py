from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access only to admin users"""
    def has_permission(self, request, view):
        user = request.user
        # Check if user is superuser or has role named 'admin'
        return bool(
            user and user.is_authenticated and 
            (user.is_superuser or (user.role and user.role.name == 'admin'))
        )

class HasRole(BasePermission):
    """Allows access only to users with allowed roles"""
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and 
            (user.role and user.role.name in self.allowed_roles)
        )
