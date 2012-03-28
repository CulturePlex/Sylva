# -*- coding: utf-8 -*-
import simplejson

from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_object_or_404, render_to_response,
                                HttpResponse)
from django.template import RequestContext
from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph

from converters import GEXFConverter


@login_required()
def graph_import_tool(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    # Schema jsonification
    schema = graph.schema.export()

    return render_to_response('graph_import_tool.html', {
                                "graph": graph,
                                "sylva_schema": simplejson.dumps(schema),
                            },
                            context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"))
def ajax_node_create(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.GET.copy()
    properties = simplejson.loads(data["properties"])
    label = graph.schema.nodetype_set.get(name=data["type"])
    node = graph.nodes.create(str(label.id), properties)
    return HttpResponse(simplejson.dumps({"id": node.id}))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"))
def ajax_relationship_create(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.GET.copy()
    source = graph.nodes.get(data["sourceId"])
    target = graph.nodes.get(data["targetId"])
    label = graph.schema.relationshiptype_set.get(name=data["type"],
            source=source.label,
            target=target.label)
    properties = data.get("properties", {})
    if properties:
        properties = simplejson.loads(properties)
    graph.relationships.create(source, target, str(label.id), properties)
    return HttpResponse(simplejson.dumps({}))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def graph_export_tool(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    converter = GEXFConverter(graph)
    response = HttpResponse(converter.stream_export(), mimetype='application/xml')
    response['Content-Disposition'] = \
            'attachment; filename=%s.gexf' % graph_name
    return response




