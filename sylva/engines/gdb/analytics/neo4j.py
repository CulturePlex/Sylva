# -*- coding: utf-8 -*-

from celery import Celery
from engines.gdb.analytics import BaseAnalytics

app = Celery('tasks', backend='amqp', broker='amqp://')


class Analytics(BaseAnalytics):

    @app.task(name="tasks.pagerank")
    def pagerank(graph, analytic):
        result = "it works"
        print analytic.algorithm
        print graph.gdb
        return result

    @app.task(name="tasks.dump_graphchi_edgelist")
    def dump_graphchi_edgelist(graph):
        """
        This is a example function that prints
        the edgelist of the relationships of a graph
        """
        f = open("./dump_files/file.txt", "r+")
        for relationship in graph.relationships.all():
            line = "{0}  {1}".format(relationship.source.id, relationship.target.id)
            f.write(line)
        f.close()
