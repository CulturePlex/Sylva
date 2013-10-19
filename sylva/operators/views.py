# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse)

from guardian.decorators import permission_required

from base.decorators import is_enabled
from graphs.models import Data, Graph
from operators.grammar import QueryParser
from schemas.models import NodeType, RelationshipType

# from .parser import parse_query


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def operator_builder(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(schema__graph__slug=graph_slug)
    return render_to_response('operators/operator_builder.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def operator_query(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    return render_to_response('operators/operator_query.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def operator_query_results(request, graph_slug):
    query = request.POST.get("query", "").strip()
    if request.is_ajax() and query:
        graph = get_object_or_404(Graph, slug=graph_slug)
        query_parser = QueryParser(graph)
        # query = "notas of autor with notas that start with lista"
        query_dict = query_parser.parse(unicode(query))
        results = graph.query(query_dict)
        # TODO: Try to make the response streamed
        return HttpResponse(json.dumps([r for r in results]),
                            status=200,
                            mimetype='application/json')
    return HttpResponse(json.dumps(None),
                        status=400,  # Bad request
                        mimetype='application/json')
