# -*- coding: utf-8 -*-
from django.db import models

from django.utils.translation import gettext as _
from graphs.models import Graph


def get_upload_to_analytics(self, filename):
    return u"%s/analytics/%s" % (self.graph.slug, filename)


def get_upload_to_dump(self, filename):
    analytic = self.analytics.latest()
    return u"%s/dumps/%s" % (analytic.graph.slug, filename)


class DataDump(models.Model):
    creation_date = models.DateTimeField(_("creation date"), null=True,
                                         blank=True)
    data_file = models.FileField(_("data file"), upload_to=get_upload_to_dump,
                                 null=True, blank=True)

    class Meta:
        get_latest_by = "creation_date"


class Analytic(models.Model):
    graph = models.ForeignKey(Graph, verbose_name=_("graph"),
                              related_name='analytics')
    dump = models.ForeignKey(DataDump, verbose_name=_("data dump"),
                             related_name='analytics')
    algorithm = models.CharField(_("Algorithm"), max_length=255)
    raw = models.FileField(_("Raw file"), upload_to=get_upload_to_analytics,
                           null=True, blank=True)
    results = models.FileField(_("Results file"), upload_to=
                               get_upload_to_analytics, null=True, blank=True)
    subgraph = models.CharField(_("Subgraph"),
                                max_length=255, null=True,
                                blank=True)

    # tasks attributes
    task_id = models.CharField(_("task_id"), max_length=255, null=True,
                               blank=True)
    task_start = models.DateTimeField(_("task_start"), null=True,
                                      blank=True)
    task_end = models.DateTimeField(_("task_end"), null=True,
                                    blank=True)
    task_status = models.CharField(_("task_status"), max_length=255,
                                   null=True, blank=True)
    task_error = models.CharField(_("task_error"), max_length=255,
                                  null=True, blank=True)

    class Meta:
        get_latest_by = "task_start"


class AnalysisManager(models.Manager):

    def __init__(self, graph, **kwargs):
        self._graph = graph

    def run(self, algorithm, **kwargs):
        analysis = self._graph.gdb.analysis()
        # affected_nodes_array = "[669, 670, 671, 672, 673, 674,
        #675, 676, 677, 678, 679, 680, 693, 694, 716]"
        # analytic = Analytic.objects.create(graph=self._graph,
        #    algorithm=algorithm, affected_nodes=affected_nodes_array)
        analytic = Analytic.objects.create(graph=self._graph,
                                           algorithm=algorithm)
        # algorithm_task = analysis.run_task(algorithm, self._graph,
        #                                    analytic)
        task = analysis.run_algorithm.apply_async(
            kwargs={'analytic': analytic,
                    'analysis': analysis})

        analytic.task_id = task.id
        analytic.save()

        return analytic

    def estimated_time(self, algorithm, **kwargs):
        analysis = self._graph.gdb.analysis()
        task = analysis.run_estimated_time.apply_async(
            kwargs={'analysis': analysis,
                    'graph': self._graph,
                    'algorithm': algorithm})

        return task
