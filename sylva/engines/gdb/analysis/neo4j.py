# -*- coding: utf-8 -*-

from django.conf import settings
from celery import Celery
from engines.gdb.analysis import BaseAnalysis
#from subprocess import call
import subprocess
import datetime
import json


app = Celery('tasks', backend='amqp', broker='amqp://')
analyticsEngine = settings.BACKEND_ANALYTICS["graphchi"]


class Analysis(BaseAnalysis):

    @app.task(name="tasks.pagerank")
    def pagerank(graph, analytic):
        #call([PAGERANK_URL, "file", "dump_files/file.txt"])
        analytic.task_start = datetime.datetime.now()
        url_dump = "dump_files/" + graph.slug + ".txt"
        url_result = "results_files/" + graph.slug + "-pagerank.txt"
        proc = subprocess.Popen(analyticsEngine["pagerank"] + " file " + url_dump + " edgelist", shell=True, stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        f = open(url_result, "w+")
        f.write(output)
        f.close()

    @app.task(name="tasks.connectedComponents")
    def connected_components(graph, analytic):
        #call([PAGERANK_URL, "file", "dump_files/file.txt"])
        analytic.task_start = datetime.datetime.now()
        url_dump = "dump_files/" + graph.slug + ".txt"
        url_result = "results_files/" + graph.slug + "-connectedcomponents.txt"
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
        analytic.task_start = datetime.datetime.now()
        url_file = "dump_files/" + graph.slug + ".txt"
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
