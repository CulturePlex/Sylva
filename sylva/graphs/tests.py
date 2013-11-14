#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from graphs.models import Graph, User
from schemas.models import Schema, NodeType
from graphs.mixins import NodeDoesNotExist


class GraphTest(TestCase):
    def setUp(self):
        # If label is not a number, it fires an exception
        self.label = "1"
        self.properties = {"property": "value with spaces"}
        self.unicode_label = u"1"
        self.unicode_properties = {u"property": u"value with spaces"}
        self.graphName = "graphTest"
        self.u = User.objects.create()
        mySchema = Schema.objects.create()
        nt = NodeType(id=1, name="test", schema=mySchema)
        nt.save()
        self.graph = Graph.objects.create(name=self.graphName,
            schema=mySchema, owner=self.u)

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
        graph_id = self.graph.id
        self.graph.delete()
        try:
            Graph.objects.get(pk=graph_id)
            exists = True
        except Graph.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)

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
        n_id = n._id
        self.graph.nodes.delete(label=self.label)
        try:
            self.graph.nodes._get(n_id)
            exists = True
        except NodeDoesNotExist:
            exists = False
        self.assertEqual(exists, False)

    def test_nodes_create_properties(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.label,
                                    properties=self.properties)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        self.assertEqual(n.properties, self.properties)
        for key, value in self.properties.items():
            self.assertIn(key, n)
            self.assertEqual(n[key], value)
        for key, value in n.properties.iteritems():
            self.assertIn(key, self.properties)
            self.assertEqual(self.properties[key], value)

    def test_nodes_set_properties(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n.properties = self.properties
        self.assertEqual(n.properties, self.properties)
        for key, value in self.properties.items():
            self.assertIn(key, n)
            self.assertEqual(n[key], value)
        for key, value in n.properties.iteritems():
            self.assertIn(key, self.properties)
            self.assertEqual(self.properties[key], value)

    def test_nodes_create_properties_unicode(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.unicode_label,
                                    properties=self.unicode_properties)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)
        self.assertEqual(n.properties, self.unicode_properties)
        for key, value in self.unicode_properties.items():
            self.assertIn(key, n)
            self.assertEqual(n[key], value)
        for key, value in n.properties.iteritems():
            self.assertIn(key, self.unicode_properties)
            self.assertEqual(self.unicode_properties[key], value)

    def test_nodes_set_properties_unicode(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.unicode_label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)
        n.properties = self.unicode_properties
        self.assertEqual(n.properties, self.unicode_properties)
        for key, value in self.unicode_properties.items():
            self.assertIn(key, n)
            self.assertEqual(n[key], value)
        for key, value in n.properties.iteritems():
            self.assertIn(key, self.unicode_properties)
            self.assertEqual(self.unicode_properties[key], value)

    def test_graph_clone(self):
        """
        Tests graph clonation
        """
        cloneGraphName = "graphCloneTest"
        mySchema_clone = Schema.objects.create()
        nt = NodeType(id=2, name="test", schema=mySchema_clone)
        nt.save()
        clone_graph = Graph.objects.create(name=cloneGraphName,
            schema=mySchema_clone, owner=self.u)
        self.assertIsNotNone(clone_graph)
        self.assertNotEqual(self.graph.name, clone_graph.name)
        self.graph.clone(clone_graph, clone_data=True)
        self.assertNotEqual(self.graph, clone_graph)
        self.assertEqual(self.graph.nodes.count(), clone_graph.nodes.count())
