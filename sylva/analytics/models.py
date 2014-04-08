# -*- coding: utf-8 -*-

from django.db import models
import datetime

from django.utils.translation import gettext as _
from graphs.models import Graph


class Analytic(models.Model):
    graph = models.ForeignKey(Graph, related_name='analytics')
    #dump = models.ForeignKey(Dump, related_name='dump')

    ALGOS = (
        ("pagerank", _("Page Rank")),
        ("hits", _("HITS")),
        ("diameter", _("Network Diameter")),
    )

    algorithm = models.CharField(max_length=8, choices=ALGOS)
    #results = models.FileField()

    # tasks attributes

    task_id = models.CharField(_("task_id"), max_length=250, null=True, blank=True)
    task_start = models.DateTimeField(_("task_start"), null=True, blank=True)
    task_end = models.DateTimeField(_("task_end"), null=True, blank=True)

    """
    task_status
    task_errors
    task_message
    """


class AnalysisManager(models.Manager):

    def __init__(self, graph, **kwargs):
        self._graph = graph

    def run(self, algorithm, **kwargs):
        analysis = self._graph.gdb.analysis()
        algorithm_func = getattr(analysis, algorithm, None)
        analytic = Analytic.objects.create(graph=self._graph, algorithm=algorithm)
        task = algorithm_func.apply_async(kwargs={'graph': self._graph, 'analytic': analytic})
        # Get the task values
        analytic.task_start = datetime.datetime.now()
        analytic.task_id = task.id
        analytic.save()

        return analytic
