from rest_framework import permissions


class IsSuperUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.role == 'moderator'
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
    

class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or (
                request.user.is_authenticated and (
                    obj.author == request.user or request.user.is_superuser or request.user.role in ('admin', 'moderator')
                )
            )
        )
