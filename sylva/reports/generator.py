import datetime
from models import ReportTemplate
from sylva.celery import app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(name='reports.generate')
def generate_report():
    logger.info('Check Reports {0}'.format(datetime.datetime.now()))
    templates = ReportTemplate.objects.all()
    for template in templates:
        if template.ready_to_execute():
            logger.info('Ready to execute: {0} at {1}'.format(
                template.name,
                datetime.datetime.now()
            ))
            template.execute()
