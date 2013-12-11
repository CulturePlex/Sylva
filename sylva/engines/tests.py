#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.test import TestCase

from engines.gdb.utils import get_connection_string
from engines.models import Instance
from graphs.models import Graph, User
from data.models import Data

gdb_properties = settings.GRAPHDATABASES["tests"]
connection_string = get_connection_string(gdb_properties)


class InstanceNeo4jTestSuite(TestCase):
    def setUp(self):
        self.u = User(username="Me")
        self.u.save()
        d = Data()
        d.save()
        self.sylva_graph = Graph(name="mygraph", data=d, owner=self.u)
        self.sylva_graph.save()
        self.instanceName = "instanceNeo4j"
        self.instanceEngine = "engines.gdb.backends.neo4j"
        self.instancePort = "7474"
        self.instancePath = "db/data"

    def test_instance_creation_neo4j(self):
        """
        Tests that a neo4j instance is created.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)

    def test_instance_edition_neo4j(self):
        """
        Tests that a neo4j instance is edited.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, self.instanceName)
        instance.name = "instanceNeo4jSet"
        self.assertEqual(instance.name, "instanceNeo4jSet")

    def test_instance_gdb_neo4j(self):
        """
        Tests that a neo4j instance has a graph database.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port="7373", path="db/sylva", owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        self.assertIsNotNone(self.sylva_graph)
        gdb = instance.get_gdb(self.sylva_graph)
        self.assertIsNotNone(gdb)

    def test_instance_deletion_neo4j(self):
        """
        Tests that a neo4j instance is deleted.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        instance_id = instance.id
        Instance.objects.get(pk=instance_id).delete()
        try:
            Instance.objects.get(pk=instance_id)
            exists = True
        except Instance.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)


class InstanceRexsterTestSuite(TestCase):
    def setUp(self):
        self.u = User(username="Me")
        self.u.save()
        d = Data()
        d.save()
        self.sylva_graph = Graph(name="mygraph", data=d, owner=self.u)
        self.sylva_graph.save()
        self.instanceName = "instanceRexster"
        self.instanceEngine = "engines.gdb.backends.rexster"
        self.instancePort = "7474"
        self.instancePath = "db/data"

    def test_instance_creation_rexster(self):
        """
        Tests that a rexster instance is created.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)

    def test_instance_edition_rexster(self):
        """
        Tests that a rexster instance is edited.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, self.instanceName)
        instance.name = "instanceRexsterSet"
        self.assertEqual(instance.name, "instanceRexsterSet")

    def test_instance_gdb_rexster(self):
        """
        Tests that a rexster instance has a graph database (TODO).
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port="7373", path="db/sylva", owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        self.assertIsNotNone(self.sylva_graph)
        # gdb = instance.get_gdb(self.sylva_graph)
        # self.assertIsNotNone(gdb)

    def test_instance_deletion_rexster(self):
        """
        Tests that a rexster instance is deleted.
        """
        instance = Instance(name=self.instanceName, engine=self.instanceEngine, port=self.instancePort, path=self.instancePath, owner=self.u)
        instance.save()
        self.assertIsNotNone(instance)
        instance_id = instance.id
        Instance.objects.get(pk=instance_id).delete()
        try:
            Instance.objects.get(pk=instance_id)
            exists = True
        except Instance.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)
