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


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def map_view(request, graph_slug, node_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    is_graph_empty = graph.is_empty()
    is_schema_empty = graph.schema.is_empty()
    nodes = graph.nodes.all()
    nodes_json = []
    for n in nodes:
        nodes_json.append(n.to_json())
    return render_to_response('maps_view.html',
                              {"graph": graph,
                               "is_graph_empty": is_graph_empty,
                               "is_schema_empty": is_schema_empty,
                               "nodes": json.dumps(nodes_json)},
                              context_instance=RequestContext(request))
