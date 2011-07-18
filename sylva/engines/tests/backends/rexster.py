#!/usr/bin/env python
#-*- coding:utf8 -*-


from engines.gdb.backends import (GraphDatabaseInitializationError,
                                   GraphDatabaseConnectionError)

from engines.gdb.backends.rexster import GraphDatabase
from engines.tests.backends.blueprints import BlueprintsEngineTestSuite


class RexsterEngineTestSuite(BlueprintsEngineTestSuite):

    REXSTER_TEST_HOST = 'http://localhost:8182'
    REXSTER_TEST_GRAPHNAME = 'tinkergraph'

    def returnBlueprintsGraph(self):
        return GraphDatabase(self.REXSTER_TEST_HOST, 
                            {"graphname": self.REXSTER_TEST_GRAPHNAME},
                            graph=self.sylva_graph)

    def testMissingGraph(self):
        self.assertRaises(GraphDatabaseInitializationError,
                            GraphDatabase,
                            self.REXSTER_TEST_HOST, 
                            {"graphname": self.REXSTER_TEST_GRAPHNAME})

    def testInvalidUrl(self):
        self.assertRaises(GraphDatabaseConnectionError,
                            GraphDatabase,
                            'http://invalidurl',
                            {"graphname": self.REXSTER_TEST_GRAPHNAME},
                            graph=self.sylva_graph)

    def testMissingParameter(self):
        self.assertRaises(GraphDatabaseInitializationError,
                            GraphDatabase,
                            self.REXSTER_TEST_HOST)

    def testValidUrl(self):
        g = self.returnBlueprintsGraph()
        self.assertIsInstance(g, GraphDatabase)
