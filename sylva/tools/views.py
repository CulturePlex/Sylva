# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse, redirect)
from django.http import Http404
from django.utils.translation import gettext as _
from django.template import RequestContext

from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph

from converters import GEXFConverter, CSVConverter


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
                               "sylva_schema": json.dumps(schema),
                               "IMPORT_MAX_SIZE": settings.IMPORT_MAX_SIZE},
                              context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def ajax_nodes_create(request, graph_slug):
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        elements = json.loads(request.POST['data'])
        ids_dict = {}
        for elem in elements:
            elem_data = elem['data']
            elem_id = elem['id']
            label = graph.schema.nodetype_set.get(name=elem_data['type'])
            properties = elem_data.get('properties', '{}')
            node = graph.nodes.create(str(label.id), properties)
            ids_dict[elem_id] = node.id
        return HttpResponse(json.dumps(ids_dict), mimetype='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX request)"))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def ajax_relationships_create(request, graph_slug):
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        elements = json.loads(request.POST["data"])
        for elem in elements:
            source = graph.nodes.get(elem["sourceId"])
            target = graph.nodes.get(elem["targetId"])
            label = graph.schema.relationshiptype_set.get(name=elem["type"],
                                                          source=source.label,
                                                          target=target.label)
            properties = elem.get("properties", "{}")
            graph.relationships.create(source, target, str(label.id), properties)
        return HttpResponse(json.dumps({}), mimetype='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX request)"))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_gexf(request, graph_slug):
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


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_csv(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    converter = CSVConverter(graph)
    zip_data, zip_name = converter.export()
    response = HttpResponse(zip_data, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
    return response
