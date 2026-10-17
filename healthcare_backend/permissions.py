from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission allowing only owners of an object to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "created_by", None) == request.user
