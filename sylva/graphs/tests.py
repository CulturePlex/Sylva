#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from accounts.models import Account, UserProfile
from data.models import Data
from graphs.models import Graph, User
from graphs.mixins import (NodesLimitReachedException,
                           RelationshipsLimitReachedException)


class GraphTest(TestCase):

    def setUp(self):
        u = User.objects.create()
        self.graph = Graph.objects.create(name="Test", owner=u)
        self.label = "Test label"
        self.properties = {"property": "value with spaces"}
        self.unicode_label = u"T€/śŧ łá¶ël+-"
        self.unicode_properties = {u"p röp/€rtŷ": u"uní©od e/välúê"}

    def test_nodes_create(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)

    def test_nodes_create_unicode(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.unicode_label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)

    def test_relationships_create(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r = self.graph.relationships.create(n1, n2, self.label)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.label)

    def test_relationships_create_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r = self.graph.relationships.create(n1, n2, self.unicode_label)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.unicode_label)

    def test_node_relationships_create(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r = n1.relationships.create(n2, self.label)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.label)

    def test_node_relationships_create_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r = n1.relationships.create(n2, self.unicode_label)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.unicode_label)

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

    def test_relationships_create_properties(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r = self.graph.relationships.create(n1, n2, self.label,
                                            properties=self.properties)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.label)
        for key, value in self.properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.properties)
            self.assertEqual(self.properties[key], value)

    def test_relationships_set_properties(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r = self.graph.relationships.create(n1, n2, self.label)
        self.assertIsNotNone(r)
        r.properties = self.properties
        self.assertEqual(r.label, self.label)
        self.assertEqual(r.properties, self.properties)
        for key, value in self.properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.properties)
            self.assertEqual(self.properties[key], value)

    def test_relationships_create_properties_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r = self.graph.relationships.create(n1, n2, self.unicode_label,
                                            properties=self.unicode_properties)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.unicode_label)
        for key, value in self.unicode_properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.unicode_properties)
            self.assertEqual(self.unicode_properties[key], value)

    def test_relationships_set_properties_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r = self.graph.relationships.create(n1, n2, self.unicode_label)
        self.assertIsNotNone(r)
        r.properties = self.unicode_properties
        self.assertEqual(r.label, self.unicode_label)
        self.assertEqual(r.properties, self.unicode_properties)
        for key, value in self.unicode_properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.unicode_properties)
            self.assertEqual(self.unicode_properties[key], value)

    def test_node_relationships_create_properties(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r = n1.relationships.create(n2, self.label, properties=self.properties)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.label)
        for key, value in self.properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.properties)
            self.assertEqual(self.properties[key], value)

    def test_node_relationships_create_properties_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r = n1.relationships.create(n2, self.unicode_label,
                                    properties=self.unicode_properties)
        self.assertIsNotNone(r)
        self.assertEqual(r.label, self.unicode_label)
        for key, value in self.unicode_properties.items():
            self.assertIn(key, r)
            self.assertEqual(r[key], value)
        for key, value in r.properties.iteritems():
            self.assertIn(key, self.unicode_properties)
            self.assertEqual(self.unicode_properties[key], value)

    def test_nodes_set_delete_property(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n[self.label] = self.label
        self.assertIn(self.label, n)
        self.assertEqual(n[self.label], self.label)
        del n[self.label]
        self.assertNotIn(self.label, n)

    def test_nodes_set_delete_property_unicode(self):
        """
        Tests node creation
        """
        n = self.graph.nodes.create(label=self.unicode_label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)
        n[self.unicode_label] = self.unicode_label
        self.assertIn(self.unicode_label, n)
        self.assertEqual(n[self.unicode_label], self.unicode_label)
        del n[self.unicode_label]
        self.assertNotIn(self.unicode_label, n)

    def test_node_get_relationships(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.label)
        n2 = self.graph.nodes.create(label=self.label)
        r1 = n1.relationships.create(n2, self.label,
                                    properties=self.properties)
        r1_id = r1.id
        r2 = n2.relationships.create(n1, self.label,
                                    properties=self.properties)
        r2_id = r2.id
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        self.assertEqual(r1.label, self.label)
        self.assertEqual(r2.label, self.label)
        self.assertEqual(len(n1.relationships.all()), 2)
        self.assertEqual(len(n1.relationships.incoming()), 1)
        self.assertEqual(len(n1.relationships.outgoing()), 1)
        self.assertEqual(len(n2.relationships.all()), 2)
        self.assertEqual(len(n2.relationships.incoming()), 1)
        self.assertEqual(len(n2.relationships.outgoing()), 1)
        self.assertEqual(n1.relationships.incoming()[0].properties,
                         self.properties)
        self.assertEqual(n2.relationships.incoming()[0].properties,
                         self.properties)
        self.assertEqual(n1.relationships.outgoing()[0].properties,
                         self.properties)
        self.assertEqual(n2.relationships.outgoing()[0].properties,
                         self.properties)
        self.assertEqual(self.graph.relationships.get(r1_id), r1)
        self.assertEqual(self.graph.relationships.get(r2_id), r2)

    def test_node_get_relationships_unicode(self):
        """
        Tests relation creation
        """
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r1 = n1.relationships.create(n2, self.unicode_label,
                                    properties=self.unicode_properties)
        r1_id = r1.id
        r2 = n2.relationships.create(n1, self.unicode_label,
                                    properties=self.unicode_properties)
        r2_id = r2.id
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        self.assertEqual(r1.label, self.unicode_label)
        self.assertEqual(r2.label, self.unicode_label)
        self.assertEqual(len(n1.relationships.all()), 2)
        self.assertEqual(len(n1.relationships.incoming()), 1)
        self.assertEqual(len(n1.relationships.outgoing()), 1)
        self.assertEqual(len(n2.relationships.all()), 2)
        self.assertEqual(len(n2.relationships.incoming()), 1)
        self.assertEqual(len(n2.relationships.outgoing()), 1)
        self.assertEqual(n1.relationships.incoming()[0].properties,
                         self.unicode_properties)
        self.assertEqual(n2.relationships.incoming()[0].properties,
                         self.unicode_properties)
        self.assertEqual(n1.relationships.outgoing()[0].properties,
                         self.unicode_properties)
        self.assertEqual(n2.relationships.outgoing()[0].properties,
                         self.unicode_properties)
        self.assertEqual(self.graph.relationships.get(r1_id), r1)
        self.assertEqual(self.graph.relationships.get(r2_id), r2)

    def test_nodes_account_limit(self):
        account = self.graph.owner.get_profile().account
        n1 = self.graph.nodes.create(label=self.unicode_label)
        nodes_limit = account.nodes
        account.nodes = 1
        account.save()
        self.assertRaises(NodesLimitReachedException, self.graph.nodes.create,
                          label=self.unicode_label)
        account.nodes = nodes_limit
        account.save()
        n2 = self.graph.nodes.create(label=self.unicode_label)

    def test_relationships_account_limit(self):
        account = self.graph.owner.get_profile().account
        n1 = self.graph.nodes.create(label=self.unicode_label)
        n2 = self.graph.nodes.create(label=self.unicode_label)
        r1 = n1.relationships.create(n2, label=self.unicode_label)
        relationships_limit = account.relationships
        account.relationships = 1
        account.save()
        self.assertRaises(RelationshipsLimitReachedException,
                          self.graph.relationships.create,
                          n2, n1, label=self.unicode_label)
        account.relationships = relationships_limit
        account.save()
        n2 = self.graph.relationships.create(n2, n1, label=self.unicode_label)
