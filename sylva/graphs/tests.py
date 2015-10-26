# -*- coding:utf-8 -*-

from django.test import TestCase

from django.contrib.auth import authenticate
from django.test.client import Client, RequestFactory
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, APIRequestFactory

from graphs.models import Graph
from graphs.mixins import RelationshipDoesNotExist
from graphs.mixins import NodeDoesNotExist
from schemas.models import Schema, NodeType, RelationshipType

import tools.views


class GraphTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.c = Client()
        self.u = User.objects.create(username='john', password='doe',
                                     is_active=True, is_staff=True)
        self.u.set_password('hello')
        self.u.save()
        mySchema = Schema.objects.create()
        nt = NodeType(id=1, name="test", schema=mySchema)
        nt.save()
        # If label is not a number, it fires an exception
        self.label = "1"
        self.properties = {"property": "value with spaces"}
        self.unicode_label = u"1"
        self.unicode_properties = {u"property": u"value with spaces"}
        self.graphName = "graphTest"
        self.graph = Graph.objects.create(name=self.graphName,
                                          schema=mySchema, owner=self.u)

    def test_graph_creation(self):
        """
        Tests that a graph is created.
        """
        self.assertIsNotNone(self.graph)
        self.assertEqual(self.graph.name, self.graphName)
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

    def test_nodes_create_unicode(self):
        """
        Tests node creation with unicode label
        """
        n = self.graph.nodes.create(label=self.unicode_label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.unicode_label)
        Graph.objects.get(name=self.graphName).destroy()

    def test_nodes_edition(self):
        """
        Tests node edition
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n._label = "2"
        self.assertNotEqual(n.label, self.label)
        Graph.objects.get(name=self.graphName).destroy()

    def test_nodes_edition_unicode(self):
        """
        Tests node edition with unicode label
        """
        n = self.graph.nodes.create(label=self.label)
        self.assertIsNotNone(n)
        self.assertEqual(n.label, self.label)
        n._label = u"2"
        self.assertNotEqual(n.label, self.label)
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()

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
        Graph.objects.get(name=self.graphName).destroy()
        Graph.objects.get(name=cloneGraphName).destroy()

    def test_graph_import(self):
        """
        Tests graph imported
        """
        authenticate(username='john', password='hello')
        login = self.c.login(username='john', password='hello')
        self.assertTrue(login)
        response = self.c.get('/accounts/signin/')
        self.assertIsNotNone(response.content)
        response = self.c.post('/accounts/signin/', {'username': 'john', 'password': 'hello'})
        self.assertEqual(response.status_code, 200)
        request = self.factory.get('/import/')
        request.user = self.u
        self.assertIsNotNone(tools.views.graph_import_tool(request, self.graph.slug))
        Graph.objects.get(name=self.graphName).destroy()

    def test_graph_export(self):
        """
        Tests graph exported
        """
        authenticate(username='john', password='hello')
        login = self.c.login(username='john', password='hello')
        self.assertTrue(login)
        response = self.c.get('/accounts/signin/')
        self.assertIsNotNone(response.content)
        response = self.c.post('/accounts/signin/', {'username': 'john', 'password': 'hello'})
        self.assertEqual(response.status_code, 200)
        Graph.objects.get(name=self.graphName).destroy()


class RelationshipTest(TestCase):
    """
    A set of tests for testing Relationship.
    """

    def setUp(self):
        """
        Sets up a few attributes and and objects for the tests we'll run.
        """
        self.node_label = '1'
        self.relationship_label = '2'
        self.property_key = 'location'
        self.property_value = "Bob's house"
        user = User.objects.create(
            username='bob',
            password='bob_secret',
            email='bob@cultureplex.ca')
        schema = Schema.objects.create()
        NodeType.objects.create(
            id=self.node_label, name="Bob's node type 1", schema=schema)
        RelationshipType.objects.create(
            id=self.relationship_label, name="Bob's relationship type",
            schema=schema)
        self.graph = Graph.objects.create(
            name="Bob's graph", schema=schema, owner=user)
        node_1 = self.graph.nodes.create(label=self.node_label)
        node_2 = self.graph.nodes.create(label=self.node_label)
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
        Graph.objects.get(name="Bob's graph").destroy()

    def test_relationship_edition(self):
        """
        Test Relationship edition from the created one.
        """
        try:
            self.relationship.get(self.property_key)
            exist = True
        except KeyError:
            exist = False

        self.assertEqual(exist, False)

        self.relationship.set(self.property_key, self.property_value)
        self.assertEqual(self.relationship.get(
            self.property_key), self.property_value)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_relationship_deletion(self):
        """
        Test Relationship deletion from the edition one.
        """
        self.graph.relationships.delete(id=self.relationship_id)

        try:
            self.graph.relationships._get(self.relationship_id)
            exist = True
        except RelationshipDoesNotExist:
            exist = False
        self.assertEqual(exist, False)
        Graph.objects.get(name="Bob's graph").destroy()


class APIGraphTest(APITestCase):
    def setUp(self):
        # We register a user
        self.user = User.objects.create(username='john', password='doe',
                                        is_active=True, is_staff=True)
        self.user.save()

        # We login with the new user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.factory = APIRequestFactory()

        # Let's store some names for our graph for testing purposes
        self.graph_name = "graphTest"
        self.graph_name_changed = "graphTestChanged"

        # Let's store the basic url, useful for the calls
        self.graphs_url = '/api/graphs/'

    def tearDown(self):
        self.client.logout()

    def test_api_graphs_get_empty(self):
        url = self.graphs_url
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

    def test_api_graphs_get_graphs(self):
        Graph.objects.create(name=self.graph_name, owner=self.user)

        url = self.graphs_url
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results contains the graph
        # The response.data contains a list with the graphs
        response_graph_name = response.data[0]['name']
        self.assertEqual(response_graph_name, self.graph_name)

    def test_api_graphs_post(self):
        data = {'name': self.graph_name}

        url = self.graphs_url
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results contains the graph
        # The response.data contains a list with the graphs
        response_graph_name = response.data['name']
        self.assertEqual(response_graph_name, self.graph_name)

    def test_api_graph_get(self):
        graph = Graph.objects.create(name=self.graph_name, owner=self.user)
        graph_slug = graph.slug

        url = self.graphs_url + graph_slug + '/'
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the result has the same name
        response_graph_name = response.data['name']
        self.assertEqual(response_graph_name, self.graph_name)

    def test_api_graph_delete(self):
        graph = Graph.objects.create(name=self.graph_name, owner=self.user)
        graph_slug = graph.slug

        url = self.graphs_url + graph_slug + '/'
        response = self.client.delete(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 204)
        # We check that the result returns a None object
        self.assertEqual(response.data, None)

    def test_api_graph_patch(self):
        data = {'name': self.graph_name_changed}
        graph = Graph.objects.create(name=self.graph_name, owner=self.user)
        graph_slug = graph.slug

        url = self.graphs_url + graph_slug + '/'

        # First, we check a get request
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the result has the same name
        response_graph_name = response.data['name']
        self.assertEqual(response_graph_name, self.graph_name)

        # And then, the patch to see the changes
        response = self.client.patch(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the result has the same name
        response_graph_name = response.data['name']
        self.assertEqual(response_graph_name, self.graph_name_changed)

    def test_api_graph_put(self):
        data = {}
        graph = Graph.objects.create(name=self.graph_name, owner=self.user)
        graph_slug = graph.slug

        url = self.graphs_url + graph_slug + '/'

        # First, we check a get request
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the result has the same name
        response_graph_name = response.data['name']
        self.assertEqual(response_graph_name, self.graph_name)

        # And then, the patch to see the changes
        response = self.client.put(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the result has the same name
        response_graph_name = response.data['last_modified']
        self.assertEqual(response_graph_name, None)
