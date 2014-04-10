# -*- coding: utf-8 -*-

from celery import Celery
from engines.gdb.analysis import BaseAnalysis
from subprocess import call


app = Celery('tasks', backend='amqp', broker='amqp://')

GRAPHCHI_FOLDER = "../../graphchi/bin/example_apps"
PAGERANK_URL = "../.././graphchi/bin/example_apps/pagerank"


class Analysis(BaseAnalysis):

    @app.task(name="tasks.pagerank")
    def pagerank(graph, analytic):
        result = "it works"
        print analytic.algorithm
        print graph.gdb
        call([PAGERANK_URL, "file", "dump_files/file.txt"])
        return result

    @app.task(name="tasks.dump_graphchi_edgelist")
    def dump_graphchi_edgelist(graph, analytic):
        """
        This is a example function that prints
        the edgelist of the relationships of a graph
        """
        f = open("dump_files/file.txt", "w+")
        for relationship in graph.relationships.all():
            line = "{0}  {1}\n".format(relationship.source.id, relationship.target.id)
            f.write(line)
        f.close()
