# -*- coding: utf-8 -*-
from celery import Celery
import datetime

app = Celery('tasks', backend='amqp', broker='amqp://')

PROC_INIT = 0
LOAD_FILE = 1
RUN_ALGOS = 2
PROC_FINA = 3


class BaseAnalysis(object):
    """
    Base class for Analytics with the common API to implement.
    """

    def dump(graph, analytic):
        """
        Dump the content of the graph into an edgelist file
        """
        raise NotImplementedError("Method has to be implemented")

    def connected_components(graph, analytic):
        """
        Connected components method
        """
        raise NotImplementedError("Method has to be implemented")

    def graph_coloring(graph, analytic):
        """
        graph coloring method
        """
        raise NotImplementedError("Method has to be implemented")

    def kcore(graph, analytic):
        """
        kcore method
        """
        raise NotImplementedError("Method has to be implemented")

    def pagerank(graph, analytic):
        """
        Pagerank method
        """
        raise NotImplementedError("Method has to be implemented")

    def shortest_path(graph, analytic):
        """
        Shortest path method
        """
        raise NotImplementedError("Method has to be implemented")

    def triangle_counting(graph, analytic):
        """
        Triangle counting method
        """
        raise NotImplementedError("Method has to be implemented")

    def betweenness_centrality(graph, analytic):
        """
        Betweenness centrality method
        """
        raise NotImplementedError("Method has to be implemented")

    @app.task(bind=True, name="tasks.analytic")
    def run_algorithm(self, analytic, analysis):
        # graph = analytic.graph
        algorithm = analytic.algorithm
        analytic.task_id = self.request.id
        # url_dump = "../dump_files/" + graph.slug + ".csv"
        try:
            try:
                analytic.task_status = "Starting"
                analytic.task_start = datetime.datetime.now()
                dump = getattr(analysis, 'dump')
                dump(analytic)
                # analytic.results = url_result
            except Exception as e:
                raise Exception(PROC_INIT, "Error starting the task")
            algorithm_func = getattr(analysis, algorithm)
            results = algorithm_func(analytic)
            if algorithm is not 'dump':
                analysis.save(results, analytic)
            analytic.task_status = "Ready"
            analytic.task_end = datetime.datetime.now()
        except Exception as e:
            analytic.task_status = "Failed"
            if e.args[0] == PROC_INIT:
                analytic.task_error = \
                    'Process could not be initialized: ' + e.args[1]
            elif e.args[0] == LOAD_FILE:
                analytic.task_error = \
                    'File could not be loaded: ' + e.args[1]
            elif e.args[0] == RUN_ALGOS:
                analytic.task_error = \
                    'Algorithm could not be processed: ' + e.args[1]
            elif e.args[0] == PROC_FINA:
                analytic.task_error = \
                    'File system could not be created: ' + e.args[1]
            else:
                analytic.task_error = \
                    'Unknown error: ' + str(e.args[0])
        finally:
            analytic.save()
            print analytic.task_error
        return analytic.task_status

    @app.task(bind=True, name="tasks.estimated_time")
    def run_estimated_time(self, analysis, graph, algorithm):
        eta_func = getattr(analysis, algorithm + '_eta')
        result = eta_func(graph)

        return result
