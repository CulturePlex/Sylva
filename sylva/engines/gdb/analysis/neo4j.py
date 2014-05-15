# -*- coding: utf-8 -*-

# from django.conf import settings
# from subprocess import call
# import subprocess
from django.utils.translation import gettext as _
from engines.gdb.analysis import BaseAnalysis
import json
from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
import graphlab
import networkx as nx
import pandas as pd

from analytics.models import DataDump

# app = Celery('tasks', backend='amqp', broker='amqp://')
# We gonna use graphlab for python
# analyticsEngine = settings.BACKEND_ANALYTICS["graphchi"]
# analyticsEngine = settings.BACKEND_ANALYTICS["graphlab"]


PROC_INIT = 0
LOAD_FILE = 1
RUN_ALGOS = 2
PROC_FINA = 3

INST_TIME = 1e-04


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
        line = "src,dest\n"
        if analytic.subgraph:
            array_id = json.loads(analytic.subgraph)
            for relationship in graph.relationships.all():
                source_id = relationship.source.id
                target_id = relationship.target.id
                if (source_id in array_id) and (target_id in array_id):
                    line += "{0},{1}\n".format(relationship.source.id,
                                               relationship.target.id)
        else:
            for relationship in graph.relationships.all():
                line += "{0},{1}\n".format(relationship.source.id,
                                           relationship.target.id)
                print line
        dump_file = SimpleUploadedFile('dump.csv', line,
                                       "text/csv")
        dump = DataDump.objects.create(creation_date=datetime.now(),
                                       data_file=dump_file)
        analytic.dump = dump
        analytic.save()

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

    def connected_components_eta(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

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

    def graph_coloring_eta(self, graph):
        nodes = graph.nodes.count()

        result = (2 * nodes) * INST_TIME

        if result < 1:
            result += 1

        return result

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

    def kcore_eta(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

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

    def pagerank_eta(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

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

    # def shortest_path_eta(self, graph):
        # TODO

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

    def triangle_counting_eta(self, graph):
        nodes = graph.nodes.count()
        exp = 3/float(2)

        result = (nodes ** exp) * INST_TIME

        if result < 1:
            result += 1

        return result

    def betweenness_centrality(self, analytic):
        try:
            g = nx.read_edgelist(analytic.dump, delimiter=',')
        except Exception:
            raise Exception(LOAD_FILE, "Error loading the file")
        try:
            bc = nx.betweenness_centrality(g).items()[2:]
            bc = pd.DataFrame(bc, columns=['__id',
                                           'betweenness_centrality'])
        except Exception:
            raise Exception(RUN_ALGOS, "Error executing the task")
        try:
            return bc
        except Exception as e:
            raise Exception(PROC_FINA,
                            "Error finishing the task: " % str(e))

    def betweenness_centrality_eta(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes * rels) * INST_TIME

        if result < 1:
            result += 1

        return result

    def save(self, results, analytic):
        result = ''
        algorithm = analytic.algorithm
        suf_raw = SimpleUploadedFile(analytic.algorithm + '.csv', "",
                                     "text/csv")
        analytic.raw = suf_raw
        analytic.save()
        if algorithm == 'pagerank':
            result = 'pagerank'
        elif algorithm == 'connected_components':
            result = 'componentid'
        elif algorithm == 'graph_coloring':
            result = 'colorid'
        elif algorithm == 'kcore':
            result = 'coreid'
        elif algorithm == 'shortest_path':
            result = 'distance'
        elif algorithm == 'triangle_counting':
            result = 'triangle_count'
        elif algorithm == 'betweenness_centrality':
            result = 'betweenness_centrality'
        if not isinstance(results, pd.DataFrame):
            results.rename({
                "__id": "node_id",
                result: algorithm,
            })
            results.save(analytic.raw.path, 'csv')
        else:
            results.to_csv(analytic.raw.path,
                           index=False,
                           header=['node_id', algorithm])
        dt_results = pd.read_csv(analytic.raw.path)
        freq_dist = dt_results[algorithm].value_counts()
        suf_results = SimpleUploadedFile(
            analytic.algorithm + '.json',
            freq_dist.to_json(),
            "application/json")
        analytic.results = suf_results
        analytic.save()
