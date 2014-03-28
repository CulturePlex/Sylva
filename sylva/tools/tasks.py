from celery import task
from celery.task import Task
from subprocess import call

folder = "/home/gabi/Desktop/sylvaAnalytics"


class ExportGraphTask(Task):
    """
    A task that export a whole Sylva graph
    """
    def run(self, graph_id, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running export graph task")

        # TODO Code creating the file

        return True


class GraphChiAnalyticsMethods():
    """
    A class that include graphchi analytics methods
    All the examples that we make are with the community
    detection method
    """

    """
    Example task to check the behaviour of celery
    """
    @task(name="tasks.example")
    def celery_example_task():
        result = "it works"
        return result

    """
    Task to run the community detection algorithm
    """
    @task(name="tasks.graphchi_communitydetection")
    def graphchi_communitydetection_task():
        # We should define GRAPHCHI_ROOT
        call(["/home/gabi/Desktop/graphchi/bin/example_apps/communitydetection", "file", folder + "/pays/pays.csv"])
        f = open(folder + '/pays/pays.csv.components', 'r+')
        result = f.read()
        f.close()
        return result

    """
    Task to run the connected components algorithm
    """
    @task(name="tasks.graphchi_connectedcomponents")
    def graphchi_connectedcomponents_task():
        # We should define GRAPHCHI_ROOT
        call(["/home/gabi/Desktop/graphchi/bin/example_apps/connectedcomponents", "file", folder + "/pays/pays.csv"])
        f = open('/home/gabi/Desktop/Dataset-graphchi/edgelist.txt.components', 'r+')
        result = f.read()
        f.close()
        return result

    """
    Task to run the minimun spanning forest algorithm
    """
    @task(name="tasks.graphchi_minimuspanningforest")
    def graphchi_minimunspanningforest_task():
        # We should define GRAPHCHI_ROOT
        call(["/home/gabi/Desktop/graphchi/bin/example_apps/minimunspanningforest", "file", folder + "/pays/pays.csv"])
        f = open('/home/gabi/Desktop/Dataset-graphchi/edgelist.txt.components', 'r+')
        result = f.read()
        f.close()
        return result

    """
    Task to run the pagerank algorithm
    """
    @task(name="tasks.graphchi_pagerank")
    def graphchi_pagerank_task():
        # We should define GRAPHCHI_ROOT
        call(["/home/gabi/Desktop/graphchi/bin/example_apps/pagerank", "file", folder + "/pays/pays.csv"])
        f = open('/home/gabi/Desktop/Dataset-graphchi/edgelist.txt.4B.vout', 'r+')
        result = f.read()
        f.close()
        return result

    """
    Task to run the triangle counting algorithm
    """
    @task(name="tasks.graphchi_trianglecounting")
    def graphchi_trianglecounting_task():
        # We should define GRAPHCHI_ROOT
        call(["/home/gabi/Desktop/graphchi/bin/example_apps/trianglecounting", "file", folder + "/pays/pays.csv"])
        f = open('/home/gabi/Desktop/Dataset-graphchi/edgelist.txt.components', 'r+')
        result = f.read()
        f.close()
        return result
