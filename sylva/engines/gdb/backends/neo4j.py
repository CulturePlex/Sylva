# -*- coding: utf-8 -*-
from lucenequerybuilder import Q
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase
from pyblueprints.neo4j import Neo4jDatabaseConnectionError

from engines.gdb.backends import (GraphDatabaseConnectionError,
                                GraphDatabaseInitializationError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase


class GraphDatabase(BlueprintsGraphDatabase):

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        self.graph = graph
        if not self.graph:
            raise GraphDatabaseInitializationError("graph parameter required")
        self.graph_id = str(self.graph.id)
        try:
            self.gdb = Neo4jGraphDatabase(self.url)
        except Neo4jDatabaseConnectionError:
            raise GraphDatabaseConnectionError(self.url) 
        self.setup_indexes()

    def get_filtered_nodes(self, lookups, label=None, include_properties=None):
        """
        Get an iterator for filtered nodes using the parameters expressed in
        the dictionary lookups.
        The most usual lookups from Django should be implemented.
        More info: https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
        """
        idx = self.node_index.neoindex
        q = Q(r"graph", r"%s" % self.graph_id)
        if label:
            q &= Q(r"label", r"%s" % label)
        for lookup in lookups:
            l = Q()
            if lookup["lookup"] == "contains":
                l |= Q(r"%s" % lookup["property"], r"*%s*" % lookup["match"],
                       wildcard=True)
            elif lookup["lookup"] == "starts":
                l |= Q(r"%s" % lookup["property"], r"%s*" % lookup["match"],
                      wildcard=True)
            elif lookup["lookup"] == "ends":
                l |= Q(r"%s" % lookup["property"], r"*%s" % lookup["match"],
                       wildcard=True)
            elif lookup["lookup"] == "exact":
                l |= Q(r"%s" % lookup["property"], r"%s" % lookup["match"])
        q = q & (l)
        if include_properties:
            for node in idx.query(q):
                yield (node.id, node.properties)
        else:
            for node in idx.query(q):
                yield (node.id, None)
