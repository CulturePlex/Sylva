# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from jsonfield import JSONField

from graphs.models import Graph


NUMBER_TYPES = ['number', 'float', 'auto_increment', 'auto_increment_update']
AGGREGATES = ["Count", "Max", "Min", "Sum", "Average", "Deviation"]


class Query(models.Model):
    graph = models.ForeignKey(Graph, verbose_name=_("graph"),
                              related_name='queries')
    name = models.CharField(_("Name"), max_length=255)
    description = models.CharField(_("Description"),
                                   max_length=255)
    results_count = models.IntegerField(_("Number of results"),
                                        null=True, blank=True)
    last_run = models.DateTimeField(_("Last time run"),
                                    null=True, blank=True)
    has_numeric_results = models.NullBooleanField(_("Has numeric results"),
                                                  default=False)
    query_dict = JSONField()
    query_aliases = JSONField()
    query_fields = JSONField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        results = self.query_dict['results']
        for result in results:
            properties = result['properties']
            if properties:
                # We check if the query has number values or aggregates
                aggregate = properties[0]['aggregate']
                datatype = properties[0]['datatype']
                datatype_is_number = datatype in NUMBER_TYPES
                has_aggregate = aggregate in AGGREGATES
                if datatype_is_number or has_aggregate:
                    # If it has it, we set has_numeric_values to True
                    self.has_numeric_results = True
        super(Query, self).save(*args, **kwargs)


class QueryManager(models.Manager):

    def __init__(self, graph, **kwargs):
        self._graph = graph

    def plottable(self, **kwargs):
        # The queries for the reports have numeric values
        queries_for_reports = self._graph.queries.all().filter(
            has_numeric_results=True)
        return queries_for_reports
