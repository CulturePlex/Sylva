# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.db.models import Q
from django.contrib.auth.models import User
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
        # see https://gist.github.com/versae/9241069
        query_dict = query_parser.parse(unicode(query))
        results = graph.query(query_dict)
        # TODO: Try to make the response streamed
        return HttpResponse(json.dumps([r for r in results]),
                            status=200,
                            mimetype='application/json')
    return HttpResponse(json.dumps(None),
                        status=400,  # Bad request
                        mimetype='application/json')


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_query_collaborators(request, graph_slug):
    if request.is_ajax() and "term" in request.GET:
        graph = get_object_or_404(Graph, slug=graph_slug)
        term = request.GET["term"]
        if graph and term:
            collabs = graph.get_collaborators(include_anonymous=True,
                                              as_queryset=True)
            collabs_dict = {}
            for collab in collabs:
                full_name = collab.get_full_name()
                if full_name:
                    name = u"%s (%s)" % (full_name, collab.username)
                else:
                    name = collab.username
                    collabs_dict[collab.id] = name
            return HttpResponse(json.dumps(collabs_dict))
    return HttpResponse(json.dumps({}))
