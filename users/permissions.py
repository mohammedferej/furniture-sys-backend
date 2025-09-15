from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access only to users in the 'admin' group or superusers"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name='admin').exists()


class HasGroup(BasePermission):
    """Allows access only to users in allowed groups"""
    def __init__(self, allowed_groups=None):
        self.allowed_groups = allowed_groups or []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name__in=self.allowed_groups).exists()
