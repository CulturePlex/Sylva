# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse, redirect)
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views.decorators.http import condition

from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph
from graphs.utils import graph_last_modified
from schemas.models import NodeType
from tools.converters import (GEXFConverter, CSVConverter, CSVQueryConverter,
                              CSVTableConverter)


@login_required()
def graph_import_tool(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    as_modal = bool(request.GET.get("asModal", False))
    if graph.schema.is_empty():
        messages.error(request, _("You are trying to import data into a "
                                  "graph with an empty schema"))
        return redirect(reverse('dashboard'))
    if not graph.is_empty():
        messages.error(request, _("You are trying to import data into a "
                                  "not empty graph"))
        return redirect(reverse('dashboard'))
    schema = graph.schema.export()  # Schema jsonification
    if as_modal:
        base_template = 'empty.html'
        render = render_to_string
    else:
        base_template = 'base.html'
        render = render_to_response
    broader_context = {"graph": graph,
                       "sylva_schema": json.dumps(schema),
                       "IMPORT_MAX_SIZE": settings.IMPORT_MAX_SIZE,
                       "base_template": base_template,
                       "as_modal": as_modal}
    response = render('graph_import_tool.html', broader_context,
                      context_instance=RequestContext(request))
    if as_modal:
        response = {'type': 'html',
                    'action': 'import_graph',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


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
        graph.last_modified = datetime.now()
        graph.data.save()
        return HttpResponse(json.dumps(ids_dict),
                            content_type='application/json')
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
            graph.relationships.create(source, target, str(label.id),
                                       properties)
        graph.last_modified = datetime.now()
        graph.data.save()
        return HttpResponse(json.dumps({}), content_type='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX request)"))


@condition(last_modified_func=graph_last_modified)
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_gexf(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if graph.is_empty():
        messages.error(request, _("You are trying to export data from an "
                                  "empty graph"))
        return redirect(reverse('dashboard'))
    converter = GEXFConverter(graph=graph)
    response = HttpResponse(converter.stream_export(),
                            content_type='application/xml')
    attachment = ('attachment; filename=%s_data.gexf' % graph_slug)
    response['Content-Disposition'] = attachment
    return response


@condition(last_modified_func=graph_last_modified)
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_csv(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    converter = CSVConverter(graph=graph)
    zip_data, zip_name = converter.export()
    response = HttpResponse(zip_data, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
    return response


@condition(last_modified_func=graph_last_modified)
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_table_csv(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node_type_id = request.session.get('node_type_id', None)
    node_type = get_object_or_404(NodeType, id=node_type_id)

    converter = CSVTableConverter(graph=graph, node_type_id=node_type_id)
    export_name = graph_slug + '_' + node_type.name + '.csv'

    response = StreamingHttpResponse(converter.stream_export(),
                                     content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % export_name
    return response


@condition(last_modified_func=graph_last_modified)
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_export_queries_csv(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    csv_results = request.session.get('csv_results', None)
    query_name = request.session.get('query_name', None)
    headers_formatted = request.session.get('headers_formatted', None)
    headers_raw = request.session.get('headers_raw', None)

    converter = CSVQueryConverter(graph=graph, csv_results=csv_results,
                                  query_name=query_name,
                                  headers_formatted=headers_formatted,
                                  headers_raw=headers_raw)
    query_name = query_name.decode('utf-8')
    csv_name = query_name + '.csv'
    export_name = graph_slug + '_' + csv_name

    response = StreamingHttpResponse(converter.stream_export(),
                                     content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % export_name
    return response
