#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from data.models import Data
from graphs.models import Graph, User


class GraphTest(TestCase):

    def setUp(self):
        d = Data.objects.create()
        u = User.objects.create()
        self.graph = Graph.objects.create(name="Test", owner=u, data=d)

    def test_nodes_create(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label="test node")
        self.assertIsNotNone(n)
        self.assertEqual(n.label, "test node")

    def test_nodes_create_unicode(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=u"test/ñôde")
        self.assertIsNotNone(n)
        self.assertEqual(n.label, u"test/ñôde")

    def test_relationships_create(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label="test node 1")
        n2 = self.graph.nodes.create(label="test node 2")
        r = self.graph.relationships.create(n1, n2, "test relation")
        self.assertIsNotNone(r)
        self.assertEqual(r.label, "test relation")

    def test_relationships_create_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label="test node 1")
        n2 = self.graph.nodes.create(label="test node 2")
        r = self.graph.relationships.create(n1, n2, u"test rêlatíoñ")
        self.assertIsNotNone(r)
        self.assertEqual(r.label, u"test rêlatíoñ")

