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
        new_properties = {'p2': 'b2', 'p3': 'v3'}
        g.update_node_properties(node_id, new_properties)
        self.assertIn('p1', g.get_node_properties(node_id))
        self.assertIn('p2', g.get_node_properties(node_id))
        self.assertIn('p3', g.get_node_properties(node_id))
        self.assertEqual(g.get_node_property(node_id, 'p2'), 'b2')
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
        g.set_relationship_property(relationship_id, 'p1', 'v1')
        self.assertEqual(g.get_relationship_source(relationship_id),
                {node1_id: None})
        self.assertEqual(g.get_relationship_target(relationship_id),
                {node2_id: None})
        self.assertEqual(g.get_node_relationships(node1_id),
                {relationship_id: None})
        self.assertEqual(g.get_node_relationships(node1_id, 
                                                include_properties=True),
                        {relationship_id: {'p1': 'v1'}})
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
        properties = {'p1': 'v1', 'p2': 'v2'}
        g.set_relationship_properties(r_id, properties)
        self.assertEqual(properties, g.get_relationship_properties(r_id))
        new_properties = {'p2': 'b2', 'p3': 'v3'}
        g.update_relationship_properties(r_id, new_properties)
        self.assertIn('p1', g.get_relationship_properties(r_id))
        self.assertIn('p2', g.get_relationship_properties(r_id))
        self.assertIn('p3', g.get_relationship_properties(r_id))
        self.assertEqual(g.get_relationship_property(r_id, 'p2'), 'b2')
        g.delete_relationship(r_id)
        g.delete_nodes([node1_id, node2_id])

    def testGetNodeProperties(self):
        g = GraphDatabase(self.NEO4J_TEST_HOST)
        node1_id = g.create_node("1")
        node2_id = g.create_node("2")
        node3_id = g.create_node("3")
        node4_id = g.create_node("4")
        node5_id = g.create_node("5")
        properties = {'p1': 'v1'}
        g.set_node_properties(node1_id, properties)
        g.set_node_properties(node2_id, properties)
        g.set_node_properties(node3_id, properties)
        g.set_node_properties(node4_id, properties)
        g.set_node_properties(node5_id, properties)
        node_ids = [node1_id, node2_id, node3_id, node4_id, node5_id]
        result = g.get_nodes_properties(node_ids)
        node_structure = {}
        node_structure = node_structure.fromkeys(node_ids, properties)
        self.assertEqual(result, node_structure)
        g.delete_nodes(node_ids) 
