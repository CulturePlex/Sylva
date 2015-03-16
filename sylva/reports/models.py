# -*- coding: utf-8 -*-
import datetime
import json
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
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
    email_to = models.ManyToManyField(
        User,
        verbose_name=_("email_to"),
        related_name="report_templates",
        blank=True,
        null=True)

    def __unicode__(self):
        return self.name

    def execute(self):
        queries = self.queries.all()
        query_dicts = {query.id: (query.execute(headers=True), query.name)
                       for query in queries}
        table = []
        for row in self.layout["layout"]:
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
        self.save(update_fields=["last_run"])
        report.save()

    def dictify(self):
        template = {
            'name': self.name,
            'slug': self.slug,
            'start_date': json.dumps(self.start_date, default=_dthandler),
            'frequency': self.frequency,
            'last_run': json.dumps(self.last_run, default=_dthandler),
            'layout': self.layout,
            'description': self.description,
            'collabs': [{"id": u.username, "display": u.username} for u in
                        self.email_to.all()]
        }
        return template


def get_upload(self, filename):
    return u"%s/%s/pdfs/%s" % (self.template.graph.slug, self.template.slug,
                               filename)


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
    pdf = models.FileField(_('pdf'), upload_to=get_upload, blank=True,
                           null=True, max_length=255)

    def __unicode__(self):
        return self.date_run.isoformat()

    def dictify(self):
        report = {
            'id': self.id,
            'table': self.table,
            'date_run': json.dumps(self.date_run, default=_dthandler)
        }
        return report


@receiver(post_save, sender=Report)
def post_report_save(sender, **kwargs):
    if kwargs.get("created", False):
        inst = kwargs["instance"]
        email_to = inst.template.email_to.all()
        if email_to:
            emails = [u.email for u in email_to]
            # Avoid circular import...? Weird. But this won't register outsid
            # of models unless I import it in __init__.py, but this causees
            # celery task queue import error.
            from tasks import generate_pdf, send_email
            res = (generate_pdf.si(inst) | send_email.si(inst, emails))()
            # Call tasks - it will start with generate pdf, then callback
            # some async map onto all of the emails needed to be sent.
        print("Received signal, report created. Length {0}".format(len(email_to)))



def _dthandler(obj):
    return obj.isoformat()
