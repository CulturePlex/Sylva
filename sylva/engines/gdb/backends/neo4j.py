# -*- coding: utf-8 -*-
from lucenequerybuilder import Q
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase
from pyblueprints.neo4j import Neo4jDatabaseConnectionError

from engines.gdb.backends import (GraphDatabaseConnectionError,
                                  GraphDatabaseInitializationError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase
from engines.gdb.lookups.neo4j import Q as q_lookup_builder
try:
    from engines.gdb.analysis.neo4j import Analysis
except ImportError:
    Analysis = None


WILDCARD_TYPE = -1
AGGREGATES = ["count", "max", "min", "sum", "average", "deviation"]

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

    def _prepare_script(self, for_node=True, label=None):
        """
        Creates part of the script for the cypher query.
        """
        if for_node:
            var = 'n'
            type = 'node'
            index = self.nidx.name
        else:
            var = 'r'
            type = 'rel'
            index = self.ridx.name
        if isinstance(label, (list, tuple)):
            if label:
                label = """ OR """.join(['label:%s' % str(label_id) for label_id in label])
            else:
                """
                It will never pass by here.
                It was checked before call this method.
                """
                pass
        else:
            if label:
                label = """label:%s""" % (label)
            else:
                label = """label:*"""
        script = """start %s=%s:`%s`('%s') """ % (var, type, index, label)
        return script

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if isinstance(label, (list, tuple)) and not label:
            return 0
        script = self._prepare_script(for_node=True, label=label)
        script = """%s return count(n)""" % script
        count = self.cypher(query=script)
        return self._clean_count(count)

    def get_relationships_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if isinstance(label, (list, tuple)) and not label:
            return 0
        script = self._prepare_script(for_node=False, label=label)
        script = """%s return count(r)""" % script
        count = self.cypher(query=script)
        return self._clean_count(count)

    def get_all_nodes(self, include_properties=False, limit=None, offset=None,
                      order_by=None):
        """
        Get an iterator for the list of tuples of all nodes, the first element
        is the id of the node and the third the node label.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties. Otherwise, None.
        """
        nodes = self.get_filtered_nodes(lookups=None, label=None,
                                        include_properties=include_properties,
                                        limit=limit, offset=offset,
                                        order_by=order_by)
        for node in nodes:
            yield node

    def get_all_relationships(self, include_properties=False,
                              limit=None, offset=None, order_by=None):
        """
        Get an iterator for the list of tuples of all relationships, the
        first element is the id of the node.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties.
        """
        rels = self.get_filtered_relationships(lookups=None, label=None,
                                        include_properties=include_properties,
                                        limit=limit, offset=offset,
                                        order_by=order_by)
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
                           limit=None, offset=None, order_by=None):
        return self.get_filtered_nodes([], label=label,
                                       include_properties=include_properties,
                                       limit=limit, offset=offset,
                                       order_by=order_by)

    def get_filtered_nodes(self, lookups, label=None, include_properties=None,
                           limit=None, offset=None, order_by=None):
        # Using Cypher
        cypher = self.cypher
        if isinstance(label, (list, tuple)) and not label:
            return
        script = self._prepare_script(for_node=True, label=label)
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
        if order_by:
            script = u"%s order by n.`%s` %s " % (script, order_by[0][0].replace('`', '\`'), order_by[0][1])
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
                                   limit=None, offset=None, order_by=None):
        return self.get_filtered_relationships(
            [], label=label, include_properties=include_properties,
            limit=limit, offset=offset, order_by=order_by)

    def get_filtered_relationships(self, lookups, label=None,
                                   include_properties=None,
                                   limit=None, offset=None, order_by=None):
        # Using Cypher
        cypher = self.cypher
        if isinstance(label, (list, tuple)) and not label:
            return
        script = self._prepare_script(for_node=False, label=label)
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
        if order_by:
            script = u"%s order by n.`%s` %s " % (script, order_by[0][0].replace('`', '\`'), order_by[0][1])
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

    def query(self, query_dict, limit=None, offset=None, order_by=None):
        script, query_params = self._query_generator(query_dict)
        cypher = self.cypher
        page = 1000
        skip = offset or 0
        limit = limit or page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(query=paged_script, params=query_params)
        except:
            result = None
        while result and "data" in result and len(result["data"]) > 0:
            for element in result["data"]:
                if "data" in element:
                    yield element["data"]
                else:
                    yield element
            for element in result["columns"]:
                if "columns" in element:
                    yield element["columns"]
                else:
                    yield element
            skip += page
            if len(result["data"]) == limit:
                try:
                    paged_script = "%s skip %s limit %s" % (script, skip,
                                                            limit)
                    result = cypher(query=paged_script, params=query_params)
                except:
                    result = None
            else:
                break

    def _query_generator(self, query_dict):
        conditions_dict = query_dict["conditions"]
        conditions_result = self._query_generator_conditions(conditions_dict)
        # _query_generator_conditions returns a list
        # with conditions ,query_params and the list of conditions alias to
        # check if a relationship has lookups or not for the index treatment
        conditions = conditions_result[0]
        query_params = conditions_result[1]
        conditions_alias = conditions_result[2]
        origins_dict = query_dict["origins"]
        origins = self._query_generator_origins(origins_dict, conditions_alias)
        results_dict = query_dict["results"]
        results = self._query_generator_results(results_dict)
        patterns_list = []
        if "patterns" in query_dict:
            patterns_dict = query_dict["patterns"]
            patterns_list = self._query_generator_patterns(patterns_dict,
                                                           conditions_alias)
        if patterns_list:
            patterns = ", ".join(patterns_list)
            match = u"MATCH {0} ".format(patterns)
        else:
            match = u""
        if conditions:
            where = u"WHERE {0} ".format(conditions)
        else:
            where = u""
        q = u"START {0} {1}{2}RETURN DISTINCT {3}".format(origins, match,
                                                          where, results)
        print q
        return q, query_params

    def _query_generator_conditions(self, conditions_dict):
        query_params = dict()
        # This list is used to control when use the index for the relationship,
        # in the origins or in the patterns
        conditions_alias = []
        conditions_list = []
        conditions_indexes = enumerate(conditions_dict)
        conditions_length = len(conditions_dict) - 1
        for lookup, property_tuple, match, connector, datatype \
                in conditions_dict:
            if lookup == "between":
                gte = q_lookup_builder(property=property_tuple[2],
                                       lookup="gte",
                                       match=match[0],
                                       var=property_tuple[1],
                                       datatype=datatype)
                lte = q_lookup_builder(property=property_tuple[2],
                                       lookup="lte",
                                       match=match[1],
                                       var=property_tuple[1],
                                       datatype=datatype)
                gte_query_objects = gte.get_query_objects(params=query_params)
                lte_query_objects = lte.get_query_objects(params=query_params)
                gte_condition = gte_query_objects[0]
                gte_params = gte_query_objects[1]
                lte_condition = lte_query_objects[0]
                lte_params = lte_query_objects[1]
                conditions_list.append(unicode(gte_condition))
                query_params.update(gte_params)
                conditions_list.append(unicode(lte_condition))
                query_params.update(lte_params)
                # We append the two property in the list
                conditions_alias.append(property_tuple[1])
            elif lookup == 'idoesnotcontain':
                q_element = ~q_lookup_builder(property=property_tuple[2],
                                              lookup="icontains",
                                              match=match,
                                              var=property_tuple[1],
                                              datatype=datatype)
                query_objects = q_element.get_query_objects(
                    params=query_params)
                condition = query_objects[0]
                params = query_objects[1]
                conditions_list.append(unicode(condition))
                query_params.update(params)
                # We append the two property in the list
                conditions_alias.append(property_tuple[1])
            else:
                q_element = q_lookup_builder(property=property_tuple[2],
                                             lookup=lookup,
                                             match=match,
                                             var=property_tuple[1],
                                             datatype=datatype)
                query_objects = q_element.get_query_objects(
                    params=query_params)
                condition = query_objects[0]
                params = query_objects[1]
                conditions_list.append(unicode(condition))
                query_params.update(params)
                # We append the two property in the list
                conditions_alias.append(property_tuple[1])
            if connector != 'not':
                # We have to get the next element to keep the concordance
                elem = conditions_indexes.next()
                connector = u' {} '.format(connector.upper())
                conditions_list.append(connector)
            elif connector == 'not':
                elem = conditions_indexes.next()
                if elem[0] < conditions_length:
                    connector = u' AND '
                    conditions_list.append(connector)
        conditions = u" ".join(conditions_list)
        return (conditions, query_params, conditions_alias)

    def _query_generator_origins(self, origins_dict, conditions_alias):
        origins_list = []
        for origin_dict in origins_dict:
            if origin_dict["type"] == "node":
                node_type = origin_dict["type_id"]
                # wildcard type
                if node_type == WILDCARD_TYPE:
                    node_type = '*'
                origin = u"""`{alias}`=node:`{nidx}`('label:{type}')""".format(
                    nidx=unicode(self.nidx.name).replace(u"`", u"\\`"),
                    alias=unicode(origin_dict["alias"]).replace(u"`", u"\\`"),
                    type=node_type,
                )
                origins_list.append(origin)
            else:
                relation_type = origin_dict["type_id"]
                # wildcard type
                if relation_type == WILDCARD_TYPE:
                    origin = u"""`{alias}`=rel:`{ridx}`('graph:{graph_id}')""".format(
                        ridx=unicode(self.ridx.name).replace(u"`", u"\\`"),
                        alias=unicode(origin_dict["alias"]).replace(u"`",
                                                                    u"\\`"),
                        graph_id=self.graph_id,
                    )
                # TODO: Why with not rel indices in START the query is faster?
                else:
                    alias = origin_dict["alias"]
                    if alias in conditions_alias:
                        origin = u"""{alias}=rel:`{ridx}`('label:{type}')""".format(
                            ridx=unicode(self.ridx.name).replace(u"`",
                                                                 u"\\`"),
                            alias=unicode(alias).replace(u"`",
                                                                        u"\\`"),
                            type=relation_type,
                        )
                        origins_list.append(origin)
        origins = u", ".join(origins_list)
        return origins

    def _query_generator_results(self, results_dict):
        results_list = []
        for result_dict in results_dict:
            alias = result_dict["alias"]
            if result_dict["properties"] is None:
                result = u"`{0}`".format(
                    unicode(alias).replace(u"`", u"\\`"))
                results_list.append(result)
            else:
                for prop in result_dict["properties"]:
                    property_value = prop["property"]
                    property_aggregate = prop["aggregate"]
                    property_distinct = prop["distinct"]
                    if property_value:
                        if not property_aggregate:
                            result = u"`{0}`.`{1}`".format(
                                unicode(alias).replace(u"`",
                                                                      u"\\`"),
                                unicode(property_value).replace(u"`", u"\\`")
                            )
                            results_list.append(result)
                        else:
                            if property_aggregate in AGGREGATES:
                                result = u"{0}(`{1}`.`{2}`)".format(
                                    unicode(property_aggregate),
                                    unicode(alias).replace(u"`",u"\\`"),
                                    unicode(property_value).replace(u"`",
                                                                    u"\\`")
                                )
                                results_list.append(result)
        results = u", ".join(results_list)
        return results

    def _query_generator_patterns(self, patterns_dict, conditions_alias):
        patterns_list = []
        for pattern_dict in patterns_dict:
                source = pattern_dict["source"]["alias"]
                target = pattern_dict["target"]["alias"]
                relation = pattern_dict["relation"]["alias"]
                relation_type = pattern_dict["relation"]["type_id"]
                # wildcard type
                if relation_type == -1:
                    pattern = u"(`{source}`)-[`{rel}`]-(`{target}`)".format(
                        source=unicode(source).replace(u"`", u"\\`"),
                        rel=unicode(relation).replace(u"`", u"\\`"),
                        target=unicode(target).replace(u"`", u"\\`"),
                    )
                else:
                    if relation in conditions_alias:
                        pattern = u"(`{source}`)-[`{rel}`]-(`{target}`)".format(
                            source=unicode(source).replace(u"`", u"\\`"),
                            rel=unicode(relation).replace(u"`", u"\\`"),
                            rel_type=unicode(relation_type).replace(u"`",
                                                                    u"\\`"),
                            target=unicode(target).replace(u"`", u"\\`"),
                        )
                    else:
                        pattern = u"(`{source}`)-[`{rel}`:`{rel_type}`]-(`{target}`)".format(
                            source=unicode(source).replace(u"`", u"\\`"),
                            rel=unicode(relation).replace(u"`", u"\\`"),
                            rel_type=unicode(relation_type).replace(u"`",
                                                                    u"\\`"),
                            target=unicode(target).replace(u"`", u"\\`"),
                        )
                patterns_list.append(pattern)
        return patterns_list

    def destroy(self):
        """Delete nodes, relationships, and even indices"""
        all_rels = self.get_all_relationships(include_properties=False)
        for rel_id, props, label in all_rels:
            self.delete_relationship(rel_id)
        all_nodes = self.get_all_nodes(include_properties=False)
        for node_id, props, label in all_nodes:
            self.delete_node(node_id)
        self.nidx.delete()
        self.ridx.delete()
        self = None

    def analysis(self):
        if Analysis is not None:
            return Analysis()
        else:
            return None
