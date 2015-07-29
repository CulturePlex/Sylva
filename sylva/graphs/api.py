# -*- coding: utf-8 -*-
from accounts.models import User
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
        # We use the username to filter the graphs of the user
        username = request.user.username
        user = User.objects.filter(username=username)[0]
        graphs = user.graphs.all()

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

    def patch(self, request, graph_slug, format=None):
        """
        Edit an existing graph. Only fields provided will be modified
        """
        # We get the data from the request
        post_data = request.data
        post_data['name'] = request.data.get('name', None)

        graph = get_object_or_404(Graph, slug=graph_slug)
        post_data['owner'] = graph.owner.pk

        if post_data['name'] is None:
            post_data['name'] = graph.name

        serializer = GraphSerializer(graph, data=post_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, graph_slug, format=None):
        """
        Edit an existing graph. Omitted fields are removed.
        """
        # We get the data from the request
        post_data = request.data
        post_data['name'] = request.data.get('name', None)

        graph = get_object_or_404(Graph, slug=graph_slug)
        post_data['owner'] = graph.owner.pk

        if post_data['name'] is None:
            post_data['name'] = graph.name

        # We get the serializer of the graph to get the fields
        serializer = GraphSerializer(graph)
        fields = serializer.fields.keys()

        # We need to omit the fields that are not included
        # We need to take into account the fields restrictions
        new_data = dict()
        for field in fields:
            if field == 'public':
                new_data[field] = graph.public
            else:
                new_data[field] = post_data.get(field, None)

        # And now we update the instance
        serializer = GraphSerializer(graph, data=new_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, graph_slug, format=None):
        """
        Delete an existing graph.
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        serializer = GraphSerializer(graph)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
