# -*- coding: utf-8 -*-
from lucenequerybuilder import Q
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase
from pyblueprints.neo4j import Neo4jDatabaseConnectionError

from engines.gdb.backends import (GraphDatabaseConnectionError,
                                  GraphDatabaseInitializationError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase
from engines.gdb.lookups.neo4j import Q as q_lookup_builder


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
        self._nidx = None
        self._ridx = None
        self._gremlin = None
        self._cypher = None

    def _get_nidx(self):
        if not self._nidx:
            self._nidx = self.node_index.neoindex
        return self._nidx
    nidx = property(_get_nidx)

    def _get_ridx(self):
        if not self._ridx:
            self._ridx = self.relationship_index.neoindex
        return self._ridx
    ridx = property(_get_ridx)

    def _get_gremlin(self):
        if not self._gremlin:
            plugin = self.gdb.neograph.extensions.GremlinPlugin.execute_script
            self._gremlin = plugin
        return self._gremlin
    gremlin = property(_get_gremlin)

    def _get_cypher(self):
        if not self._cypher:
            plugin = self.gdb.neograph.extensions.CypherPlugin.execute_query
            self._cypher = plugin
        return self._cypher
    cypher = property(_get_cypher)

    def _clean_count(self, count):
        try:
            return count["data"][0][0]
        except IndexError:
            return 0

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.nidx
        if label:
            script = """start n=node:`%s`('label:%s')""" % (index.name, label)
        else:
            script = """start n=node:`%s`('label:*')""" % (index.name)
        script = """%s return count(n)""" % script
        count = self.cypher(query=script)
        return self._clean_count(count)

    def get_relationships_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.ridx
        if label:
            script = """start r=rel:`%s`('label:%s')""" % (index.name, label)
        else:
            script = """start r=rel:`%s`('label:*')""" % (index.name)
        script = """%s return count(r)""" % script
        count = self.cypher(query=script)
        return self._clean_count(count)

    def get_all_nodes(self, include_properties=False, limit=None, offset=None):
        """
        Get an iterator for the list of tuples of all nodes, the first element
        is the id of the node and the third the node label.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties. Otherwise, None.
        """
        nodes = self.get_filtered_nodes(lookups=None, label=None,
                                        include_properties=include_properties,
                                        limit=limit, offset=offset)
        for node in nodes:
            yield node

    def get_all_relationships(self, include_properties=False,
                              limit=None, offset=None):
        """
        Get an iterator for the list of tuples of all relationships, the
        first element is the id of the node.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties.
        """
        rels = self.get_filtered_relationships(lookups=None, label=None,
                                        include_properties=include_properties,
                                        limit=limit, offset=offset)
        for rel in rels:
            yield rel

    def get_node_relationships_count(self, id, incoming=False, outgoing=False,
                                     label=None):
        """
        Get the number of all relationships of a node.
        If "incoming" is True, it only counts the ids for incoming ones.
        If "outgoing" is True, it only counts the ids for outgoing ones.
        If "label" is provided, relationships will be filtered.
        """
        gremlin = self.gremlin
        script = """g.idx("%s")[[id:"%s"]]""" % (self.nidx.name, id)
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

    def get_nodes_by_label(self, label, include_properties=False,
                           limit=None, offset=None):
        return self.get_filtered_nodes([], label=label,
                                       include_properties=include_properties,
                                       limit=limit, offset=offset)

    def get_filtered_nodes(self, lookups, label=None, include_properties=None,
                           limit=None, offset=None):
        # Using Cypher
        cypher = self.cypher
        if label:
            script = """start n=node:`%s`('label:%s') """ \
                     % (self.nidx.name, label)
        else:
            script = """start n=node:`%s`('label:*') """ \
                     % self.nidx.name
        where = None
        params = []
        if lookups:
            wheres = q_lookup_builder()
            for lookup in lookups:
                if isinstance(lookup, q_lookup_builder):
                    wheres &= lookup
                elif isinstance(lookup, dict):
                    wheres &= q_lookup_builder(**lookup)
            where, params = wheres.get_query_objects(var="n")
        if where:
            script = u"%s where %s return " % (script, where)
        else:
            script = u"%s return " % script
        if include_properties:
            script = u"%s id(n), n" % script
        else:
            script = u"%s id(n)" % script
        page = 1000
        skip = offset or 0
        limit = limit or page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(query=paged_script, params=params)
        except:
            result = None
        while result and "data" in result:
            if include_properties:
                for element in result["data"]:
                    properties = element[1]["data"]
                    elto_id = properties.pop("_id")
                    elto_label = properties.pop("_label")
                    properties.pop("_graph", None)
                    yield (elto_id, properties, elto_label)
            else:
                for element in result["data"]:
                    if len(element) > 1:
                        yield (element[0], None, element[1])
                    else:
                        yield (element[0], None, None)
            skip += limit
            if len(result["data"]) == limit:
                try:
                    paged_script = "%s skip %s limit %s" % (script, skip,
                                                            limit)
                    result = cypher(query=paged_script, params=params)
                except:
                    result = None
            else:
                break

    def get_relationships_by_label(self, label, include_properties=False,
                                   limit=None, offset=None):
        return self.get_filtered_relationships([], label=label,
                                        include_properties=include_properties,
                                        limit=limit, offset=offset)

    def get_filtered_relationships(self, lookups, label=None,
                                   include_properties=None,
                                   limit=None, offset=None):
        # Using Cypher
        cypher = self.cypher
        if label:
            script = """start r=rel:`%s`('label:%s') """ % (self.ridx.name,
                                                            label)
        else:
            script = """start r=rel:`%s`('label:*') """ % self.ridx.name
        script = """%s match a-[r]->b """ % script
        where = None
        params = []
        if lookups:
            wheres = q_lookup_builder()
            for lookup in lookups:
                if isinstance(lookup, q_lookup_builder):
                    wheres &= lookup
                elif isinstance(lookup, dict):
                    wheres &= q_lookup_builder(**lookup)
            where, params = wheres.get_query_objects(var="r")
        if include_properties:
            type_or_r = "r"
        else:
            type_or_r = "type(r)"
        if where:
            script = u"%s where %s return distinct id(r), %s, a, b" \
                     % (script, where, type_or_r)
        else:
            script = u"%s return distinct id(r), %s, a, b" \
                     % (script, type_or_r)
        page = 1000
        skip = offset or 0
        limit = limit or page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(query=paged_script, params=params)
        except:
            result = None
        while result and "data" in result and len(result["data"]) > 0:
            if include_properties:
                for element in result["data"]:
                    properties = element[1]["data"]
                    properties.pop("_id")
                    properties.pop("_graph", None)
                    elto_label = properties.pop("_label")
                    source_props = element[2]["data"]
                    source_id = source_props.pop("_id")
                    source_label = source_props.pop("_label")
                    source_props.pop("_graph", None)
                    source = {
                        "id": source_id,
                        "properties": source_props,
                        "label": source_label
                    }
                    target_props = element[3]["data"]
                    target_id = target_props.pop("_id")
                    target_label = target_props.pop("_label")
                    target_props.pop("_graph", None)
                    target = {
                        "id": target_id,
                        "properties": target_props,
                        "label": target_label
                    }
                    yield (element[0], properties, elto_label, source, target)
            else:
                for element in result["data"]:
                    yield (element[0], None, element[1])
            skip += page
            if len(result["data"]) == limit:
                try:
                    paged_script = "%s skip %s limit %s" % (script, skip,
                                                            limit)
                    result = cypher(query=paged_script, params=params)
                except:
                    result = None
            else:
                break

    def lookup_builder(self):
        return q_lookup_builder
