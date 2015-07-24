# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from graphs.models import Graph
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
        """
        pass


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
        """
        pass
