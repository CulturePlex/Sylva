from graphs.models import Graph
from guardian import shortcuts as guardian
from rest_framework import permissions


CHANGE_PERM = "change_graph"
VIEW_PERM = "view_graph"

CHANGE_METHODS = ['POST', 'PATCH', 'PUT', 'DELETE']
VIEW_METHODS = ['GET']


class GraphChange(permissions.BasePermission):
    """
    Custom permission to modify a graph.
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

            return CHANGE_PERM in perms
        return True


class GraphView(permissions.BasePermission):
    """
    Custom permission to view a graph.
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

            return VIEW_PERM in perms
        return True
