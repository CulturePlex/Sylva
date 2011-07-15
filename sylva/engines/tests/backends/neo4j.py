#!/usr/bin/env python
#-*- coding:utf8 -*-


from django.test import TestCase

from engines.gdb.backends import NodeDoesNotExist, RelationshipDoesNotExist
from engines.gdb.backends.neo4j import GraphDatabase

from engines.tests.backends.blueprints import BlueprintsEngineTestSuite


class Neo4jEngineTestSuite(BlueprintsEngineTestSuite):

    NEO4J_TEST_HOST = 'http://localhost:7474/db/data'

    def testInvalidUrl(self):
        self.assertRaises(Exception,
                            GraphDatabase,
                            'http://invalidurl')

    def returnBlueprintsGraph(self):
        return GraphDatabase(self.NEO4J_TEST_HOST)

    def testValidUrl(self):
        g = self.returnBlueprintsGraph()
