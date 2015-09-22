# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import get_object_or_404

from graphs.models import Graph
from graphs.permissions import IsOwner
from schemas.models import NodeType, RelationshipType
from data.forms import NodeForm
from data.serializers import (GetNodesSerializer, GetRelationshipsSerializer,
                              NodeSerializer, RelationshipSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class GetNodesView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of nodes that belongs to type_slug
        """

        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = GetNodesSerializer(nodetype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new node of a type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of relationships that belongs to type_slug
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = GetRelationshipsSerializer(relationshiptype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new relationship of allowed relationship
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        # We get the post data
        data = request.data
        source_id = data['source_id']
        target_id = data['target_id']
        reltype_id = str(relationshiptype.id)

        # We create the relationship
        graph.relationships.create(
            source=source_id, target=target_id, label=reltype_id)

        return Response(status=status.HTTP_201_CREATED)


class NodeView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Returns information about a node
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        node = graph.nodes.get(node_id)
        serializer = NodeSerializer(node)

        return Response(serializer.data)

    def patch(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Edit properties of a node
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        node = graph.nodes.get(node_id)

        new_data = dict()
        new_data['id'] = post_data.get('id', node.id)
        new_data['label'] = post_data.get('label', node.label)
        new_data['label_display'] = (
            post_data.get('label_display', node.label_display))
        new_data['properties'] = (
            post_data.get('properties', node.properties))

        serializer = NodeSerializer(node, data=new_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Edit properties of a node. Omitted properties are removed
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        node = graph.nodes.get(node_id)

        new_data = dict()
        new_data['id'] = post_data.get('id', node.id)
        new_data['label'] = post_data.get('label', node.label)
        new_data['label_display'] = (
            post_data.get('label_display', node.label_display))
        new_data['properties'] = (
            post_data.get('properties', None))

        serializer = NodeSerializer(node, data=new_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, graph_slug, type_slug, node_id, format=None):
        """
        Delete the node with id equals to node_id
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        node = graph.nodes.get(node_id)
        serializer = NodeSerializer(node)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelationshipView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, relationship_id,
            format=None):
        """
        Returns information about a relationship
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationship = graph.relationships.get(relationship_id)
        serializer = RelationshipSerializer(relationship)

        return Response(serializer.data)

    def patch(self, request, graph_slug, type_slug, relationship_id,
              format=None):
        """
        Edit properties of a relationship
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        relationship = graph.relationships.get(relationship_id)

        new_data = dict()
        new_data['id'] = post_data.get('id', relationship.id)
        new_data['label'] = post_data.get('label', relationship.label)
        new_data['label_display'] = (
            post_data.get('label_display', relationship.label_display))
        new_data['properties'] = (
            post_data.get('properties', relationship.properties))

        serializer = RelationshipSerializer(relationship, data=new_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, graph_slug, type_slug, relationship_id,
            format=None):
        """
        Edit properties of a relationship
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        relationship = graph.relationships.get(relationship_id)

        new_data = dict()
        new_data['id'] = post_data.get('id', relationship.id)
        new_data['label'] = post_data.get('label', relationship.label)
        new_data['label_display'] = (
            post_data.get('label_display', relationship.label_display))
        new_data['properties'] = (
            post_data.get('properties', None))

        serializer = RelationshipSerializer(relationship, data=new_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, graph_slug, type_slug, relationship_id,
               format=None):
        """
        Delete the relationship with id equals to relationship_id
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationship = graph.relationships.get(relationship_id)
        serializer = RelationshipSerializer(relationship)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
