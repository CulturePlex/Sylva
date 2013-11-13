#!/usr/bin/env python
#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.test import TestCase

from engines.gdb.backends import NodeDoesNotExist, RelationshipDoesNotExist
from engines.gdb.backends.neo4j import GraphDatabase
from engines.gdb.utils import get_connection_string

from engines.tests.backends.blueprints import BlueprintsEngineTestSuite

gdb_properties = settings.GRAPHDATABASES["tests"]
connection_string = get_connection_string(gdb_properties)


class Neo4jEngineTestSuite(BlueprintsEngineTestSuite):

    NEO4J_TEST_HOST = connection_string

    def testInvalidUrl(self):
        self.assertRaises(Exception,
                            GraphDatabase,
                            'http://invalidurl')

    def returnBlueprintsGraph(self):
        return GraphDatabase(self.NEO4J_TEST_HOST, graph=self.sylva_graph)

    def testValidUrl(self):
        g = self.returnBlueprintsGraph()
