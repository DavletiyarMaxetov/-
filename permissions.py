from rest_framework.permissions import BasePermission, SAFE_METHODS

class HasProfile(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and hasattr(user, "profile"))

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and hasattr(request.user, "profile") and request.user.profile.is_customer)

class IsExecutor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and hasattr(request.user, "profile") and request.user.profile.is_executor)

class IsJobOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and obj.owner_id == request.user.id)

class IsAssignedExecutor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and obj.assigned_to_id == request.user.id)