"""Reusable DRF permission classes for role-based access control."""

from rest_framework import permissions

from .models import User


class IsAdmin(permissions.BasePermission):
    """Only platform administrators."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and (request.user.role == User.Role.ADMIN or request.user.is_staff)
        )


class IsSeller(permissions.BasePermission):
    """Farmers and wholesalers may create/manage listings."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_seller
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level: only the owner can modify; everyone may read."""

    owner_field = 'seller'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, getattr(view, 'owner_field', self.owner_field), None)
        return owner == request.user
