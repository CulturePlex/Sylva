from schemas.models import Schema, NodeType, RelationshipType
from rest_framework import serializers


class NodeTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeType
        fields = ('name', 'slug', 'description', 'schema')


class RelationshipTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipType
        fields = ('name', 'slug', 'source', 'target', 'description', 'schema')


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

    def rels_func(self, relationshiptype):
        # We get the relationships of the graph
        # We need to filter by this relationshiptype
        filtered_relationships = (
            relationshiptype.schema.graph.nodes.filter(
                label=relationshiptype.id))

        relationships = list()

        for relationship in filtered_relationships:
            relationships.append(relationship.properties)

        # We are ready to return the result
        return relationships

    class Meta:
        model = RelationshipType
        fields = ('name', 'slug', 'description', 'schema_info', 'rels_info')


class NodeTypeSchemaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True,
                                 max_length=150)
    description = serializers.CharField(required=False, allow_blank=True)
    total = serializers.IntegerField(read_only=True)
    relations = serializers.SerializerMethodField('relations_func')
    properties = serializers.SerializerMethodField('properties_func')

    def properties_func(self, nodetype):
        properties = list()

        # First, we are going to get the properties
        for node_property in nodetype.properties.all().select_related():
            prop = {
                "label": node_property.key,
                "type": node_property.get_datatype_value(),
                "id": node_property.id,
                "name": node_property.slug,
                "primary": False,
                "blank": False,
                "choices": node_property.get_choices(),
            }
            properties.append(prop)

        return properties

    def relations_func(self, nodetype):
        # If we want it, we can add the relations of the node type also
        relations = list()

        return relations

    def update(self, instance, validated_data):
        """
        Update and return an existing instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)

        instance.save()

        return instance


class RelationshipTypeSchemaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True,
                                 max_length=150)
    description = serializers.CharField(required=False, allow_blank=True)
    total = serializers.IntegerField(required=False, default=0)
    properties = serializers.SerializerMethodField('properties_func')

    def properties_func(self, relationshiptype):
        properties = list()

        # First, we are going to get the properties
        for rel_property in relationshiptype.properties.all().select_related():
            prop = {
                "label": rel_property.key,
                "type": rel_property.get_datatype_value(),
                "id": rel_property.id,
                "name": rel_property.slug,
                "primary": False,
                "blank": False,
                "choices": rel_property.get_choices(),
            }
            properties.append(prop)

        return properties

    def update(self, instance, validated_data):
        """
        Update and return an existing instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)

        instance.save()

        return instance


class NodeTypeSchemaPropertiesSerializer(serializers.ModelSerializer):
    properties_info = serializers.SerializerMethodField('properties_func')

    def properties_func(self, nodetype):
        properties = list()

        # First, we are going to get the properties
        for node_property in nodetype.properties.all().select_related():
                prop = {
                    "label": node_property.key,
                    "type": node_property.get_datatype_value(),
                    "id": node_property.id,
                    "name": node_property.slug,
                    "primary": False,
                    "blank": False,
                    "choices": node_property.get_choices(),
                }
                properties.append(prop)

        # We create our info for the properties
        properties = {
            "name": nodetype.name,
            "properties": properties,
            "id": nodetype.id
        }

        return properties

    class Meta:
        model = NodeType
        fields = ['properties_info']


class RelationshipTypeSchemaPropertiesSerializer(serializers.ModelSerializer):
    schema_info = serializers.SerializerMethodField('schema_func')

    def schema_func(self, relationshiptype):
        properties = list()

        # First, we are going to get the properties
        for rel_property in relationshiptype.properties.all().select_related():
                prop = {
                    "label": rel_property.key,
                    "type": rel_property.get_datatype_value(),
                    "id": rel_property.id,
                    "name": rel_property.slug,
                    "primary": False,
                    "blank": False,
                    "choices": rel_property.get_choices(),
                }
                properties.append(prop)

        # We create our info for the schema
        schema = {
            "name": relationshiptype.name,
            "properties": properties,
            "id": relationshiptype.id
        }

        return schema

    class Meta:
        model = Schema
        fields = ['schema_info']
