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

    def _clean_count(self, count):
        if isinstance(count, (tuple, list)):
            return len(count)
        else:
            return count

    def _get_count(self, index, label=None):
        gremlin = self.gdb.neograph.extensions.GremlinPlugin.execute_script
        if label:
            script = """g.idx("%s")[[label:"%s"]].count()""" % (index.name,
                                                                label)
        else:
            script = """g.idx("%s")[[graph:"%s"]].count()""" % (index.name,
                                                                self.graph_id)
        count = gremlin(script=script)
        return self._clean_count(count)

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.node_index.neoindex
        return self._get_count(index, label=label)

    def get_relationships_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.relationship_index.neoindex
        return self._get_count(index, label=label)

    def get_node_relationships_count(self, id, incoming=False, outgoing=False,
                                     label=None):
        """
        Get the number of all relationships of a node.
        If "incoming" is True, it only counts the ids for incoming ones.
        If "outgoing" is True, it only counts the ids for outgoing ones.
        If "label" is provided, relationships will be filtered.
        """
        index = self.node_index.neoindex
        gremlin = self.gdb.neograph.extensions.GremlinPlugin.execute_script
        script = """g.idx("%s")[[id:"%s"]]""" % (index.name, id)
        if incoming:
            script = u"%s.inE" % script
        elif outgoing:
            script = u"%s.outE" % script
        else:
            # Same effect that incoming=True, outgoing=True
            script = u"%s.bothE" % script
        if label:
            script = u"%s.filter{it.label==""}" % label
        script = u"%s.count()" % script
        count = gremlin(script=script)
        return self._clean_count(count)

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
