# -*- coding: utf-8 -*-
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase

from engines.gdb.backends import BlueprintsGraphDatabase


class GraphDatabase(BlueprintsGraphDatabase):

    def __init__(self, *args, **kwargs):
        super(BlueprintsGraphDatabase, self).__init__(*args, **kwargs)
        self.gdb = Neo4jGraphDatabase(self.url)
