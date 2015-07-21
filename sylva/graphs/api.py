# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from graphs.models import Graph
from graphs.serializers import GraphsSerializer, GraphSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class GraphsView(APIView):

    def get(self, request, format=None):
        """
        Returns all the graph that owns to the user
        """
        graphs = Graph.objects.all()
        serializer = GraphsSerializer(graphs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Create a new graph
        """
        # We get the data from the request
        post_data = request.data
        # We add the user that executes the request as owner
        post_data['owner'] = request.user.pk

        serializer = GraphsSerializer(data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GraphView(APIView):

    def get(self, request, graph_slug, format=None):
        """
        Returns the information of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        serializer = GraphSerializer(graph)
        return Response(serializer.data)
