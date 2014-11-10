# -*- coding: utf-8 -*-
import datetime
import operator
from dateutil import tz, relativedelta
from django.db.models import Q
from models import ReportTemplate
from sylva.celery import app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(name='reports.generate')
def generate_report():
    logger.info('Check Reports {0}'.format(datetime.datetime.now()))
    templates = ready_to_execute()
    if templates:
        for template in templates:
            logger.info('Ready to execute: {0} at {1}'.format(
                template.name,
                datetime.datetime.now()
            ))
            template.execute()


def ready_to_execute():
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    future = now + relativedelta.relativedelta(minutes=+14)
    hour = relativedelta.relativedelta(hours=+1)
    day = relativedelta.relativedelta(days=+1)
    week = relativedelta.relativedelta(weeks=+1)
    month = relativedelta.relativedelta(months=+1)
    hour_range = [now - hour, future - hour]
    day_range = [now - day, future - day]
    week_range = [now - week, future - week]
    month_range = [now - month, future - month]
    print('day range: {0}'.format(day_range))
    q_list = [
        Q(frequency='h') &
        (Q(start_date__range=hour_range) |
         Q(last_run__range=hour_range)),
        Q(frequency='d') &
        (Q(start_date__range=day_range) |
         Q(last_run__range=day_range)),
        Q(frequency='w') &
        (Q(start_date__range=week_range) |
         Q(last_run__range=week_range)),
        Q(frequency='m') &
        (Q(start_date__range=month_range) |
        Q(last_run__range=month_range)),
    ]
    queryset = ReportTemplate.objects.filter(
        reduce(operator.or_, q_list)
    )
    return queryset