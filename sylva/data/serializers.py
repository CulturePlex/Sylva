# -*- coding: utf-8 -*-
from rest_framework import serializers


class NodesSerializer(serializers.Serializer):
    total = serializers.SerializerMethodField('count_func')
    nodes = serializers.SerializerMethodField('nodes_func')

    def count_func(self, nodes):
        # Nodes is a list of NodeSequence
        return len(nodes)

    def nodes_func(self, nodes):
        result_nodes = [{'id': node.id, 'properties': node.properties}
                        for node in nodes]
        return result_nodes


class RelationshipsSerializer(serializers.Serializer):
    total = serializers.SerializerMethodField('count_func')
    relationships = serializers.SerializerMethodField('rels_func')

    def count_func(self, relationships):
        return len(relationships)

    def rels_func(self, relationships):
        result_relationships = []
        for relationship in relationships:
            relationship_dict = dict()

            relationship_dict['id'] = relationship.id
            relationship_dict['source'] = (
                relationship.source.properties)
            relationship_dict['target'] = (
                relationship.target.properties)
            relationship_dict['properties'] = (
                relationship.properties)

            result_relationships.append(relationship_dict)

        # We are ready to return the result
        return result_relationships


class NodeSerializer(serializers.Serializer):
    id = serializers.CharField()
    label = serializers.CharField()
    label_display = serializers.CharField()
    properties = serializers.DictField()
    # properties = serializers.SerializerMethodField('properties_func')

    def properties_func(self, node):
        return node.properties

    def update(self, instance, validated_data):
        properties = (
            validated_data.get('properties', instance.properties))

        instance.properties = properties

        return instance


class RelationshipSerializer(serializers.Serializer):
    id = serializers.CharField()
    label = serializers.CharField()
    label_display = serializers.CharField()
    properties = serializers.DictField()
    # properties = serializers.SerializerMethodField('properties_func')

    def properties_func(self, relationship):
        return relationship.properties

    def update(self, instance, validated_data):
        properties = (
            validated_data.get('properties', instance.properties))

        instance.properties = properties

        return instance
