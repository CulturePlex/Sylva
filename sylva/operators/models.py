# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from jsonfield import JSONField

from graphs.models import Graph


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
    query_dict = JSONField()
    query_aliases = JSONField()
    query_fields = JSONField()

    def __unicode__(self):
      return self.name
