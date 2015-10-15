# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import get_object_or_404

# from engines.gdb.lookups.neo4j import Q
from graphs.models import Graph
from schemas.models import NodeType, RelationshipType
from data.forms import NodeForm
from data.permissions import DataAdd, DataChange, DataDelete, DataView
from data.serializers import (NodesSerializer, RelationshipsSerializer,
                              NodeSerializer, RelationshipSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics


class NodesViewFilter(generics.ListAPIView):
    permission_classes = (DataAdd, DataView,)
    serializer_class = NodeSerializer

    def get_queryset(self):
        queryset = NodeType.objects.all()
        type_slug = self.request.query_params.get('type_slug', None)
        property_type = self.request.query_params.get('property', None)
        property_value = self.request.query_params.get('value', None)

        nodes_queryset = queryset.filter(slug=type_slug)
        nt = nodes_queryset.first()

        # It would be interesting to filter the nodes by lookups
        # lookups = []
        # lookup = Q(property="Name", lookup="equals", match="Prueba1")
        # lookups.append(str(lookup))

        # nodes = nt.schema.graph.nodes.filter(lookups=lookups)
        result = []
        nodes = nt.schema.graph.nodes.all()
        for node in nodes:
            try:
                if node.properties[property_type] == property_value:
                    result.append(node)
            except KeyError:
                pass

        return result


class NodesView(APIView):
    permission_classes = (DataAdd, DataView,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of nodes that belongs to type_slug
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodesSerializer(nodetype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new node of a type for each element from data
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        # We get the post data
        data = request.data
        nodes_ids = []
        transaction_ok = True

        # We have in data a list of elements to create as new
        for node_data in data:
            node_form = NodeForm(graph=graph, itemtype=nodetype,
                                 data=node_data, user=request.user.username)

            if node_data and node_form.is_valid():
                with transaction.atomic():
                    new_node = node_form.save()
                    nodes_ids.append(new_node.id)
            else:
                transaction_ok = False
                break

        if transaction_ok:
            return Response(nodes_ids, status=status.HTTP_201_CREATED)
        else:
            return Response(node_form.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete a list of nodes by their ids
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        # We get the post data
        data = request.data
        nodes_ids = []

        # We have in data a list of elements to create as new
        for node_id in data:
            node = graph.nodes.get(node_id)
            serializer = NodeSerializer(node)

            try:
                serializer.instance.delete()
                nodes_ids.append(node_id)
            except:
                nodes_ids.append(None)

        return Response(nodes_ids, status=status.HTTP_204_NO_CONTENT)


class RelationshipsView(APIView):
    permission_classes = (DataAdd, DataView,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns a list of relationships that belongs to type_slug
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = RelationshipsSerializer(relationshiptype)

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
        rels_ids = []
        transaction_ok = True

        # We have in data a list of elements to create as new
        for rel_data in data:
            source_id = rel_data['source_id']
            target_id = rel_data['target_id']
            reltype_id = str(relationshiptype.id)

            try:
                if source_id and target_id:
                    # We create the relationship
                    rel = graph.relationships.create(source=source_id,
                                                     target=target_id,
                                                     label=reltype_id)
                    rels_ids.append(rel.id)
                else:
                    transaction_ok = False
                    break
            except Exception as e:
                error = dict()
                error['detail'] = e.message
                transaction_ok = False
                break

        if transaction_ok:
            return Response(rels_ids, status=status.HTTP_201_CREATED)
        else:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete a list of relationships by their ids
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        # We get the post data
        data = request.data
        rels_ids = []

        # We have in data a list of elements to create as new
        for relationship_id in data:
            relationship = graph.relationships.get(relationship_id)
            serializer = RelationshipSerializer(relationship)

            try:
                serializer.instance.delete()
                rels_ids.append(relationship_id)
            except:
                rels_ids.append(None)

        return Response(rels_ids, status=status.HTTP_204_NO_CONTENT)


class NodeView(APIView):
    permission_classes = (DataChange, DataDelete, DataView,)

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
    permission_classes = (DataChange, DataDelete, DataView,)

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
