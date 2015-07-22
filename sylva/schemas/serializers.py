from schemas.models import NodeType, RelationshipType
from rest_framework import serializers


class NodeTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeType
        fields = ('name', 'slug', 'description', 'schema')


class RelationshipTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipType
        fields = ('name', 'slug', 'description', 'schema')


class NodeTypeSerializer(serializers.ModelSerializer):
    schema_info = serializers.SerializerMethodField('schema_func')
    nodes_info = serializers.SerializerMethodField('nodes_func')

    def schema_func(self, nodetype):
        # We get the graph
        graph = nodetype.schema.graph
        graph_name = graph.name

        # We get the schema id
        schema_id = nodetype.schema_id

        # We create our info for the schema
        result = dict()
        result['name'] = "Schema for {0}".format(graph_name)
        result['id'] = schema_id

        return result

    def nodes_func(self, nodetype):
        # We get the nodes of the graph
        # We need to filter by this nodetype
        filtered_nodes = (
            nodetype.schema.graph.nodes.filter(label=nodetype.id))

        nodes = list()

        for node in filtered_nodes:
            nodes.append(node.properties)

        # We are ready to return the result
        return nodes

    class Meta:
        model = NodeType
        fields = ('name', 'slug', 'description', 'schema_info', 'nodes_info')


class RelationshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipType
        fields = ('name', 'slug', 'description', 'schema')
