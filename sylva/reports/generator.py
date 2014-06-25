from sylva.celery import app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(bind=True, name='reports.generate')
def generate_report(self):
    return 'generate report'
