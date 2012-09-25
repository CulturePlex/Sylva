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
        gremlin = self.gdb.neograph.extensions.GremlinPlugin
        if label:
            script = """g.idx("%s")[[label:"%s"]].count()""" % (index.name,
                                                                label)
        else:
            script = """g.idx("%s")[[graph:"%s"]].count()""" % (index.name,
                                                                self.graph_id)
        count = gremlin.execute_script(script=script)
        return self._clean_count(count)

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.node_index.neoindex
        return self._get_count(index, label=label)

    def get_all_nodes(self, include_properties=False):
        """
        Get an iterator for the list of tuples of all nodes, the first element
        is the id of the node and the third the node label.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties. Otherwise, None.
        """
        # Using Cypher
        index = self.node_index.neoindex
        cypher = self.gdb.neograph.extensions.CypherPlugin
        if include_properties:
            script = """start n=node:`%s`("label:*") return id(n), n""" \
                     % (index.name)
        else:
            script = """start n=node:`%s`("label:*") return id(n), n._label""" \
                     % index.name
        page = 1000
        skip = 0
        limit = page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher.execute_query(query=paged_script)
        except:
            result = None
        while result and "data" in result and len(result["data"]) > 0:
            if include_properties:
                for element in result["data"]:
                    properties = element[1]["data"]
                    elto_id = properties.pop("_id")
                    elto_label = properties.pop("_label")
                    yield (elto_id, properties, elto_label)
            else:
                for element in result["data"]:
                    yield (element[0], None, element[1])
            skip += limit
            try:
                paged_script = "%s skip %s limit %s" % (script, skip, limit)
                result = cypher.execute_query(query=paged_script)
            except:
                result = None

    def get_relationships_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        index = self.relationship_index.neoindex
        return self._get_count(index, label=label)

    def get_all_relationships(self, include_properties=False):
        """
        Get an iterator for the list of tuples of all relationships, the
        first element is the id of the node.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties.
        """
        # Using Cypher
        index = self.relationship_index.neoindex
        cypher = self.gdb.neograph.extensions.CypherPlugin
        script = """start r=rel:`%s`("label:*") """ \
                 """match a-[r]->b return distinct id(r), %s, a, b"""
        if include_properties:
            script = script % (index.name, "r")
        else:
            script = script % (index.name, "type(r)")
        page = 1000
        skip = 0
        limit = page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher.execute_query(query=paged_script)
        except:
            result = None
        while result and "data" in result and len(result["data"]) > 0:
            if include_properties:
                for element in result["data"]:
                    properties = element[1]["data"]
                    elto_label = properties.pop("_label")
                    source_props = element[2]["data"]
                    source_id = source_props.pop("_id")
                    source_label = source_props.pop("_label")
                    source = {
                        "id": source_id,
                        "properties": source_props,
                        "label": source_label
                    }
                    target_props = element[3]["data"]
                    target_id = target_props.pop("_id")
                    target_label = target_props.pop("_label")
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
            try:
                paged_script = "%s skip %s limit %s" % (script, skip, limit)
                result = cypher.execute_query(query=paged_script)
            except:
                result = None


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
        # Using Cypher
        index = self.node_index.neoindex
        cypher = self.gdb.neograph.extensions.CypherPlugin.execute_query
        if label:
            script = """start n=node:`%s`(label="%s") where""" \
                     % (index.name, label)
        else:
            script = """start n=node:`%s`("label:*") where""" \
                     % index.name
        wheres = []
        for lookup in lookups:
            where = None
            match = lookup["match"].replace(u"/", u"\\/")
            prop = lookup["property"].replace(u"`", u"\\`")
            if lookup["lookup"] == "icontains":
                where = u"( n.`%s`? =~ /(?i).*%s.*/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "istarts":
                where = u"( n.`%s`? =~ /(?i)%s.*/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "iends":
                where = u"( n.`%s`? =~ /(?i).*%s/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "iexact":
                where = u"( n.`%s`? =~ /(?i)%s/ )" \
                        % (prop, match)
            if lookup["lookup"] == "contains":
                where = u"( n.`%s`? =~ /.*%s.*/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "starts":
                where = u"( n.`%s`? =~ /%s.*/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "ends":
                where = u"( n.`%s`? =~ /.*%s/ )" \
                        % (prop, match)
            elif lookup["lookup"] == "exact":
                where = u"( n.`%s`? =~ /%s/ )" \
                        % (prop, match)
            if where:
                wheres.append(where)
        script = u"%s %s return n" % (script, " and ".join(wheres))
        result = None
        try:
            result = cypher(query=script)
        except:
            pass
        if result and "data" in result and len(result["data"]) > 0:
            if include_properties:
                for element in result["data"]:
                    properties = element[0]["data"]
                    node_id = properties.pop("_id")
                    properties.pop("_label")
                    yield (node_id, properties)
            else:
                for element in result["data"]:
                    node_id = element[0]["data"].pop("_id")
                    yield (node_id, None)

    def _get_filtered_nodes(self, lookups, label=None, include_properties=None):
        # Working on indices
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
