# -*- coding: utf-8 -*-
import datetime
import operator
from django.db.models import Q
from models import ReportTemplate
from sylva.celery import app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


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
        (Q(start_date__minute=now.minute) |
         Q(last_run__minute=now.minute)),

        # Reports that execute daily.
        Q(frequency='d') &
        Q(start_date__lt=now) &
        (Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute)) |
        (Q(last_run__hour=now.hour) &
         Q(last_run__minute=now.minute)),

        # Reports that execute once a week.
        Q(frequency='w') &
        Q(start_date__lt=now) &
        (Q(start_date__week_day=wd) &
         Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute)) |
        (Q(last_run__week_day=wd) &
         Q(last_run__hour=now.hour) &
         Q(last_run__minute=now.minute)),

        # Reports that execute once a month.
        Q(frequency='m') &
        Q(start_date__lt=now) &
        (Q(start_date__day=now.day) &
         Q(start_date__hour=now.hour) &
         Q(start_date__minute=now.minute)) |
        (Q(last_run__day=now.day) &
         Q(last_run__hour=now.hour) &
         Q(last_run__minute=now.minute))
    ]

    queryset = ReportTemplate.objects.filter(
        reduce(operator.or_, q_list)
    )
    return queryset
