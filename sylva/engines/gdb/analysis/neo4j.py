# -*- coding: utf-8 -*-

from django.conf import settings
from celery import Celery
from engines.gdb.analysis import BaseAnalysis
from datetime import datetime
#from subprocess import call
import subprocess
import json


app = Celery('tasks', backend='amqp', broker='amqp://')
# analyticsEngine = settings.BACKEND_ANALYTICS["graphchi"]
analyticsEngine = settings.BACKEND_ANALYTICS["graphlab"]


PROC_INIT = 0
RUN_ALGOS = 1
PROC_FINA = 2


class Analysis(BaseAnalysis):

    @app.task(name="tasks.pagerank")
    def pagerank(graph, analytic):
        #call([PAGERANK_URL, "file", "dump_files/file.txt"])
        url_dump = "../dump_files/" + graph.slug + ".txt"
        url_result = "../results_files/" + graph.slug + "-pagerank.txt"
        proc = subprocess.Popen(analyticsEngine["pagerank"] + " file " + url_dump + " edgelist", shell=True, stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        f = open(url_result, "w+")
        f.write(output)
        f.close()

    @app.task(name="tasks.pagerankAux")
    def pagerankAux(graph, analytic):
        url_dump = "../dump_files/" + graph.slug + ".txt"
        url_result = "../results_files/" + graph.slug + "-pagerank.txt"
        try:
            try:
                analytic.task_status = "Starting"
                analytic.task_start = datetime.now()
                # analytic.dump = url_dump
                # analytic.results = url_result
                analytic.save()
            except Exception as e:
                raise Exception(PROC_INIT, "Error starting the task")
            try:
                proc = subprocess.Popen(analyticsEngine["pagerank"] + " --graph " + url_dump + " --format tsv " + "--saveprefix " + url_result, shell=True, stdout=subprocess.PIPE, )
            except Exception as e:
                raise Exception(RUN_ALGOS, "Error executing the task")
            try:
                analytic.task_status = "Ready"
                analytic.task_end = datetime.now()
                output = proc.communicate()[0]
            except Exception as e:
                raise Exception(PROC_FINA, "Error finishing the task")
        except Exception as e:
            analytic.task_status = "Failed"
            if e.args[0] == PROC_INIT:
                analytic.task_error = \
                    'Process could not be initialized: ' + e.args[1]
            elif e.args[0] == RUN_ALGOS:
                analytic.task_error = \
                    'Algorithm could not be processed: ' + e.args[1]
            elif e.args[0] == PROC_FINA:
                analytic.task_error = \
                    'File system could not be created: ' + e.args[1]
            else:
                analytic.task_error = \
                    'Unknown error: ' + e.args[0]
        finally:
            analytic.save()
        return output

    @app.task(name="tasks.connectedComponents")
    def connected_components(graph, analytic):
        #call([PAGERANK_URL, "file", "dump_files/file.txt"])
        url_dump = "../dump_files/" + graph.slug + ".txt"
        url_result = "../results_files/" + graph.slug + "-connectedcomponents.txt"
        proc = subprocess.Popen(analyticsEngine["connectedComponents"] + " file " + url_dump + " edgelist", shell=True, stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        f = open(url_result, "w+")
        f.write(output)
        f.close()

    @app.task(name="tasks.dump")
    def dump(graph, analytic):
        """
        This is a example function that prints
        the edgelist of the relationships of a graph
        """
        url_file = "../dump_files/" + graph.slug + ".txt"
        f = open(url_file, "w+")
        if analytic.affected_nodes:
            arrayId = json.loads(analytic.affected_nodes)
            for relationship in graph.relationships.all():
                sourceId = relationship.source.id
                targetId = relationship.target.id
                if (sourceId in arrayId) and (targetId in arrayId):
                    line = "{0}  {1}\n".format(relationship.source.id, relationship.target.id)
                    f.write(line)
        else:
            for relationship in graph.relationships.all():
                line = "{0}  {1}\n".format(relationship.source.id, relationship.target.id)
                f.write(line)
        f.close()
