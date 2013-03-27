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

from graphs.models import Graph
from schemas.models import NodeType, RelationshipType

from .parser import parse_query


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Graph, "slug", "graph_slug"),
                     return_403=True)
def operator_query(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(schema__graph__slug=graph_slug)
    return render_to_response('operators/operator_query.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_query(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node_types = graph.schema.nodetype_set.all()
    rel_types = graph.schema.relationshiptype_set.all()
    node_type_names = [nt.name for nt in node_types]
    rel_type_names = [rt.name for rt in rel_types]
    node_properties = []
    for node_type in node_types:
        for node_prop in node_type.properties.all():
            node_properties.append({
                'value': node_prop.key,
                'label': '(' + node_type.name + ') ' + node_prop.key
            })
    return render_to_response('operators/graph_query.html',
                              {"graph": graph,
                               "node_types": json.dumps(node_type_names),
                               "relationship_types": json.dumps(rel_type_names),
                               "node_properties": json.dumps(node_properties)},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
def process_ajax_query(request):
    if request.is_ajax() and request.method == 'POST':
        query = request.POST.get('query')
        data = parse_query(query)
        return HttpResponse(json.dumps(data),
                            status=200,
                            mimetype='application/json')
