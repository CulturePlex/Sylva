# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from graphs.models import Graph


class LookupsTestSuite(TestCase):
    def setUp(self):
        # We register a user
        self.user = User.objects.create(username='john', password='doe',
                                        is_active=True, is_staff=True)
        self.user.save()
        # We create a graph
        self.graph_name = "graphTest"
        self.graph = Graph.objects.create(name=self.graph_name,
                                          owner=self.user)
        self.graph_slug = self.graph.slug
        # Lookups property and match
        self.property = 'property1'
        self.match = 'match'

    def test_lookups_exact(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="exact",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u'match')

    def test_lookups_iexact(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="iexact",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match')

    def test_lookups_contains(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="contains",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'.*match.*')

    def test_lookups_icontains(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="icontains",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i).*match.*')

    def test_lookups_startswith(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="startswith",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'match.*')

    def test_lookups_istartswith(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="istartswith",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match.*')

    def test_lookups_endswith(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="endswith",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'.*match')

    def test_lookups_iendswith(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="iendswith",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i).*match')

    def test_lookups_regex(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="regex",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'match')

    def test_lookups_iregex(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="iregex",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` =~ {p0}')
        self.assertEqual(match['p0'], u'(?i)match')

    def test_lookups_gt_regular(self):
        lookup = self.graph.Q(property=self.property,
                              lookup=">",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` > {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_gt_date(self):
        lookup = self.graph.Q(property=self.property,
                              lookup=">",
                              match=self.match,
                              datatype=u'date')
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` > {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_gte_regular(self):
        lookup = self.graph.Q(property=self.property,
                              lookup=">=",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` >= {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_gte_date(self):
        lookup = self.graph.Q(property=self.property,
                              lookup=">=",
                              match=self.match,
                              datatype=u'date')
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` >= {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_lt_regular(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="<",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` < {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_lt_date(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="<",
                              match=self.match,
                              datatype=u'date')
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` < {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_lte_regular(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="<=",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <= {p0}')
        self.assertEqual(match['p0'], u'')

    def test_lookups_lte_date(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="<=",
                              match=self.match,
                              datatype=u'date')
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <= {p0}')
        self.assertEqual(match['p0'], u"")

    def test_lookups_in(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="in",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` IN {p0}')
        self.assertEqual(match['p0'], u"[m', 'a', 't', 'c', 'h]")

    def test_lookups_inrange(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="inrange",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` IN {p0}')
        self.assertEqual(match['p0'], u"[m', 'a', 't', 'c', 'h]")

    def test_lookups_isnull_with_match(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="isnull",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"null")

    def test_lookups_isnull_without_match(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="isnull",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <> {p0}')
        self.assertEqual(match['p0'], u"null")

    def test_lookups_eq(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="eq",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"match")

    def test_lookups_equals(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="equals",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` = {p0}')
        self.assertEqual(match['p0'], u"match")

    def test_lookups_neq(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="neq",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <> {p0}')
        self.assertEqual(match['p0'], u"match")

    def test_lookups_notequals(self):
        lookup = self.graph.Q(property=self.property,
                              lookup="notequals",
                              match=self.match)
        # lookup objects
        query = lookup.get_query_objects()[0]
        match = lookup.get_query_objects()[1]
        self.assertEqual(query, u'`n`.`property1` <> {p0}')
        self.assertEqual(match['p0'], u"match")
