# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from graphs.models import Graph
from graphs.permissions import IsOwner
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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Returns all the nodetypes of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetypes = graph.schema.nodetype_set.all()

        serializer = NodeTypesSerializer(nodetypes, many=True)

        return Response(serializer.data)

    def post(self, request, graph_slug, format=None):
        """
        Create a new node type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, format=None):
        """
        Returns all the relationship types of a graph
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptypes = graph.schema.relationshiptype_set.all()

        serializer = RelationshipTypesSerializer(relationshiptypes, many=True)

        return Response(serializer.data)

    def post(self, request, graph_slug, format=None):
        """
        Create a new relationship type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns info related to the node type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns info related to the relationship type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the schema info of the node type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSchemaSerializer(nodetype)

        return Response(serializer.data)

    def patch(self, request, graph_slug, type_slug, format=None):
        """
        Change all fields at once. Omitted ones are not modified.
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the schema info of the relationship type
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        serializer = RelationshipTypeSchemaSerializer(relationshiptype)

        return Response(serializer.data)


class NodeTypeSchemaPropertiesView(APIView):
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the node type properties
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

        return Response(serializer.data)

    def post(self, request, graph_slug, type_slug, format=None):
        """
        Create a new property
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data
        # We need to get all the fields to create the property

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)

        try:
            post_data['node'] = nodetype
            nodeproperty = NodeProperty.objects.create(**post_data)
            nodeproperty.save()

            serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # We create our json response
            error = dict()
            error['detail'] = e.message
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, graph_slug, type_slug, format=None):
        """
        Modify an existing property. Omitted ones are removed.
        We need to check migration options.
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)
        # We check the flag for migrations
        migration_flag = post_data.get('migration', None)

        # We are going to store the ids treated
        properties_ids = list()

        if migration_flag is not None:
            try:
                # We iterate over the properties, to modify them
                properties = post_data['properties']
                for prop in properties:
                    prop_id = prop['id']
                    prop_id = int(prop_id)
                    properties_ids.append(prop_id)

                    # We filter to get the property
                    temp_prop = nodetype.properties.filter(id=prop_id)[0]
                    old_key = temp_prop.key
                    new_key = prop['key']

                    if temp_prop:
                        # We change the fields of the property
                        temp_prop.key = prop.get('key', temp_prop.key)
                        prop_type = prop.get('prop_type',
                                             temp_prop.get_datatype_display())
                        prop_type_code = (
                            temp_prop.get_datatype_dict()[prop_type])
                        temp_prop.datatype = prop_type_code
                        # temp_prop.choices = prop.get('choices',
                        #                              temp_prop.choices)
                        temp_prop.save()

                        # Here, we need to check the flag and treat
                        # the migrations
                        if migration_flag == "rename":
                            elements = nodetype.all()
                            for element in elements:
                                try:
                                    element.set(new_key, element.get(old_key))
                                    element.delete(old_key)
                                except KeyError:
                                    pass
                        elif migration_flag == "delete":
                            elements = nodetype.all()
                            for element in elements:
                                try:
                                    element.delete(old_key)
                                except KeyError:
                                    pass

                serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

                # Finally, we need to remove the properties that we have not
                # treated
                nodetype.properties.exclude(pk__in=properties_ids).delete()

                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                # We create our json response
                error = dict()
                error['detail'] = e.message
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            # We create our json response
            error = dict()
            error['detail'] = _("You need to add a migration option. "
                                "See the documentation for more information")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, graph_slug, type_slug, format=None):
        """
        Modify an existing property. Omitted ones remain.
        We need to check migration options.
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        post_data = request.data

        nodetype = get_object_or_404(NodeType,
                                     slug=type_slug,
                                     schema__graph__slug=graph_slug)
        # We check the flag for migrations
        migration_flag = post_data.get('migration', None)

        if migration_flag is not None:
            try:
                # We iterate over the properties, to modify them
                properties = post_data['properties']

                for prop in properties:
                    prop_id = prop['id']
                    # We filter to get the property
                    temp_prop = nodetype.properties.filter(id=int(prop_id))[0]
                    old_key = temp_prop.key
                    new_key = prop['key']

                    if temp_prop:
                        # We change the fields of the property
                        temp_prop.key = prop.get('key', temp_prop.key)
                        prop_type = prop.get('prop_type',
                                             temp_prop.get_datatype_display())
                        prop_type_code = (
                            temp_prop.get_datatype_dict()[prop_type])
                        temp_prop.datatype = prop_type_code
                        # temp_prop.choices = prop.get('choices',
                        #                              temp_prop.choices)

                        temp_prop.save()

                        # Here, we need to check the flag and treat
                        # the migrations
                        if migration_flag == "rename":
                            elements = nodetype.all()
                            for element in elements:
                                try:
                                    element.set(new_key, element.get(old_key))
                                    element.delete(old_key)
                                except KeyError:
                                    pass
                        elif migration_flag == "delete":
                            elements = nodetype.all()
                            for element in elements:
                                try:
                                    element.delete(old_key)
                                except KeyError:
                                    pass

                serializer = NodeTypeSchemaPropertiesSerializer(nodetype)

                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                # We create our json response
                error = dict()
                error['detail'] = e.message
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            # We create our json response
            error = dict()
            error['detail'] = _("You need to add a migration option. "
                                "See the documentation for more information")
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, graph_slug, type_slug, format=None):
        """
        Delete all the node type properties
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
    permission_classes = (IsOwner,)

    def get(self, request, graph_slug, type_slug, format=None):
        """
        Returns the relationship type properties
        """
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

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
        graph = get_object_or_404(Graph, slug=graph_slug)
        self.check_object_permissions(self.request, graph)

        relationshiptype = get_object_or_404(RelationshipType,
                                             slug=type_slug,
                                             schema__graph__slug=graph_slug)

        relationshiptype.properties.all().delete()

        # Migrations must be passed in
        # We can pass an argument to remove all of them or only the properties

        return Response(status=status.HTTP_204_NO_CONTENT)
