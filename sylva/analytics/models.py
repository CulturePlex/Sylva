# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _

from graphs.models import Graph


def get_upload_to_analytics(self, filename):
    return u"%s/analytics/%s" % (self.dump.graph.slug, filename)


def get_upload_to_dump(self, filename):
    return u"%s/dumps/%s" % (self.graph.slug, filename)


class Dump(models.Model):
    graph = models.ForeignKey(Graph, verbose_name=_("graph"),
                              related_name='dumps')
    creation_date = models.DateTimeField(_("creation date"), null=True,
                                         blank=True)
    data_file = models.FileField(_("data file"), upload_to=get_upload_to_dump,
                                 null=True, blank=True, max_length=255)
    data_hash = models.CharField(_("data hash"), max_length=255)

    class Meta:
        get_latest_by = "creation_date"

    def get_data_file_path(self):
        """
        Returns self.data_file.path or download the file for those storages
        that don't support absolute paths and return a temporary file path
        """
        try:
            data_file_path = self.data_file.path
        except NotImplementedError:
            data_file_path = self.data_file.url
        return data_file_path


class Analytic(models.Model):
    dump = models.ForeignKey(Dump, verbose_name=_("data dump"),
                             related_name='analytics')
    algorithm = models.CharField(_("Algorithm"), max_length=255)
    raw = models.FileField(_("Raw file"), upload_to=get_upload_to_analytics,
                           null=True, blank=True, max_length=255)
    results = models.FileField(_("Results file"), null=True, blank=True,
                               upload_to=get_upload_to_analytics,
                               max_length=255)
    values = models.FileField(_("Values file"), null=True, blank=True,
                              upload_to=get_upload_to_analytics,
                              max_length=255)
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

    def get_raw_path(self):
        """
        Returns self.raw.path or download the file for those storages
        that don't support absolute paths and return a temporary file path
        """
        try:
            raw_path = self.raw.path
        except NotImplementedError:
            raw_path = self.raw.url
        return raw_path


class AnalysisManager(models.Manager):

    def __init__(self, graph, **kwargs):
        self._graph = graph
        self._analysis = self._graph.gdb.analysis()

    def run(self, algorithm, subgraph=None, **kwargs):
        dump = self._analysis.get_dump(self._graph.id, subgraph)
        analytic = Analytic.objects.create(dump=dump,
                                           algorithm=algorithm)
        task = self._analysis.run.apply_async(
            kwargs={'analytic_id': analytic.id,
                    'analysis': self._analysis})
        analytic.task_id = task.id
        analytic.save()
        return analytic

    def estimate(self, algorithm):
        estimation = self._analysis.estimate(
            analysis=self._analysis,
            graph=self._graph,
            algorithm=algorithm
        )
        return estimation

    def get_algorithms(self):
        return self._analysis.get_algorithms()
