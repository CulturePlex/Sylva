# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.template.defaultfilters import slugify

from neo4jrestclient.exceptions import StatusException
from pyblueprints.neo4j import (
    Neo4jTransactionalIndexableGraph as Neo4jGraphDatabase)
from pyblueprints.neo4j import Neo4jDatabaseConnectionError

from engines.gdb.backends import (GraphDatabaseConnectionError,
                                  GraphDatabaseInitializationError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase, VERTEX
from engines.gdb.lookups.neo4j import Q as q_lookup_builder
try:
    from engines.gdb.analysis.neo4j import Analysis
except ImportError:
    Analysis = None
if settings.ENABLE_SPATIAL:
    import geojson
    from shapely.geometry import shape
    # Any symbol would work
    SPATIAL_INDEX_KEY = "$"
    SPATIAL_INDEX_VALUE = "$"
    SPATIAL_PROPERTY_NAMES = ("bbox", "gtype")


WILDCARD_TYPE = -1
AGGREGATES = {
    "Count": "count",
    "Max": "max",
    "Min": "min",
    "Sum": "sum",
    "Average": "avg",
    "Deviation": "stdev"
}


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
        self._cypher = None
        self._spatial = None
        self.transaction = getattr(self.gdb.neograph, "transaction", None)
        if settings.ENABLE_SPATIAL:
            self.sidx = {}  # shortcut for spatial indices
            self.setup_spatial()

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

    def _get_cypher(self):
        if not self._cypher:
            # Look for the native Cypher endpoint first
            try:
                cypher_func = self.gdb.neograph.query
            except AttributeError:
                func = self.gdb.neograph.extensions.CypherPlugin.execute_query

                def cypher_func(q, params=None, **kwargs):
                    return func(query=q, params=params, **kwargs)

            self._cypher = cypher_func
        return self._cypher
    cypher = property(_get_cypher)

    def _clean_count(self, count):
        try:
            return count["data"][0][0]
        except (IndexError, KeyError):
            return 0

    def _escape(self, val):
        return unicode(val).replace(u"`", u"\\`")

    def _prepare_script(self, for_node=True, label=None):
        """
        Creates part of the script for the cypher query.
        """
        if for_node:
            var = 'n'
            var_type = 'node'
            index = self.nidx.name
        else:
            var = 'r'
            var_type = 'rel'
            index = self.ridx.name
        if isinstance(label, (list, tuple)):
            label = """ OR """.join(['label:%s' % str(label_id)
                                     for label_id in label])
        elif label:
            label = """label:%s""" % (label)
        else:
            label = """label:*"""
        script = """start %s=%s:`%s`('%s') """ % (var, var_type, index, label)
        return script

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if isinstance(label, (list, tuple)) and not label:
            return 0
        if self.nidx not in self.gdb.neograph.nodes.indexes.values():
            return 0
        script = self._prepare_script(for_node=True, label=label)
        script = """%s return count(n)""" % script
        count = self.cypher(q=script)
        return self._clean_count(count)

    def get_relationships_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if isinstance(label, (list, tuple)) and not label:
            return 0
        if self.ridx not in self.gdb.neograph.relationships.indexes.values():
            return 0
        script = self._prepare_script(for_node=False, label=label)
        script = """%s return count(r)""" % script
        count = self.cypher(q=script)
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
        rels = self.get_filtered_relationships(
            lookups=None, label=None, include_properties=include_properties,
            limit=limit, offset=offset, order_by=order_by)
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
        # Using Cypher
        if isinstance(label, (list, tuple)) and not label:
            return 0
        if self.ridx not in self.gdb.neograph.relationships.indexes.values():
            return 0
        # """start %s=%s:`%s`('%s') """ % (var, type, index, label)
        script = self._prepare_script(for_node=False, label=label)
        if incoming:
            script = u"%s match (n)<-[r]-()" % script
        elif outgoing:
            script = u"%s match (n)-[r]->()" % script
        else:
            # Same effect that incoming=True, outgoing=True
            script = u"%s (n)-[r]-()" % script
        script = """%s return count(r)""" % script
        count = self.cypher(q=script)
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
        params = {}
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
            script = u"%s order by n.`%s` %s " % (
                script, order_by[0][0].replace(u'`', u'\\`'), order_by[0][1]
            )
        page = 1000
        skip = offset or 0
        limit = limit or page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(q=paged_script, params=params)
        except:
            result = None
        while result and "data" in result:
            if include_properties:
                for element in result["data"]:
                    properties = element[1]["data"]
                    elto_id = properties.pop("_id")
                    elto_label = properties.pop("_label")
                    properties.pop("_graph", None)
                    if settings.ENABLE_SPATIAL:
                        for to_remove in SPATIAL_PROPERTY_NAMES:
                            properties.pop(to_remove, None)
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
                    result = cypher(q=paged_script, params=params)
                except:
                    result = None
            else:
                break

    def get_relationships_by_label(self, label, include_properties=False,
                                   source_id=None, target_id=None,
                                   directed=True,
                                   limit=None, offset=None, order_by=None):
        return self.get_filtered_relationships(
            [], label=label, include_properties=include_properties,
            source_id=source_id, target_id=target_id, directed=directed,
            limit=limit, offset=offset, order_by=order_by)

    def get_filtered_relationships(self, lookups, label=None,
                                   include_properties=None,
                                   source_id=None, target_id=None,
                                   directed=True,
                                   limit=None, offset=None, order_by=None):
        # Using Cypher
        cypher = self.cypher
        if isinstance(label, (list, tuple)) and not label:
            return
        script = self._prepare_script(for_node=False, label=label)
        if source_id and target_id:
            script = """%s, a=node(%s), b=node(%s)""" % (
                script, source_id, target_id)
        elif source_id and not target_id:
            script = """%s, a=node(%s)""" % (script, source_id)
        elif not source_id and target_id:
            script = """%s, b=node(%s)""" % (script, target_id)
        if directed:
            script = """%s match (a)-[r]->(b) """ % script
        else:
            script = """%s match (a)-[r]-(b) """ % script
        where = None
        params = {}
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
            script = u"%s order by n.`%s` %s " % (
                script, order_by[0][0].replace(u'`', u'\\`'), order_by[0][1]
            )
        page = 1000
        skip = offset or 0
        limit = limit or page
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(q=paged_script, params=params)
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
                    target_props = element[3]["data"]
                    target_id = target_props.pop("_id")
                    target_label = target_props.pop("_label")
                    target_props.pop("_graph", None)
                    if settings.ENABLE_SPATIAL:
                        for to_remove in SPATIAL_PROPERTY_NAMES:
                            source_props.pop(to_remove, None)
                            target_props.pop(to_remove, None)
                    source = {
                        "id": source_id,
                        "properties": source_props,
                        "label": source_label
                    }
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
                    result = cypher(q=paged_script, params=params)
                except:
                    result = None
            else:
                break

    def lookup_builder(self):
        return q_lookup_builder

    def query(self, query_dict, limit=None, offset=None, order_by=None,
              headers=None, only_ids=None):
        results_list = []
        script, query_params = self._query_generator(query_dict, only_ids)
        cypher = self.cypher
        page = 1000
        skip = offset or 0
        limit = limit or page
        if order_by is not None:
            alias = order_by[0]
            # We check if it is an aggregate
            if alias == 'aggregate':
                script = u"%s order by `%s` %s " % (script,
                                                    order_by[1],
                                                    order_by[2])
            else:
                script = u"%s order by `%s`.`%s` %s " % (
                    script, alias.replace(u'`', u'\\`'),
                    order_by[1].replace(u'`', u'\\`'),
                    order_by[2])
        try:
            paged_script = "%s skip %s limit %s" % (script, skip, limit)
            result = cypher(q=paged_script, params=query_params)
        except:
            result = None
        if headers is True and result and "columns" in result:
                results_list.append(result["columns"])
        while result and "data" in result and len(result["data"]) > 0:
            for element in result["data"]:
                if "data" in element:
                    results_list.append(element["data"])
                else:
                    results_list.append(element)
            skip += page
            if len(result["data"]) == limit:
                try:
                    paged_script = "%s skip %s limit %s" % (script, skip,
                                                            limit)
                    result = cypher(q=paged_script, params=query_params)
                except:
                    result = None
            else:
                break
        return results_list

    def _query_generator(self, query_dict, only_ids):
        distinct = ""
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
        results = self._query_generator_results(results_dict, only_ids)
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
            # Let's check if the 'with_statement' exists
            with_statement = query_dict["meta"]["with_statement"]
            if with_statement:
                with_header = "WITH "
                with_list = []
                for key, val in with_statement.iteritems():
                    with_list.append(key + " AS " + val)
                with_params = ','.join(with_list)
                _with = with_header + with_params
                where = u"{0} WHERE {1} ".format(_with, conditions)
            else:
                where = u"WHERE {0} ".format(conditions)
        else:
            where = u""
        # We treat the meta dictionary to know if we need to include the global
        # distinct
        try:
            has_distinct = query_dict["meta"]["has_distinct"]
        except KeyError:
            has_distinct = False
        if has_distinct:
            distinct = u" DISTINCT"
        q = u"START {0} {1}{2}RETURN{3}{4}".format(origins, match, where,
                                                   distinct, results)

        return q, query_params

    def _query_generator_conditions(self, conditions_dict):
        query_params = {}
        # This list is used to control when use the index for the relationship,
        # in the origins or in the patterns
        conditions_alias = set()
        # conditions_set = set()
        # We are going to use a list because when the set add elements,
        # it include them in order and breaks our pattern with AND, OR
        conditions_set = []
        conditions_indexes = enumerate(conditions_dict)
        conditions_length = len(conditions_dict) - 1
        for condition_dict in conditions_dict:
            lookup, property_tuple, match, connector, datatype = condition_dict
            # This is the option to have properties of another boxes
            if datatype == "property_box":
                match_dict = {}
                # We catch exception of type IndexError, in case that we
                # doesn't receive an appropiate array.
                try:
                    # The match can be defined in three different ways:
                    # slug.property_id
                    # aggregate (slug.property_id)
                    # aggregate (DISTINCT slug.property_id)
                    # And also, we could have two match values for
                    # 'in between' lookups...
                    match_results = []
                    match_elements = []
                    datatypes = []
                    if not isinstance(match, (tuple, list)):
                        match_elements.append(match)
                        datatypes.append(datatype)
                    else:
                        match_elements = match
                        datatypes = datatype
                    index = 0
                    while index < len(match_elements):
                        match_element = match_elements[index]
                        if datatypes[index] == 'property_box':
                            # Let's check what definition we have...
                            match_splitted = re.split('\)|\(|\\.| ',
                                                      match_element)
                            match_first_element = match_splitted[0]
                            # We check if aggregate belongs to the aggregate
                            # set
                            if match_first_element not in AGGREGATES.keys():
                                slug = match_first_element
                                prop = match_splitted[1]
                                match_var, match_property = (
                                    self._get_slug_and_prop(slug, prop))
                                # Finally, we assign the correct values to the
                                # dict
                                match_dict['var'] = match_var
                                match_dict['property'] = match_property
                                match = match_dict
                            else:
                                # We have aggregate
                                aggregate = match_first_element
                                match_second_element = match_splitted[1]
                                # We check if we already have the distinct
                                # clause
                                if match_second_element != 'DISTINCT':
                                    # We get the slug and the property
                                    slug = match_second_element
                                    prop = match_splitted[2]
                                    match_var, match_property = (
                                        self._get_slug_and_prop(slug, prop))
                                    # Once we have the slug and the prop, we
                                    # build the
                                    # aggregate again
                                    agg_field = u"{0}({1}.{2})".format(
                                        aggregate, match_var, match_property)
                                    match_dict['aggregate'] = agg_field
                                    match = match_dict
                                else:
                                    # We have distinct, slug and the property
                                    distinct = match_second_element
                                    # We get the slug and the property
                                    slug = match_splitted[2]
                                    prop = match_splitted[3]
                                    match_var, match_property = (
                                        self._get_slug_and_prop(slug, prop))
                                    # Once we have the slug and the prop, we
                                    # build the aggregate again
                                    agg_field = (
                                        u"{0}({1} {2}.{3})".format(
                                            aggregate, distinct, match_var,
                                            match_property))
                                    match_dict['aggregate'] = agg_field
                                    match = match_dict
                        else:
                            match = match_element
                        index = index + 1
                        match_results.append(match)
                    if len(match_results) == 1:
                        match = match_results[0]
                    else:
                        match = match_results
                except IndexError:
                    match_dict['var'] = ""
                    match_dict['property'] = ""
                    match = match_dict

            if lookup == "between":
                gte = q_lookup_builder(property=property_tuple[2],
                                       lookup="gte",
                                       match=match[0],
                                       var=property_tuple[1],
                                       datatype=datatype[0])
                lte = q_lookup_builder(property=property_tuple[2],
                                       lookup="lte",
                                       match=match[1],
                                       var=property_tuple[1],
                                       datatype=datatype[1])
                gte_query_objects = gte.get_query_objects(params=query_params)
                lte_query_objects = lte.get_query_objects(params=query_params)
                gte_condition = gte_query_objects[0]
                gte_params = gte_query_objects[1]
                lte_condition = lte_query_objects[0]
                lte_params = lte_query_objects[1]
                # conditions_set.add(unicode(gte_condition))
                if gte_condition not in conditions_set:
                    conditions_set.append(unicode(gte_condition))
                query_params.update(gte_params)
                # conditions_set.add(unicode(lte_condition))
                if lte_condition not in conditions_set:
                    conditions_set.append(unicode(lte_condition))
                query_params.update(lte_params)
                # We append the two property in the list
                conditions_alias.add(property_tuple[1])
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
                # conditions_set.add(unicode(condition))
                if condition not in conditions_set:
                    conditions_set.append(unicode(condition))
                query_params.update(params)
                # We append the two property in the list
                conditions_alias.add(property_tuple[1])
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
                # conditions_set.add(unicode(condition))
                if condition not in conditions_set:
                    conditions_set.append(unicode(condition))
                # Uncomment this line to see the difference between use
                # query params or use the q_element
                # conditions_set.add(unicode(q_element))
                query_params.update(params)
                # We append the two property in the list
                conditions_alias.add(property_tuple[1])
            if connector != 'not':
                # We have to get the next element to keep the concordance
                elem = conditions_indexes.next()
                connector = u' {} '.format(connector.upper())
                # conditions_set.add(connector)
                conditions_set.append(connector)
            elif connector == 'not':
                elem = conditions_indexes.next()
                if elem[0] < conditions_length:
                    connector = u' AND '
                    # conditions_set.add(connector)
                    conditions_set.append(connector)
        # We check if we have only one condition and one operator
        if len(conditions_set) > 0:
            conditions_last_index = len(conditions_set) - 1
            conditions_last_element = conditions_set[conditions_last_index]
            if (conditions_last_element == ' AND ' or
                    conditions_last_element == ' OR '):
                conditions_set.pop()
        conditions = u" ".join(conditions_set)
        return (conditions, query_params, conditions_alias)

    def _query_generator_origins(self, origins_dict, conditions_alias):
        origins_set = set()
        for origin_dict in origins_dict:
            # This is to maintain the logic for the older queries
            try:
                alias = origin_dict['slug']
            except KeyError:
                alias = origin_dict['alias']
            if origin_dict["type"] == "node":
                node_type = origin_dict["type_id"]
                # wildcard type
                if node_type == WILDCARD_TYPE:
                    node_type = '*'
                origin = u"""`{alias}`=node:`{nidx}`('label:{type}')""".format(
                    nidx=self._escape(self.nidx.name),
                    alias=self._escape(alias),
                    type=node_type,
                )
                origins_set.add(origin)
            else:
                relation_type = origin_dict["type_id"]
                # wildcard type
                if relation_type == WILDCARD_TYPE:
                    _origin = u"""`{alias}`=rel:`{ridx}`('graph:{graph_id}')"""
                    origin = _origin.format(
                        ridx=self._escape(self.ridx.name),
                        alias=self._escape(alias),
                        graph_id=self.graph_id,
                    )
                # TODO: Why with not rel indices in START the query is faster?
                else:
                    if alias in conditions_alias:
                        _origin = u"""`{alias}`=rel:`{ridx}`('label:{type}')"""
                        origin = _origin.format(
                            ridx=self._escape(self.ridx.name),
                            alias=self._escape(alias),
                            type=relation_type,
                        )
                        origins_set.add(origin)
        origins = u", ".join(origins_set)
        return origins

    def _query_generator_results(self, results_dict, only_ids):
        results_set = set()

        for result_dict in results_dict:
            alias = result_dict["alias"]
            if result_dict["properties"] is None:
                result = u"`{0}`".format(
                    self._escape(alias))
                results_set.add(result)
            else:
                for prop in result_dict["properties"]:
                    property_value = prop["property"]
                    property_aggregate = prop["aggregate"]
                    property_distinct = prop["distinct"]
                    if property_value:
                        if not property_aggregate and not only_ids:
                            result = u"`{0}`.`{1}`".format(
                                self._escape(alias),
                                self._escape(property_value)
                            )
                            results_set.add(result)
                        elif property_aggregate and not only_ids:
                            distinct_clause = ""
                            if property_distinct:
                                distinct_clause = u"DISTINCT "
                            if property_aggregate in AGGREGATES.keys():
                                result = u"{0}({1}`{2}`.`{3}`)".format(
                                    unicode(AGGREGATES[property_aggregate]),
                                    unicode(distinct_clause),
                                    self._escape(alias),
                                    self._escape(property_value)
                                )
                                results_set.add(result)
                        else:
                            result = u"ID(`{0}`)".format(
                                self._escape(alias)
                            )
                            results_set.add(result)
        properties_results = u", ".join(results_set)

        results = u" {0}".format(properties_results)
        return results

    def _query_generator_patterns(self, patterns_dict, conditions_alias):
        patterns_set = set()
        for pattern_dict in patterns_dict:
                source = pattern_dict["source"]["alias"]
                target = pattern_dict["target"]["alias"]
                try:
                    relation = pattern_dict["relation"]["slug"]
                except KeyError:
                    relation = pattern_dict["relation"]["alias"]
                relation_type = pattern_dict["relation"]["type_id"]
                # wildcard type
                if relation_type == -1:
                    pattern = u"(`{source}`)-[`{rel}`]-(`{target}`)".format(
                        source=self._escape(source),
                        rel=self._escape(relation),
                        target=self._escape(target),
                    )
                else:
                    if relation in conditions_alias:
                        pattern = (
                            u"(`{source}`)-[`{rel}`]-(`{target}`)".format(
                                source=self._escape(source),
                                rel=self._escape(relation),
                                target=self._escape(target),
                            )
                        )
                    else:
                        pattern = (
                            u"(`{source}`)-[`{rel}`:`{rel_type}`]-(`{target}`)"
                            .format(
                                source=self._escape(source),
                                rel=self._escape(relation),
                                rel_type=self._escape(relation_type),
                                target=self._escape(target),
                            )
                        )
                patterns_set.add(pattern)
        return patterns_set

    def destroy(self):
        """Delete nodes, relationships, and even indices"""
        all_rels = self.get_all_relationships(include_properties=False)
        for rel_id, props, label in all_rels:
            self.delete_relationship(rel_id)
        all_nodes = self.get_all_nodes(include_properties=False)
        for node_id, props, label in all_nodes:
            self.delete_node(node_id)
        if self.nidx in self.gdb.neograph.nodes.indexes.values():
            self.nidx.delete()
        if self.ridx in self.gdb.neograph.relationships.indexes.values():
            self.ridx.delete()
        if settings.ENABLE_SPATIAL and self.sidx:
            for sidx_key, sidx_dict in self.sidx.items():
                index = sidx_dict["index"]
                if index in self.gdb.neograph.nodes.indexes.values():
                    index.delete()
            self.sidx = {}
        self = None

    def analysis(self):
        if settings.ENABLE_ANALYTICS and Analysis is not None:
            return Analysis()
        else:
            return None

    def _get_slug_and_prop(self, elem_slug, prop):
        # We treat the elem_slug param
        raw_slug = slugify(elem_slug)
        raw_slug_splitted = raw_slug.split("_")
        final_pos = len(raw_slug_splitted)
        match_slug = raw_slug_splitted[0: final_pos - 1]
        slug = "_".join(match_slug)
        # Let's treat the property
        property_id = prop
        property_id = int(property_id)
        # We filter for slug and then for property
        schema = self.graph.schema
        nodetype = (schema.nodetype_set.all()
                                       .filter(slug=slug)[0])
        prop_value = nodetype.properties.all().filter(
            id=property_id)
        match_property = prop_value[0].key
        # Finally, we return the values
        return elem_slug, match_property

    # Spatial
    def setup_spatial(self):
        # Setup spatial indices if they don't exist already
        # The proccess goes as follows
        # - post /db/sylva/index/node/
        # {"name": "spatial3", "config": {"provider": "spatial", "wkt": "wkt"}}
        # - post /db/sylva/index/node/spatial3
        # {"value": "0", "key": "0",
        #  "uri": "http://host:port/db/sylva/node/17600"}
        # - post /db/sylva/ext/SpatialPlugin/graphdb/addNodeToLayer
        # {"layer": "spatial3", "node": "http://host:port/db/sylva/node/17600"}
        spatial_datatypes = [u'p', u'l', u'm']
        spatial_properties = self.graph.schema.nodetype_set.filter(
            properties__datatype__in=spatial_datatypes
        ).values("id", "schema__graph__id", "properties__key",
                 "properties__id")
        indices = self.gdb.neograph.nodes.indexes
        for spatial_property in spatial_properties:
            # Spatial index name is in
            # the form: <graph_id>_<nodetype_id>_<property_id>_spatial
            spatial_index_name = u"{}_{}_{}_spatial".format(
                spatial_property["schema__graph__id"],
                spatial_property["id"],
                spatial_property["properties__id"])
            spatial_index = None
            try:
                spatial_index = indices.get(spatial_index_name)
            except StatusException:
                spatial_index = None
            finally:
                # The spatial index property to index by is
                # in the form: _spatial_<property_id>
                spatial_index_by = u"_spatial_{}".format(
                    spatial_property["properties__id"])
                if spatial_index is None:
                    spatial_index = indices.create(
                        name=spatial_index_name,
                        provider="spatial",
                        wkt=spatial_index_by
                    )
                # Keep track of properties indexed in spatial indices
                sidx_key = u"{}_{}".format(
                    spatial_property["id"],
                    spatial_property["properties__key"])
                self.sidx[sidx_key] = {
                    "index": spatial_index,
                    "key": spatial_index_by,
                }

    def _get_spatial(self):
        if not self._spatial and settings.ENABLE_SPATIAL:
            self._spatial = self.gdb.neograph.extensions.SpatialPlugin
        return self._spatial
    spatial = property(_get_spatial)

    def _index_spatial_property(self, node, key, value, label):
        sidx_key = u"{}_{}".format(label, key)
        if sidx_key in self.sidx:
            geo_value = geojson.loads(value)
            is_valid_geojson = geojson.is_valid(geo_value)['valid'] != 'no'
            if is_valid_geojson:
                # Add node to index
                index = self.sidx[sidx_key]["index"]
                index_key = self.sidx[sidx_key]["key"]
                wkt_value = shape(geo_value).wkt
                node[index_key] = wkt_value
                index.add(SPATIAL_INDEX_KEY, SPATIAL_INDEX_VALUE, node)
                # Add node to layer
                self.spatial.addNodeToLayer(layer=index.name, node=node.url)

    def _deindex_spatial_property(self, node, key, label):
        sidx_key = u"{}_{}".format(label, key)
        if sidx_key in self.sidx:
            index = self.sidx[sidx_key]["index"]
            index.delete(SPATIAL_INDEX_KEY, SPATIAL_INDEX_VALUE, node)

    def _reindex_spatial_property(self, node, key, value, label):
        self._deindex_spatial_property(node, key, label)
        self._index_spatial_property(node, key, value, label)

    def _set_element_property(self, element, key, value, element_type=None):
        super(GraphDatabase, self)._set_element_property(
            element, key, value, element_type)
        if settings.ENABLE_SPATIAL and element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            self._reindex_spatial_property(node, key, value, label)

    def _delete_element_property(self, element, key, element_type=None):
        super(GraphDatabase, self)._delete_element_property(
            element, key, element_type)
        if settings.ENABLE_SPATIAL and element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            self._deindex_spatial_property(node, key, label)

    def _set_element_properties(self, element, properties, element_type=None):
        if settings.ENABLE_SPATIAL and element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key in self._get_public_keys(element):
                self._deindex_spatial_property(node, key, label)
        super(GraphDatabase, self)._set_element_properties(
            element, properties, element_type)

    def _update_element_properties(self, element, properties,
                                   element_type=None):
        super(GraphDatabase, self)._update_element_properties(
            element, properties, element_type)
        if settings.ENABLE_SPATIAL and element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key, value in properties.items():
                self._reindex_spatial_property(node, key, value, label)

    def _delete_element_properties(self, element, element_type=None):
        if settings.ENABLE_SPATIAL and element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key in self._get_public_keys(element):
                self._deindex_spatial_property(node, key, label)
        super(GraphDatabase, self)._delete_element_properties(
            element, element_type)

    def create_node(self, label, properties=None):
        node_id = super(GraphDatabase, self).create_node(
            label=label, properties=properties)
        # We introspect all property values to see if any would have a
        # spatial value and an index in which to be indexed
        if settings.ENABLE_SPATIAL and self.sidx and properties:
            node = self.gdb.neograph.nodes.get(node_id)
            for key, value in properties.items():
                self._index_spatial_property(node, key, value, label)
        return node_id

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False, label=None):
        rels = super(GraphDatabase, self).get_node_relationships(
            id, incoming, outgoing, include_properties, label
        )
        if not settings.ENABLE_SPATIAL:
            return rels
        # If spatial enabled, avoid returning spatial
        # specific relationships by checking their label
        spatial_rel_labels = set([
            "RTREE_METADATA", "RTREE_ROOT", "RTREE_CHILD",
            "RTREE_REFERENCE", "FIRST_NODE", "LAST_NODE", "OTHER", "NEXT",
            "OSM", "WAYS", "RELATIONS", "MEMBERS", "MEMBER", "TAGS", "GEOM",
            "BBOX", "NODE", "CHANGESET", "USER", "USERS", "OSM_USER",
        ])
        clean_rels = []
        for (rel_id, rel_props) in rels:
            label = self._get_edge(rel_id).neoelement.type
            if not label in spatial_rel_labels:
                clean_rels.append((rel_id, rel_props))
        return clean_rels

    def get_node_properties(self, id):
        properties = super(GraphDatabase, self).get_node_properties(id)
        if settings.ENABLE_SPATIAL:
            for to_remove in SPATIAL_PROPERTY_NAMES:
                if to_remove in properties:
                    del properties[to_remove]
        return properties
