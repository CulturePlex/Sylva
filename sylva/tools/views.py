# -*- coding: utf-8 -*-
import simplejson

from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_object_or_404, render_to_response,
                                HttpResponse)
from django.template import RequestContext
from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph


@login_required()
def graph_import_tool(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    # Schema jsonification
    schema = graph.schema.export()
    schema_json = {"nodeTypes": {}, "allowedEdges":{}}
    for node_type in schema["node_types"]:
        schema_json["nodeTypes"][node_type.name] = {}
    for edge_type in schema["relationship_types"]:
        edge_name = "%s_%s_%s" % (edge_type.source.name,
                                edge_type.name,
                                edge_type.target.name)
        schema_json["allowedEdges"][edge_name] = {
                "source": edge_type.source.name,
                "label": edge_type.name,
                "target": edge_type.target.name}
    return render_to_response('graph_import_tool.html', {
                                "graph": graph,
                                "sylva_schema": simplejson.dumps(schema_json),
                            },
                            context_instance=RequestContext(request))

@permission_required("data.change_data", (Data, "graph__id", "graph_id"))
def ajax_node_create(request, graph_id):
    return HttpResponse(simplejson.dumps({}))
