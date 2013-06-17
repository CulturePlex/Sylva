# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse, redirect)
from django.utils.translation import gettext as _
from django.template import RequestContext

from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph

from converters import GEXFConverter


@login_required()
def graph_import_tool(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if graph.schema.is_empty():
        messages.error(request, _("You are trying to import data into a "
                                  "graph with an empty schema"))
        return redirect(reverse('dashboard'))
    if not graph.is_empty():
        messages.error(request, _("You are trying to import data into a "
                                  "not empty graph"))
        return redirect(reverse('dashboard'))
    schema = graph.schema.export()  # Schema jsonification
    return render_to_response('graph_import_tool.html',
                              {"graph": graph,
                               "sylva_schema": simplejson.dumps(schema)},
                              context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def ajax_node_create(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.POST.copy()
    properties = simplejson.loads(data["properties"])
    label = graph.schema.nodetype_set.get(name=data["type"])
    node = graph.nodes.create(str(label.id), properties)
    return HttpResponse(simplejson.dumps({"id": node.id}))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def ajax_relationship_create(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.POST.copy()
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


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_tool(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if graph.is_empty():
        messages.error(request, _("You are trying to export data from an "
                                  "empty graph"))
        return redirect(reverse('dashboard'))
    converter = GEXFConverter(graph)
    response = HttpResponse(converter.stream_export(),
                            mimetype='application/xml')
    attachment = 'attachment; filename=%s.gexf' % graph_slug.replace("-", "_")
    response['Content-Disposition'] = attachment
    return response
