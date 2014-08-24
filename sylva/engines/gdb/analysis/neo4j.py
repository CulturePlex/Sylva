# -*- coding: utf-8 -*-
import json
import graphlab
import math
import networkx as nx
import os
import pandas as pd
import tempfile
import time

from datetime import datetime
from hashlib import sha1

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext as _

from analytics.models import Dump
from engines.gdb.analysis import (
    BaseAnalysis, LOAD_FILE, RUN_ALGOS, PROC_FINA
)
from graphs.models import Graph

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

    def get_dump(self, graph_id, subgraph=None):
        """
        Dump the content of the graph into an edgelist file
        """
        graph = Graph.objects.get(id=graph_id)
        lines = "src,dest\n"
        last_modified_relationships = graph.data.last_modified_relationships
        if last_modified_relationships is None:
            dumps = graph.dumps.all()
        else:
            dumps = graph.dumps.filter(
                creation_date__gte=graph.data.last_modified_relationships
            )
        # We get the lines, for the sha or for create the dump
        relationships = graph.relationships.all()
        if subgraph:
            # We treat the subgraph here. Subgraph is a list of ids
            for relationship in relationships:
                source_id = relationship.source.id
                target_id = relationship.target.id
                if source_id in subgraph and target_id in subgraph:
                    lines += "{0},{1}\n".format(source_id, target_id)
        else:
            for relationship in relationships:
                lines += "{0},{1}\n".format(relationship.source.id,
                                            relationship.target.id)
        # We get the latest dump or we create a new dump
        lines_hash = sha1(lines).hexdigest()
        existed_dumps = dumps.filter(data_hash=lines_hash)
        if dumps.count() == 0 or existed_dumps.count() == 0:
            # TODO: Write to a temp file instad of in memory
            timestamp = "{:.0f}".format(time.time() * 1000)
            dump_file_name = "{0}_dump_{1}.csv".format(graph.slug, timestamp)
            dump_file = SimpleUploadedFile(dump_file_name, lines,
                                           "text/csv")
            data_hash = sha1(lines).hexdigest()
            dump = Dump.objects.create(graph=graph,
                                       creation_date=datetime.now(),
                                       data_file=dump_file,
                                       data_hash=data_hash)
            dump.save()
        else:
            dump = existed_dumps.latest()
        return dump

    def run_connected_components(self, analytic):
        try:
            sf = graphlab.SFrame.read_csv(analytic.dump.get_data_file_path())
            g = graphlab.SGraph()
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
            g = graphlab.SGraph()
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
            g = graphlab.SGraph()
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
            g = graphlab.SGraph()
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
            g = graphlab.SGraph()
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
            g = graphlab.SGraph()
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
            bc = nx.betweenness_centrality(g).items()
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

    def _get_values_dict(self, values):
        values_dict = dict()
        for key, val in values.iteritems():
            if val in values_dict.keys():
                if key not in values_dict[val]:
                    values_dict[val].append(key)
            else:
                values_dict[val] = list()
                values_dict[val].append(key)
        return values_dict

    def save(self, results, analytic):
        result = ''
        algorithm = analytic.algorithm
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
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        if not isinstance(results, pd.DataFrame):
            results.rename({
                "__id": "node_id",
                result: algorithm,
            })
            results.save(temp_file.name, 'csv')
            freq_dist = results.to_dataframe()[algorithm].value_counts()
            # We treat the series to form the dictionary with the value as key
            # and the keys in a list of values
            values = results.to_dataframe()[algorithm]
            values_dict = self._get_values_dict(values)
            # SFrame saves the file and appends a .csv at the end :@
            temp_file_name = temp_file.name + '.csv'
        else:
            results.to_csv(temp_file.name,
                           index=False,
                           header=['node_id', algorithm])
            freq_dist = results[algorithm].value_counts()
            # We treat the series to form the dictionary with the value as key
            # and the keys in a list of values
            values = results[algorithm]
            values_dict = self._get_values_dict(values)
            temp_file_name = temp_file.name
        timestamp = "{:.0f}".format(time.time() * 1000)
        suf_name = "{0}_{1}_{2}".format(
            analytic.dump.graph.slug, analytic.algorithm, timestamp
        )
        suf_values_name = "{0}_{1}_values_{2}".format(
            analytic.dump.graph.slug, analytic.algorithm, timestamp
        )
        suf_raw = SimpleUploadedFile(
            "{0}.csv".format(suf_name),
            open(temp_file_name, 'r').read(),
            "text/csv"
        )
        analytic.raw = suf_raw
        suf_results = SimpleUploadedFile(
            "{0}.json".format(suf_name),
            freq_dist.to_json(),
            "application/json")
        analytic.results = suf_results
        suf_values = SimpleUploadedFile(
            "{0}.json".format(suf_values_name),
            json.dumps(values_dict),
            "application/json")
        analytic.values = suf_values
        analytic.save()
        # Remove the two temp files
        if temp_file_name != temp_file.name:
            os.unlink(temp_file_name)
        os.unlink(temp_file.name)
