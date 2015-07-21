from graphs.models import Graph
from rest_framework import serializers


class GraphsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graph
        fields = ('name', 'slug', 'description', 'owner')


class GraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graph
        fields = ('name',
                  'description',
                  'public',
                  'order',
                  'data',
                  'schema',
                  'options',
                  'last_modified',
                  'owner')
