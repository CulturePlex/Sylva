from graphs.models import Graph
from guardian import shortcuts as guardian
from rest_framework import permissions


ADD_PERM = "add_data"
CHANGE_PERM = "change_data"
DELETE_PERM = "delete_data"
VIEW_PERM = "view_data"

ADD_METHODS = ['POST']
CHANGE_METHODS = ['PATCH', 'PUT']
DELETE_METHODS = ['DELETE']
VIEW_METHODS = ['GET']


class DataAdd(permissions.BasePermission):
    """
    Custom permission to add data to the graph.
    Only for POST.
    """

    def has_object_permission(self, request, view, obj):
        is_graph = isinstance(obj, Graph)
        method_correct = request.method in ADD_METHODS
        if is_graph and method_correct:
            # We get the permissions of the graph for the user
            user = request.user
            graph = obj
            perms = guardian.get_perms(user, graph)

            # We check if the user has the perms or is the graph owner
            is_owner = user == graph.owner
            has_perms = ADD_PERM in perms

            return is_owner or has_perms
        return True


class DataChange(permissions.BasePermission):
    """
    Custom permission to modify the graph data.
    Only for PATCH and PUT.
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


class DataDelete(permissions.BasePermission):
    """
    Custom permission to delete data.
    Only for DELETE.
    """

    def has_object_permission(self, request, view, obj):
        is_graph = isinstance(obj, Graph)
        method_correct = request.method in DELETE_METHODS
        if is_graph and method_correct:
            # We get the permissions of the graph for the user
            user = request.user
            graph = obj
            perms = guardian.get_perms(user, graph)

            # We check if the user has the perms or is the graph owner
            is_owner = user == graph.owner
            has_perms = DELETE_PERM in perms

            return is_owner or has_perms
        return True


class DataView(permissions.BasePermission):
    """
    Custom permission to view the graph data.
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
