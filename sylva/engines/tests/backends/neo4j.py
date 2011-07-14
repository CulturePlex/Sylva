#!/usr/bin/env python
#-*- coding:utf8 -*-


from django.test import TestCase
from engines.gdb.backends import NodeDoesNotExist, RelationshipDoesNotExist
from engines.gdb.backends.neo4j import GraphDatabase


class Neo4jEngineTestSuite(TestCase):

    NEO4J_TEST_HOST = 'http://localhost:7474/db/data'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInvalidUrl(self):
        self.assertRaises(Exception,
                            GraphDatabase,
                            'http://invalidurl')

    def testValidUrl(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        self.assertIsInstance(g, GraphDatabase)

    def testCreateDeleteNode(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        node_id = g.create_node("myNode")
        self.assertEqual(g.get_node_label(node_id), "myNode")
        g.set_node_label(node_id, "yourNode")
        self.assertEqual(g.get_node_label(node_id), "yourNode")
        g.delete_node(node_id)
        self.assertRaises(NodeDoesNotExist, g.get_node_label, node_id)

    def testNodeProperties(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        node_id = g.create_node("myNode")
        self.assertEqual(g.get_node_label(node_id), "myNode")
        g.set_node_property(node_id, "myProp", "myValue")
        self.assertEqual(g.get_node_property(node_id, "myProp"), "myValue")
        self.assertIn("myProp", g.get_node_properties(node_id))
        g.delete_node_property(node_id, "myProp")
        self.assertNotIn("myProp", g.get_node_properties(node_id))
        properties = {'p1': 'v1', 'p2': 'v2'}
        g.set_node_properties(node_id, properties)
        self.assertEqual(properties, g.get_node_properties(node_id))
        g.delete_node_properties(node_id)
        self.assertEqual({}, g.get_node_properties(node_id))
        g.delete_node(node_id)
        self.assertRaises(NodeDoesNotExist, g.get_node_label, node_id)

    def testNodesAndRelationships(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        node1_id = g.create_node("1")
        node2_id = g.create_node("2")
        relationship_id = g.create_relationship(node1_id,
                                                node2_id,
                                                "myLabel")
        self.assertEqual(g.get_relationship_source(relationship_id),
                            node1_id)
        self.assertEqual(g.get_relationship_target(relationship_id),
                            node2_id)
        g.delete_relationship(relationship_id)
        g.delete_nodes([node1_id, node2_id])

    def testRelationshipProperties(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        node1_id = g.create_node("1")
        node2_id = g.create_node("2")
        r_id = g.create_relationship(node1_id,
                                                node2_id,
                                                "myLabel")
        self.assertEqual(g.get_relationship_label(r_id),
                            "myLabel")
        g.set_relationship_property(r_id, "myProp", "myValue")
        self.assertIn("myProp", g.get_relationship_properties(r_id))
        self.assertEqual(g.get_relationship_property(r_id, "myProp"),
                            "myValue")
        g.delete_relationship_property(r_id, "myProp")
        self.assertNotIn("myProp", g.get_relationship_properties(r_id))
        g.delete_relationship(r_id)
        g.delete_nodes([node1_id, node2_id])
