# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import get_object_or_404

from graphs.models import Graph
from data.forms import NodeForm
from data.serializers import (GetNodesSerializer, GetRelationshipsSerializer,)
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
