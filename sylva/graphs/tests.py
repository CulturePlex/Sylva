#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from graphs.models import Graph, User
from schemas.models import Schema, NodeType


class GraphTest(TestCase):
    def setUp(self):
        # If label is not a number, it fires an exception
        self.label = "1"
        self.unicode_label = u"1"
        self.graphName = "graphTest"
        u = User.objects.create()
        mySchema = Schema.objects.create()
        nt = NodeType(id=1, name="test", schema=mySchema)
        nt.save()
        self.graph = Graph.objects.create(name=self.graphName,
            schema=mySchema, owner=u)

    def test_graph_creation(self):
        """
        Tests that a graph is created.
        """
        self.assertIsNotNone(self.graph)
        self.assertEqual(self.graph.name, self.graphName)

    def test_graph_deletion(self):
        """
        Tests that a graph is created.
        """
        elem = self.graph
        self.assertIsNotNone(elem)
        elem = self.graph.delete()
        self.assertIsNone(elem)

    def test_nodes_create(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)

    def test_nodes_create_unicode(self):
        """
        Tests node creation with unicode label
        """
        n = self.graph.nodes.create(label=self.unicode_label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)

    def test_nodes_edition(self):
        """
        Tests node edition
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n._label = "2"
        self.assertNotEqual(n.label, self.label)

    def test_nodes_edition_unicode(self):
        """
        Tests node edition with unicode label
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n._label= u"2"
        self.assertNotEqual(n.label, self.label)

    def test_nodes_deletion(self):
        """
        Tests node deletion
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        elem = self.graph.nodes.delete(label=self.label)
        self.assertIsNone(elem)


