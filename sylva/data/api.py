# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import get_object_or_404

from graphs.models import Graph
from data.forms import NodeForm
from data.serializers import (GetNodesSerializer, GetRelationshipsSerializer,
                              NodeSerializer, RelationshipSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class GetNodesView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of nodes that belongs to type_slug
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        nodetype = (
            graph.schema.nodetype_set.all().filter(slug=type_slug)[0])

        serializer = GetNodesSerializer(nodetype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new node of a type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        nodetype = (
            graph.schema.nodetype_set.all().filter(slug=type_slug)[0])

        # We get the post data
        data = request.data

        node_form = NodeForm(graph=graph, itemtype=nodetype, data=data,
                             user=request.user.username)

        if data and node_form.is_valid():
            with transaction.atomic():
                node_form.save()
                return Response(status=status.HTTP_201_CREATED)

        return Response(node_form.errors, status=status.HTTP_400_BAD_REQUEST)


class GetRelationshipsView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of relationships that belongs to type_slug
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        relationshiptype = (
            graph.schema.relationshiptype_set.all().filter(slug=type_slug)[0])

        serializer = GetRelationshipsSerializer(relationshiptype)

        return Response(serializer.data)

    def post(self, request, graph_slug, format=None):
        """
        Create a new relationship of allowed relationship
        """
        pass


class NodeView(APIView):

    def get(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Returns information about a node
        """
        graph = get_object_or_404(Graph, slug=graph_slug)

        node = graph.nodes.get(node_id)
        serializer = NodeSerializer(node)

        return Response(serializer.data)

    def delete(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Delete the node with id equals to node_id
        """
        graph = get_object_or_404(Graph, slug=graph_slug)

        node = graph.nodes.get(node_id)
        serializer = NodeSerializer(node)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelationshipView(APIView):

    def get(self, request, graph_slug, type_slug, relationship_id,
            format=None):
        """
        Returns information about a relationship
        """
        graph = get_object_or_404(Graph, slug=graph_slug)

        relationship = graph.relationships.get(relationship_id)
        serializer = RelationshipSerializer(relationship)

        return Response(serializer.data)

    def delete(self, request, graph_slug, type_slug, relationship_id,
               format=None):
        """
        Delete the relationship with id equals to relationship_id
        """
        graph = get_object_or_404(Graph, slug=graph_slug)

        relationship = graph.relationships.get(relationship_id)
        serializer = RelationshipSerializer(relationship)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
