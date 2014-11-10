# -*- coding: utf-8 -*-
import datetime
import json
from django.db import models
from django.utils.translation import gettext as _
from jsonfield import JSONField

from graphs.models import Graph
from queries.models import Query
from sylva.fields import AutoSlugField


class ReportTemplate(models.Model):
    name = models.CharField(_('name'), max_length=150)
    slug = AutoSlugField(
        populate_from=['name'],
        max_length=250,
        editable=False,
        unique=True
    )
    start_date = models.DateTimeField(_('start date'))
    FREQUENCY_CHOICES = (
        ((u'h'), _(u'Hourly')),
        ((u'd'), _(u'Daily')),
        ((u'w'), _(u'Weekly')),
        ((u'm'), _(u'Monthly'))
    )
    frequency = models.CharField(
        _('frequency'),
        max_length=1,
        choices=FREQUENCY_CHOICES,
        default=u'w'
    )
    last_run = models.DateTimeField(_('last run'), blank=True, null=True)
    layout = JSONField(_('layout'))
    description = models.TextField(_('description'), blank=True, null=True)
    graph = models.ForeignKey(
        Graph,
        verbose_name=_('graph'),
        related_name='report_templates'
    )
    queries = models.ManyToManyField(
        Query,
        verbose_name=_('queries'),
        related_name='report_templates',
        blank='true',
        null='true'
    )

    def __unicode__(self):
        return self.name

    def execute(self):
        queries = self.queries.all()
        # EXECUTE QUERIES HERE
        query_dicts = {query.id: (query.execute(), query.name)
                       for query in queries}
        table = []
        for row in self.layout:
            new_row = []
            for cell in row:
                query = cell.get('displayQuery', '')
                if query:
                    query = int(query)
                    attrs = query_dicts[query]
                    cell['series'] = attrs[0]
                    cell['name'] = attrs[1]
                new_row.append(cell)
            table.append(new_row)
        report = Report(
            date_run=datetime.datetime.now(),
            table=table,
            template=self
        )
        self.last_run = datetime.datetime.now()
        self.save()
        report.save()
        # Here I need to update the last_run attr

    def historify(self):
        report_dict = self.dictify()
        reports = self.reports.order_by('-date_run')
        report_dict['history'] = [{k: v for (k, v) in report.dictify().items()
                                   if k != 'table'} for report in reports]
        return report_dict

    def dictify(self):
        template = {
            'name': self.name,
            'slug': self.slug,
            'start_date': json.dumps(self.start_date, default=_dthandler),
            'frequency': self.frequency,
            'last_run': json.dumps(self.last_run, default=_dthandler),
            'layout': self.layout,
            'description': self.description
        }
        return template


class Report(models.Model):
    date_run = models.DateTimeField()
    slug = AutoSlugField(
        populate_from=['date_run'],
        max_length=250,
        editable=False,
        unique=True
    )
    table = JSONField(_('table'))
    template = models.ForeignKey(
        ReportTemplate,
        verbose_name=_('template'),
        related_name='reports'
    )

    def __unicode__(self):
        return self.date_run.isoformat()

    def dictify(self):
        report = {
            'id': self.id,
            'table': self.table,
            'date_run': json.dumps(self.date_run, default=_dthandler)
        }
        return report


def _dthandler(obj):
    return obj.isoformat()
