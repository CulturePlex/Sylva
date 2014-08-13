# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from jsonfield import JSONField

from sylva.fields import AutoSlugField
from graphs.models import Graph
from operators.models import Query


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
        ((u'w'), _(u'Weekley')),
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

    # Various methods here


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

    # Various methods here