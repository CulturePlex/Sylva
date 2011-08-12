# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def nodes_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    data_preview = []
    for type_element in graph.schema.nodetype_set.all():
        type_element_name = type_element.name
        properties = [p.key for p in type_element.properties.all()]
        data = []
        #TODO An optimized method that returns nodes by type
        #TODO In the preview we must cut the number of nodes
        for element in graph.nodes.all():
            if element.label == type_element_name:
                row = []
                for p in properties:
                    row.append(element.get(p))
                data.append(row)
        data_preview.append([type_element_name,
            properties,
            data])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def relationships_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    return render_to_response('relationships_list.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))
