# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from guardian.decorators import permission_required

from base.decorators import is_enabled

from graphs.models import Graph
from schemas.models import NodeType, RelationshipType


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
    return render_to_response('operators/graph_query.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))
