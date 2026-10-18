from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.is_superuser:
            return True
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.is_admin)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_admin:
            return True
        if hasattr(obj, 'user'):
            return obj.user == profile
        return obj == profile