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
    schema_info = serializers.SerializerMethodField('schema_func')
    rels_info = serializers.SerializerMethodField('rels_func')

    def schema_func(self, relationshiptype):
        # We get the graph
        graph = relationshiptype.schema.graph
        graph_name = graph.name

        # We get the schema id
        schema_id = relationshiptype.schema_id

        # We create our info for the schema
        result = dict()
        result['name'] = "Schema for {0}".format(graph_name)
        result['id'] = schema_id

        return result

    def nodes_func(self, relationshiptype):
        # We get the relationships of the graph
        # We need to filter by this relationshiptype
        filtered_relationships = (
            relationshiptype.schema.graph.nodes.filter(
                label=relationshiptype.id))

        relationships = list()

        for relationship in filtered_relationships:
            relationships.append(relationship.properties)

        # We are ready to return the result
        return relationship

    class Meta:
        model = RelationshipType
        fields = ('name', 'slug', 'description', 'schema_info', 'rels_info')
