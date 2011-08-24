# -*- coding: utf-8 -*-
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from guardian.decorators import permission_required

from data.models import Data
from data.forms import NodeForm, RelationshipForm, TypeBaseFormSet
from graphs.models import Graph
from schemas.models import NodeType


def create_data(properties, data_list):
    data = []
    #TODO In the preview we must cut the number of nodes better
    for element in data_list:
        row = []
        for p in properties:
            row.append(element.get(p))
        data.append(row)
    return data


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def nodes_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    data_preview = []
    for type_element in graph.schema.nodetype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties,
                    graph.nodes.filter(label=type_element.name)[:5])
        data_preview.append([type_element.name,
            properties,
            data,
            type_element.id])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def nodes_list_full(request, graph_id, node_type_id):
    graph = get_object_or_404(Graph, id=graph_id)
    type_element = get_object_or_404(NodeType, id=node_type_id)
    data_preview = []
    properties = [p.key for p in type_element.properties.all()]
    data = create_data(properties,
                graph.nodes.filter(label=type_element.name))
    data_preview.append([type_element.name,
        properties,
        data])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__id", "graph_id"))
def nodes_create(request, graph_id, node_type_id):
    graph = get_object_or_404(Graph, id=graph_id)
    nodetype = get_object_or_404(NodeType, id=node_type_id)
    node_form = NodeForm(itemtype=nodetype)
    relationship_formsets = {}
    for relationship in nodetype.outgoing_relationships.all():
        if relationship.arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=relationship.arity,
                                                  extra=1)
        else:
            # TODO: Use dynamic formset
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  extra=1)
        relationship_formset = RelationshipFormSet(itemtype=relationship)
        relationship_formsets[relationship.name] = relationship_formset
    return render_to_response('nodes_create.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "relationship_formsets": relationship_formsets},
        context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def relationships_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    data_preview = []
    for type_element in graph.schema.relationshiptype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties,
                    graph.relationships.filter(label=type_element.name)[:5])
        data_preview.append([type_element.name,
            properties,
            data,
            type_element.id])
    return render_to_response('relationships_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def relationships_list_full(request, graph_id, relationship_type_id):
    graph = get_object_or_404(Graph, id=graph_id)
    type_element = get_object_or_404(RelationshipType,
                                    id=relationship_type_id)
    data_preview = []
    properties = [p.key for p in type_element.properties.all()]
    data = create_data(properties,
                graph.relationships.filter(label=type_element.name))
    data_preview.append([type_element.name,
        properties,
        data])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))
