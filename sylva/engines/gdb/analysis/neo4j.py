# -*- coding: utf-8 -*-
import graphlab
import math
import networkx as nx
import os
import pandas as pd
import tempfile

from datetime import datetime
from hashlib import sha1

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext as _

from engines.gdb.analysis import (
    BaseAnalysis, LOAD_FILE, RUN_ALGOS, PROC_FINA
)
from analytics.models import Dump

INST_TIME = 1e-04

if (hasattr(settings, "AWS_ACCESS_KEY_ID")
        and hasattr(settings, "AWS_SECRET_ACCESS_KEY")):
    graphlab.aws.set_credentials(
        settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY
    )


class Analysis(BaseAnalysis):

    def get_algorithms(self):
        """
        Returns the list of available algorithms with labels
        """
        return {'connected_components': _("Connected components"),
                'graph_coloring': _("Graph coloring"),
                'kcore': _("Degeneracy (k-core)"),
                'pagerank': _("Pagerank"),
                'triangle_counting': _("Triangle counting"),
                'betweenness_centrality': _("Betweenness centrality")}

    def get_dump(self, graph):
        """
        Dump the content of the graph into an edgelist file
        """
        lines = "src,dest\n"
        last_modified_relationships = graph.data.last_modified_relationships
        if last_modified_relationships is None:
            dumps = graph.dumps.all()
        else:
            dumps = graph.dumps.filter(
                creation_date__gte=graph.data.last_modified_relationships
            )
        if dumps.count() == 0:
            for relationship in graph.relationships.all():
                lines += "{0},{1}\n".format(relationship.source.id,
                                            relationship.target.id)
            dump_file = SimpleUploadedFile('dump.csv', lines,
                                           "text/csv")
            data_hash = sha1(lines).hexdigest()
            dump = Dump.objects.create(graph=graph,
                                       creation_date=datetime.now(),
                                       data_file=dump_file,
                                       data_hash=data_hash)
            dump.save()
        else:
            dump = dumps.latest()
        return dump

    def run_connected_components(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_connected_components(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

    def run_graph_coloring(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_graph_coloring(self, graph):
        nodes = graph.nodes.count()

        result = (2 * nodes) * INST_TIME

        if result < 1:
            result += 1

        return result

    def run_kcore(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_kcore(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

    def run_pagerank(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_pagerank(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()

        result = (nodes + rels) * INST_TIME

        if result < 1:
            result += 1

        return result

    def run_shortest_path(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_shortest_path(self, graph):
        # Min priority-queue: |E| + |V|log(|V|)
        nodes = graph.nodes.count()
        rels = graph.relationships.count()
        result = nodes + (rels * math.log(rels))
        if result < 1:
            result += 1
        return result

    def run_triangle_counting(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
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
            raise Exception(PROC_FINA, "Error finishing the task: " + str(e))

    def estimate_triangle_counting(self, graph):
        nodes = graph.nodes.count()
        exp = 3.0 / 2.0
        result = (nodes ** exp) * INST_TIME
        if result < 1:
            result += 1
        return result

    def run_betweenness_centrality(self, analytic):
        try:
            dump_df = pd.read_csv(analytic.dump.get_data_file_path(),
                                  delimiter=",")
            g = nx.DiGraph()
            for row in dump_df.iterrows():
                g.add_edge(*row[1].values)
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

    def estimate_betweenness_centrality(self, graph):
        nodes = graph.nodes.count()
        rels = graph.relationships.count()
        result = (nodes * rels) * INST_TIME
        if result < 1:
            result += 1
        return result

    def save(self, results, analytic):
        result = ''
        algorithm = analytic.algorithm
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
        raw_file = tempfile.NamedTemporaryFile(delete=False)
        raw_file.close()
        if not isinstance(results, pd.DataFrame):
            results.rename({
                "__id": "node_id",
                result: algorithm,
            })
            results.save(raw_file.name, 'csv')
            # SFrame saves the file and appends a .csv at the end :@
            raw_file_name = raw_file.name + '.csv'
        else:
            results.to_csv(raw_file.name,
                           index=False,
                           header=['node_id', algorithm])
            raw_file_name = raw_file.name
        suf_raw = SimpleUploadedFile(
            analytic.algorithm + '.csv',
            open(raw_file_name, 'r').read(),
            "text/csv"
        )
        analytic.raw = suf_raw
        # We load the file again because SFrame does not have value_counts
        dt_results = pd.read_csv(raw_file_name)
        freq_dist = dt_results[algorithm].value_counts()
        suf_results = SimpleUploadedFile(
            analytic.algorithm + '.json',
            freq_dist.to_json(),
            "application/json")
        analytic.results = suf_results
        analytic.save()
        os.unlink(raw_file)
