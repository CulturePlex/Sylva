# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import (get_object_or_404, render_to_response)
from django.template import RequestContext

from guardian.decorators import permission_required

from graphs.models import Graph
from graphs.views import _jsonify_graph


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def map_view(request, graph_slug, node_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    is_schema_empty = graph.schema.is_empty()
    is_graph_empty = graph.is_empty()
    '''
    nodes = graph.nodes.all()
    nodes_json = []
    for n in nodes:
        nodes_json.append(n.to_json())
    '''
    nodes_list = graph.nodes.all()
    relations_list = graph.relationships.all()
    graph_json, nodetypes, reltypes, node_ids = _jsonify_graph(
        graph, nodes_list, relations_list)
    size = len(nodes_list)
    graph_json_data = {
        'graph': graph_json,
        'nodetypes': nodetypes,
        'reltypes': reltypes,
        'nodeIds': node_ids,
        'size': size
    }
    return render_to_response('maps_view.html',
                              {"graph": graph,
                               "is_schema_empty": is_schema_empty,
                               "is_graph_empty": is_graph_empty,
                               "graph_json": json.dumps(graph_json_data)},
                              context_instance=RequestContext(request))
