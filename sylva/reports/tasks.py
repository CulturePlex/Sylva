# -*- coding: utf-8 -*-
import datetime
import operator
import os
from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.sites.models import Site
from celery.utils.log import get_task_logger
from models import ReportTemplate, Report
from utils import phantom_process
from views import pdf_gen_view
from sylva.celery import app


SECRET = getattr(settings, "REPORTS_SECRET", "")


logger = get_task_logger(__name__)


@app.task(name='reports.email')
def send_email(inst_id):
    inst = Report.objects.get(pk=inst_id)
    graph_slug = inst.template.graph.slug
    emails = [u.email for u in inst.template.email_to.all()]
    site = Site.objects.get_current()
    url = "{0}://{1}/reports/{2}/pdf/{3}".format("http", site.domain,
                                                 graph_slug, inst.id)
    send_mail("Sylva Reports", "Please view this report: {0}".format(url),
              settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)


@app.task(name="reports.pdf")
def generate_pdf(inst_id):
    inst = Report.objects.get(pk=inst_id)
    graph_slug = inst.template.graph.slug
    template_slug = inst.template.slug
    site = Site.objects.get_current()
    sessionid = "nosessionid"
    csrftoken = "nocsrftoken"
    filename = phantom_process(
        'http',
        site.domain,
        pdf_gen_view,
        graph_slug,
        template_slug,
        'localhost',
        csrftoken,
        sessionid,
        SECRET
    )
    try:
        with open(filename) as pdf:
            f = File(pdf)
            inst.report_file.save(filename.split("/")[-1], f)
    except IOError:
        pass
    os.unlink(filename)


@app.task(name='reports.generate')
def generate_report():
    logger.info('Check Reports at: {0}'.format(datetime.datetime.now()))
    templates = ready_to_execute()
    if templates:
        for template in templates:
            logger.info('Ready to execute: {0} at {1}'.format(
                template.name,
                datetime.datetime.now()
            ))
            template.execute()


def ready_to_execute():
    now = datetime.datetime.now()
    # Convert datetime.weekday() to the
    # same number scale as django lookup week_day.
    weekday_to_week_day = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
    wd = weekday_to_week_day[now.weekday()]
    q_list = [
        # Reports that execute on the hour.
        Q(frequency='h') &
        Q(start_date__lt=now) &
        Q(start_date__minute=now.minute),

        # Reports that execute daily.
        Q(frequency='d') &
        Q(start_date__lt=now) &
        (Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute)),

        # Reports that execute once a week.
        Q(frequency='w') &
        Q(start_date__lt=now) &
        (Q(start_date__week_day=wd) &
         Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute)),

        # Reports that execute once a month.
        Q(frequency='m') &
        Q(start_date__lt=now) &
        (Q(start_date__day=now.day) &
         Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute))
    ]

    queryset = ReportTemplate.objects.filter(
        reduce(operator.or_, q_list)
    )
    return queryset
