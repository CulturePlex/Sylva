# -*- coding: utf-8 -*-
import json
from django.db import models
from django.utils.translation import gettext as _
from jsonfield import JSONField

from graphs.models import Graph
from operators.models import Query
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
    last_run = models.DateTimeField(_('last run'))
    layout = JSONField(_('layout'))
    description = models.TextField(_('description'), blank=True, null=True)
    graph = models.ForeignKey(
        Graph,
        verbose_name= _('graph'), 
        related_name='report_templates'
    )
    queries = models.ManyToManyField(
        Query,
        verbose_name=_('queries'),
        related_name='report_templates'
    )

    def historify(self):
        report_dict = self.dictify()
        reports = self.reports.order_by('-date_run')
        report_dict['history'] = [{k: v for (k, v) in report.dictify().items()
                                   if k != 'table'} for report in reports]
        return report_dict

    def dictify(self):
        template =  {
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
        verbose_name= _('template'),
        related_name='reports'
    )

    def dictify(self):
        report = {
            'slug': self.slug,
            'table': self.table,
            'date_run': json.dumps(self.date_run, default=_dthandler)
        }
        return report


def _dthandler(obj):
    return obj.isoformat()
