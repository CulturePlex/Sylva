#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from graphs.models import Graph
from graphs.mixins import RelationshipDoesNotExist
from schemas.models import Schema, NodeType, RelationshipType


class RelationshipTest(TestCase):
    """
    A set of tests for testing Relationship.
    """

    def setUp(self):
        """
        Sets up a few attributes and and objects for the tests we'll run.
        """
        self.node_1_label = '1'
        self.node_2_label = '2'
        self.relationship_label = '3'
        self.new_relationship_label = '19'
        self.property_key = 'location'
        self.property_value = "Bob's house"
        user = User.objects.create(
            username='bob',
            password='bob_secret',
            email='bob@cultureplex.ca')
        schema = Schema.objects.create()
        NodeType.objects.create(
            id=self.node_1_label, name="Bob's node type 1", schema=schema)
        NodeType.objects.create(
            id=self.node_2_label, name="Bob's node type 2", schema=schema)
        RelationshipType.objects.create(
            id=self.relationship_label, name="Bob's relationship type",
            schema=schema)
        self.graph = Graph.objects.create(
            name="Bob's graph", schema=schema, owner=user)
        node_1 = self.graph.nodes.create(label=self.node_1_label)
        node_2 = self.graph.nodes.create(label=self.node_2_label)
        self.relationship = self.graph.relationships.create(
            node_1, node_2, self.relationship_label)
        self.relationship_id = self.relationship.id

    def test_relationship_creation(self):
        """
        Tets Relationship creation from the setUp() method.
        """
        self.assertIsNotNone(self.relationship)
        self.assertIsNotNone(self.relationship.id)
        self.assertEqual(self.relationship.label, self.relationship_label)

    def test_relationship_edition(self):
        """
        Test Relationship edition from the created one.
        """
        self.relationship.set(self.property_key, self.property_value)
        self.assertEqual(self.relationship.get(
            self.property_key), self.property_value)

    def test_relationship_deletion(self):
        """
        Test Relationship deletion from the edition one.
        """
        self.graph.relationships.delete(label=self.relationship_label)

        try:
            self.graph.relationships._get(self.relationship_id)
            exist = True
        except RelationshipDoesNotExist:
            exist = False

        self.assertEqual(exist, False)
