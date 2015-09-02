# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from graphs.models import Graph
from schemas.models import (NodeType, RelationshipType,
                            NodeProperty, RelationshipProperty)
from schemas.serializers import (NodeTypesSerializer,
                                 RelationshipTypesSerializer,
                                 NodeTypeSerializer,
                                 RelationshipTypeSerializer,
                                 NodeTypeSchemaSerializer,
                                 RelationshipTypeSchemaSerializer,
                                 NodeTypeSchemaPropertiesSerializer,
                                 RelationshipTypeSchemaPropertiesSerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class NodeTypesView(APIView):

    def get(self, request, graph_slug, format=None):
        """
        Returns all the nodetypes of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        nodetypes = graph.schema.nodetype_set.all()

        serializer = NodeTypesSerializer(nodetypes, many=True)

        return Response(serializer.data)

    def post(self, request, graph_slug, format=None):
        """
        Create a new node type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        # We get the data from the request
        post_data = request.data
        # We get the schema id
        post_data['schema'] = graph.schema_id

        serializer = NodeTypesSerializer(data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationshipTypesView(APIView):

    def get(self, request, graph_slug, format=None):
        """
        Returns all the relationship types of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        relationshiptypes = graph.schema.relationshiptype_set.all()

        serializer = RelationshipTypesSerializer(relationshiptypes, many=True)

        return Response(serializer.data)

    def post(self, request, graph_slug, format=None):
        """
        Create a new relationship type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)

        # We get the data from the request
        post_data = request.data

        source_slug = post_data['source']
        target_slug = post_data['target']
        # We need the reference of the nodes
        source = get_object_or_404(NodeType,
                                   slug=source_slug,
                                   schema__graph__slug=graph_slug)
        target = get_object_or_404(NodeType,
                                   slug=target_slug,
                                   schema__graph__slug=graph_slug)

        # We get the schema id
        post_data['schema'] = graph.schema_id
        post_data['source'] = source.id
        post_data['target'] = target.id

        serializer = RelationshipTypesSerializer(data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeTypeView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns info related to the node type
        """
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSerializer(nodetype)

        return Response(serializer.data)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete the node type from the schema
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        # We need to remove all the related nodes and
        # relationships
        graph.nodes.delete(label=nodetype.id)

        serializer = NodeTypeSerializer(nodetype)
        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelationshipTypeView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns info related to the relationship type
        """
        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = RelationshipTypeSerializer(relationshiptype)

        return Response(serializer.data)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete the relationship type from the schema
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        # We need to remove all the related nodes and
        # relationships
        graph.relationships.delete(label=relationshiptype.id)

        serializer = RelationshipTypeSerializer(relationshiptype)
        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class NodeTypeSchemaView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the schema info of the node type
        """
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSchemaSerializer(nodetype)

        return Response(serializer.data)

    def patch(self, request, graph_slug, type_slug, format=None):
        """
        Change all fields at once. Omitted ones are not modified.
        """

        # We get the data from the request
        post_data = request.data

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSchemaSerializer(nodetype, data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, graph_slug, type_slug, format=None):
        """
        Change all fields at once. Omitted ones are removed
        """
        # We get the data from the request
        post_data = request.data

        post_data['name'] = request.data.get('name', "")
        post_data['description'] = request.data.get('description', "")

        # We get the serializer of the graph to get the fields
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)
        serializer = NodeTypeSchemaSerializer(nodetype)

        serializer = NodeTypeSchemaSerializer(nodetype, data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationshipTypeSchemaView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the schema info of the relationship type
        """
        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = RelationshipTypeSchemaSerializer(relationshiptype)

        return Response(serializer.data)


class NodeTypeSchemaPropertiesView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the node type properties
        """
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new property
        """
        post_data = request.data
        # We need to get all the fields to create the property

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        post_data['node'] = nodetype
        nodeproperty = NodeProperty.objects.create(**post_data.dict())
        nodeproperty.save()

        serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete all the node type properties
        """
        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        # We need to remove all the related nodes and
        # relationships
        nodetype.properties.all().delete()

        # Migrations must be passed in
        # We can pass an argument to remove all of them or only the properties

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelationshipTypeSchemaPropertiesView(APIView):

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the relationship type properties
        """
        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = RelationshipTypeSchemaPropertiesSerializer(
            relationshiptype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new property
        """
        post_data = request.data
        # We need to get all the fields to create the property

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)
        post_data['relationship'] = relationshiptype
        relationshipproperty = RelationshipProperty.objects.create(
            **post_data.dict())
        relationshipproperty.save()

        serializer = RelationshipTypeSchemaPropertiesSerializer(
            relationshiptype)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete all the relationship type properties
        """
        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        relationshiptype.properties.all().delete()

        # Migrations must be passed in
        # We can pass an argument to remove all of them or only the properties

        return Response(status=status.HTTP_204_NO_CONTENT)
