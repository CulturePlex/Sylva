from graphs.models import Graph
from guardian import shortcuts as guardian
from rest_framework import permissions


CHANGE_PERM = "change_schema"
VIEW_PERM = "view_schema"

CHANGE_METHODS = ['POST', 'PATCH', 'PUT', 'DELETE']
VIEW_METHODS = ['GET']


class SchemaChange(permissions.BasePermission):
    """
    Custom permission to modify a schema.
    Only for PATCH, PUT and DELETE.
    """

    def has_object_permission(self, request, view, obj):
        is_graph = isinstance(obj, Graph)
        method_correct = request.method in CHANGE_METHODS
        if is_graph and method_correct:
            # We get the permissions of the graph for the user
            user = request.user
            graph = obj
            perms = guardian.get_perms(user, graph)

            # We check if the user has the perms or is the graph owner
            is_owner = user == graph.owner
            has_perms = CHANGE_PERM in perms

            return is_owner or has_perms
        return True


class SchemaView(permissions.BasePermission):
    """
    Custom permission to view a graph schema.
    Only for GET methods.
    """

    def has_object_permission(self, request, view, obj):
        is_graph = isinstance(obj, Graph)
        method_correct = request.method in VIEW_METHODS
        if is_graph and method_correct:
            # We get the permissions of the graph for the user
            user = request.user
            graph = obj
            perms = guardian.get_perms(user, graph)

            # We check if the user has the perms or is the graph owner
            is_owner = user == graph.owner
            has_perms = VIEW_PERM in perms

            return is_owner or has_perms
        return True
