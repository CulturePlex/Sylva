# -*- coding: utf-8 -*-
from datetime import datetime

from accounts.models import User
from django.shortcuts import get_object_or_404
from graphs.models import Graph
from graphs.permissions import IsOwner
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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Returns the information of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        serializer = GraphSerializer(graph)

        return Response(serializer.data)

    def patch(self, request, graph_slug, format=None):
        """
        Edit an existing graph. Only fields provided will be modified
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        # We get the data from the request
        post_data = request.data
        post_data['name'] = request.data.get('name', None)

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
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        # We get the data from the request
        post_data = request.data
        post_data['name'] = request.data.get('name', None)

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
        self.check_object_permissions(self.request, graph)

        serializer = GraphSerializer(graph)

        serializer.instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# Export classes

class GraphCompleteExportView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Export the schema and the data of the graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        schema = graph.schema.export()
        data = dict(nodes=[{'id': n.id,
                            'label': n.display,
                            'type': n.label_display,
                            'properties': n.properties}
                           for n in graph.nodes.all()],
                    edges=[{'id': e.id,
                            'label': e.display,
                            'type': e.label_display,
                            'properties': e.properties}
                           for e in graph.relationships.all()])
        schema.update(data)

        return Response(schema)


class GraphSchemaExportView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Export the schema of the graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        return Response(graph.schema.export())


class GraphDataExportView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Export the data of the graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        data = dict(nodes=[{'id': n.id,
                            'type': n.label_display,
                            'type_id': n.label,
                            'properties': n.properties}
                           for n in graph.nodes.all()],
                    edges=[{'id': e.id,
                            'type': e.label_display,
                            'type_id': e.label,
                            'source_id': e.source.id,
                            'target_id': e.target.id,
                            'properties': e.properties}
                           for e in graph.relationships.all()])

        return Response(data)


# Import classes

class GraphCompleteImportView(APIView):
    permission_classes = (IsOwner,)

    def put(self, request, graph_slug, format=None):
        """
        Import the schema and the data of the graph
        """
        pass


class GraphSchemaImportView(APIView):
    permission_classes = (IsOwner,)

    def put(self, request, graph_slug, format=None):
        """
        Import the schema of the graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        data = request.data

        graph.schema._import(data)

        return Response(data,
                        status=status.HTTP_201_CREATED)


class GraphDataImportView(APIView):
    permission_classes = (IsOwner,)

    def put(self, request, graph_slug, format=None):
        """
        Import the data of the graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        data = request.data

        # Nodes
        nodes = data['nodes']
        ids_dict = {}
        for elem in nodes:
            elem_id = elem['id']
            label = graph.schema.nodetype_set.get(name=elem['type'])
            properties = elem.get('properties', '{}')
            node = graph.nodes.create(str(label.id), properties)
            ids_dict[elem_id] = node.id

        # Relationships
        relationships = data['edges']
        for elem in relationships:
            source = graph.nodes.get(elem["source_id"])
            target = graph.nodes.get(elem["target_id"])

            label = elem["type"]
            label_id = elem["type_id"]
            properties = elem.get("properties", "{}")

            graph.relationships.create(source, target, label_id,
                                       properties)
        graph.last_modified = datetime.now()
        graph.data.save()

        return Response(data,
                        status=status.HTTP_201_CREATED)
