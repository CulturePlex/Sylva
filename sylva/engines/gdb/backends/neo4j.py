# -*- coding: utf-8 -*-
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase

from engines.gdb.backends.blueprints import BlueprintsGraphDatabase


class GraphDatabase(BlueprintsGraphDatabase):

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        self.graph = graph
        self.gdb = Neo4jGraphDatabase(self.url)
