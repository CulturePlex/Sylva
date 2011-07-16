# -*- coding: utf-8 -*-
from pyblueprints import RexsterIndexableGraph as RexsterGraphDatabase
from pyblueprints import RexsterServer, RexsterException

from engines.gdb.backends import (GraphDatabaseConnectionError,
                                GraphDatabaseInitializationError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase


class GraphDatabase(BlueprintsGraphDatabase):

    PRIVATE_PREFIX = '^'

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        if "graphname" not in self.params:
            error_msg = "Parameter \"graphname\" is mandatory"
            raise GraphDatabaseInitializationError(error_msg)
        self.graph = graph
        self.graphname = self.params.get("graphname")
        try:
            server = RexsterServer(self.url)
            self.gdb = RexsterGraphDatabase(server, self.graphname) 
        except RexsterException:
            raise GraphDatabaseConnectionError(self.url) 
