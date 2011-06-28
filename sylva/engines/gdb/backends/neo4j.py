# -*- coding: utf-8 -*-
from neo4jrestclient.client import GraphDatabase as Neo4jGraphDatabase

from engines.gdb.backends import BaseGraphDatabase


class GraphDatabase(BaseGraphDatabase):

    def __init__(self, *args, **kwargs):
        super(GraphDatabase, self).__init__(*args, **kwargs)
        self.gdb = Neo4jGraphDatabase(self.url)
