# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from engines.models import Instance
from graphs.models import Graph


def create_and_get_gdb(test):
    instance = Instance(name=test.instanceName, engine=test.instanceEngine,
                        port="7373", path="db/sylva", owner=test.user)
    instance.save()
    test.assertIsNotNone(instance)
    test.assertIsNotNone(test.graph)
    gdb = instance.get_gdb(test.graph)
    test.assertIsNotNone(gdb)
    return gdb


def get_query_dict(lookup, datatype=None):
    if not datatype:
        datatype = u'default'
    query_dict = {
        u'patterns': [],
        u'meta': {
            u'boxes_properties': {},
            u'has_distinct': True,
            u'with_statement': {}
        },
        u'conditions': [
            [lookup,
                [u'property', u'property_1', u'ejemplo'],
                u'pepe',
                u'not',
                datatype]
        ],
        u'results': [
            {u'alias': u'property_1',
             u'properties': [{
                 u'display_alias': u'Property 1.Ejemplo',
                 u'alias': u'property_1.Ejemplo',
                 u'distinct': u'',
                 u'datatype': u'default',
                 u'aggregate': False,
                 u'property': u'Name'}]}
        ],
        u'origins': [
            {u'alias': u'Property 1',
             u'type': u'node',
             u'slug': u'property_1',
             u'type_id': 2}]
    }
    return query_dict


class LookupsTestSuite(TestCase):
    def setUp(self):
        # We register a user
        self.user = User.objects.create(username='john', password='doe',
                                        is_active=True, is_staff=True)
        # We create a graph
        self.graph_name = "graphTest"
        self.graph = Graph.objects.create(name=self.graph_name,
                                          owner=self.user)
        self.instanceName = "instanceNeo4j"
        self.instanceEngine = "engines.gdb.backends.neo4j"
        self.instancePort = "7474"
        self.instancePath = "db/data"
        # Lookups property and match
        self.property = 'property1'
        self.match = 'match'

        # Query mandatory param
        self.only_ids = None

    def test_lookups_exact(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'exact'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` = {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="exact",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u'match')

    def test_lookups_iexact(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'iexact'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="iexact",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match')

    def test_lookups_contains(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'contains'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup objects
        lookup = self.graph.Q(property=self.property,
                              lookup="contains",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'.*match.*')

    def test_lookups_icontains(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'icontains'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="icontains",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i).*match.*')

    def test_lookups_startswith(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'startswith'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        lookup = self.graph.Q(property=self.property,
                              lookup="startswith",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'match.*')

    def test_lookups_istartswith(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'istartswith'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="istartswith",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match.*')

    def test_lookups_endswith(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'endswith'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="endswith",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'.*match')

    def test_lookups_iendswith(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'iendswith'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="iendswith",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i).*match')

    def test_lookups_regex(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'regex'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="regex",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'match')

    def test_lookups_iregex(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'iregex'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` =~ {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="iregex",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match')

    def test_lookups_gt_regular(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'gt'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` > {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup=">",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` > {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_gt_date(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'gt'
        datatype = u'date'
        query_dict = get_query_dict(lookup, datatype)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        query_params = {u'p0': u"'27/01/15'"}
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` > {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup=">",
                              match=self.match,
                              datatype=u'date')
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` > {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_gte_regular(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'gte'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` > {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup=">=",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` >= {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_gte_date(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'gte'
        datatype = u'date'
        query_dict = get_query_dict(lookup, datatype)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` > {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup=">=",
                              match=self.match,
                              datatype=u'date')
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` >= {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_lt_regular(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'lt'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` < {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="<",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` < {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_lt_date(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'lt'
        datatype = u'date'
        query_dict = get_query_dict(lookup, datatype)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` < {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="<",
                              match=self.match,
                              datatype=u'date')
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` < {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_lte_regular(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'lte'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` < {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="<=",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <= {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_lte_date(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'lte'
        datatype = u'date'
        query_dict = get_query_dict(lookup, datatype)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` < {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="<=",
                              match=self.match,
                              datatype=u'date')
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <= {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_in(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'in'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` IN {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="in",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` IN {p0}')
        self.assertEqual(match['p0'], u"[m', 'a', 't', 'c', 'h]")

    def test_lookups_inrange(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'inrange'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` IN {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="inrange",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` IN {p0}')
        self.assertEqual(match['p0'], u"[m', 'a', 't', 'c', 'h]")

    def test_lookups_isnull_with_match(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'isnull'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` = {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="isnull",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"null")

    def test_lookups_isnull_without_match(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'isnull'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` = {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="isnull",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"null")

    def test_lookups_equals(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'equals'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` = {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="equals",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"match")

    def test_lookups_neq(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'neq'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` <> {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="neq",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <> {p0}')
        self.assertEqual(match['p0'], u"match")

    def test_lookups_notequals(self):
        # cypher test
        gdb = create_and_get_gdb(self)
        # query dict and lookup
        lookup = u'notequals'
        query_dict = get_query_dict(lookup)
        script, query_params = gdb._query_generator(query_dict, self.only_ids)
        cypher = gdb.cypher
        cypher(q=script, params=query_params)
        self.assertEqual(
            u"START `property_1`=node:`1_nodes`('label:2') WHERE `property_1`."
            u"`ejemplo` <> {p0} RETURN DISTINCT `property_1`.`Name`", script)
        # lookup creation test
        lookup = self.graph.Q(property=self.property,
                              lookup="notequals",
                              match=self.match)
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <> {p0}')
        self.assertEqual(match['p0'], u"match")
