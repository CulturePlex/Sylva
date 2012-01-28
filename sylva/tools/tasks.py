from datetime import date, timedelta
from celery.task import Task


class ExportGraphTask(Task):
    """
    A task that export a whole Sylva graph
    """
    def run(self, graph_id, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running export graph task")

        # TODO Code creating the file

        return True
