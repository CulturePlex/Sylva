# -*- coding: utf-8 -*-

# from django.conf import settings
# from subprocess import call
# import subprocess
from django.utils.translation import gettext as _
from engines.gdb.analysis import BaseAnalysis
import json

import graphlab
import networkx as nx


# app = Celery('tasks', backend='amqp', broker='amqp://')
# We gonna use graphlab for python
# analyticsEngine = settings.BACKEND_ANALYTICS["graphchi"]
# analyticsEngine = settings.BACKEND_ANALYTICS["graphlab"]


PROC_INIT = 0
LOAD_FILE = 1
RUN_ALGOS = 2
PROC_FINA = 3


class Analysis(BaseAnalysis):

    def list_algorithms(self):
        return {'connected_components': _("Connected components"),
                'graph_coloring': _("Graph coloring"),
                'kcore': _("Kcore"),
                'pagerank': _("Pagerank"),
                'triangle_counting': _("Triangle counting"),
                'betweenness_centrality': _("Betweenness centrality")}

    def dump(self, analytic):
        """
        This is a example function that prints
        the edgelist of the relationships of a graph
        """
        graph = analytic.graph
        f = open(analytic.dump, "w+")
        line = "src,dest\n"
        f.write(line)
        if analytic.affected_nodes:
            array_id = json.loads(analytic.affected_nodes)
            for relationship in graph.relationships.all():
                source_id = relationship.source.id
                target_id = relationship.target.id
                if (source_id in array_id) and (target_id in array_id):
                    line = "{0},{1}\n".format(relationship.source.id,
                                              relationship.target.id)
                    f.write(line)
        else:
            for relationship in graph.relationships.all():
                line = "{0},{1}\n".format(relationship.source.id,
                                          relationship.target.id)
                f.write(line)
        f.close()

    def connected_components(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            cc = graphlab.connected_components.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return cc.get('componentid')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def graph_coloring(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            gc = graphlab.graph_coloring.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return gc.get('colorid')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def kcore(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            kc = graphlab.kcore.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return kc.get('coreid')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def pagerank(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            pr = graphlab.pagerank.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return pr.get('pagerank')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def shortest_path(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            sp = graphlab.shortest_path.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return sp.get('distance')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def triangle_counting(self, analytic):
        try:
            sf = graphlab.SFrame(analytic.dump)
            g = graphlab.Graph()
            g = g.add_edges(sf, 'src', 'dest')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            tc = graphlab.triangle_counting.create(g)
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return tc.get('triangle_count')
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def betweenness_centrality(self, analytic):
        try:
            g = nx.read_edgelist(analytic.dump, delimiter=',')
        except Exception as e:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            bc = nx.betweenness_centrality(g).items()
        except Exception as e:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return bc
        except Exception as e:
            raise Exception(PROC_FINA, "Error finishing the task")

    def save(self, results, analytic):
        # this branch is for the betweenness centrality algorithm
        if type(results) == list:
            f = open(analytic.results + '.csv', 'w')
            elem = '"{0}",{1}\n'.format("__id", "betweenness_centrality")
            f.write(elem)
            for key, value in results:
                # this is to avoid the first attributes of the columns
                if key is not "src" or "dest":
                    elem = '"{0}",{1}\n'.format(key, value)
                    f.write(elem)
        else:
            results.save(analytic.results, 'csv')
