# accounts/permissions.py
from rest_framework import permissions


class IsAdminUserRole(permissions.BasePermission):
    """Allow access only to admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'SUPER_ADMIN']


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to super admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'


class CanManageProjects(permissions.BasePermission):
    """Check if user can manage projects."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role in ['ADMIN', 'SUPER_ADMIN'] or 
            request.user.is_staff
        )