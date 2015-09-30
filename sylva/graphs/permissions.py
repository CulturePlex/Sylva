from graphs.models import Graph
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # We check only the Graph
        if isinstance(obj, Graph):
            return obj.owner == request.user
        return True


class IsCollaborator(permissions.BasePermission):
    """
    Custom permission to allow collaborators of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # We check only the Graph
        if isinstance(obj, Graph):
            return request.user in obj.get_collaborators()
        return True
