# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.shortcuts import (render_to_response,
                        redirect, HttpResponse)
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

from guardian.decorators import permission_required

from data.models import Data
from data.forms import (NodeForm, RelationshipForm, TypeBaseFormSet,
                        MediaFileFormSet, MediaLinkFormSet)
from graphs.models import Graph
from schemas.models import NodeType, RelationshipType


def create_data(properties, data_list, add_edge_extras=False):
    data = []
    #TODO In the preview we must cut the number of nodes better
    for element in data_list:
        row = []
        if add_edge_extras:
            row.append(element.source.id)
            row.append(element.target.id)
        for p in properties:
            row.append(element.get(p, ""))
        row.append(element.id)
        data.append(row)
    return data


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def nodes_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    data_preview = []
    for type_element in graph.schema.nodetype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties,
                    graph.nodes.filter(label=type_element.id)[:5])
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
                graph.nodes.filter(label=type_element.id))
    data_preview.append([type_element.name,
        properties,
        data,
        type_element.id])
    nodes = graph.nodes.filter(label=node_type_id)
    return render_to_response('nodes_list.html', {
                                "graph": graph,
                                "option_list": data_preview,
                                "nodes": nodes,
                              }, context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__id", "graph_id"))
def nodes_create(request, graph_id, node_type_id):
    graph = get_object_or_404(Graph, id=graph_id)
    nodetype = get_object_or_404(NodeType, id=node_type_id)
    if request.POST:
        data = request.POST.copy()
    else:
        data = None
    node_form = NodeForm(itemtype=nodetype, data=data)
    relationship_formsets = {}
    for relationship in nodetype.outgoing_relationships.all():
        if relationship.arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=relationship.arity,
                                                  extra=1)
        else:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  can_delete=True,
                                                  extra=1)
        formset_prefix = slugify(relationship.name).replace("-", "_")
        relationship_formset = RelationshipFormSet(itemtype=relationship,
                                                   prefix=formset_prefix,
                                                   data=data)
        relationship_formsets[formset_prefix] = relationship_formset
    # TODO: Use dynamic formset
    mediafile_formset = MediaFileFormSet(data=data, prefix="__files")
    medialink_formset = MediaLinkFormSet(data=data, prefix="__links")
    if (data and node_form.is_valid()
        and mediafile_formset.is_valid() and  medialink_formset.is_valid()
        and all([rf.is_valid() for rf in relationship_formsets.values()])):
        # TODO: This should be under a transaction
        node = node_form.save()
        for relationship_formset in relationship_formsets.values():
            for relationship_form in relationship_formset.forms:
                relationship_form.save(source_node=node)
        mediafile_formset.save()
        medialink_formset.save()
        redirect_url = reverse("nodes_list_full", args=[graph.id, node_type_id])
        return redirect(redirect_url)
    return render_to_response('nodes_create.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "relationship_formsets": relationship_formsets,
         "mediafile_formset": mediafile_formset,
         "medialink_formset": medialink_formset},
        context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def relationships_list(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    data_preview = []
    for type_element in graph.schema.relationshiptype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties,
                    graph.relationships.filter(label=type_element.id)[:5],
                    True)
        columns = ["source", "target"]
        columns.extend(properties)
        data_preview.append([type_element.name,
            columns,
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
                graph.relationships.filter(label=type_element.id),
                True)
    columns = ["source", "target"]
    columns.extend(properties)
    data_preview.append([type_element.name,
        columns,
        data,
        type_element.id])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__id", "graph_id"))
def node_relationships(request, graph_id, node_id):
    graph = get_object_or_404(Graph, id=graph_id)
    node = graph.nodes.get(int(node_id))
    result = []
    for r in node.relationships.incoming():
        label = get_object_or_404(RelationshipType, id=r.label)
        result.append({"node_id": r.source.id,
                        "node_display": r.source.display,
                        "direction": "incoming",
                        "label": label.name})
    for r in node.relationships.outgoing():
        label = get_object_or_404(RelationshipType, id=r.label)
        result.append({"node_id": r.target.id,
                        "node_display": r.target.display,
                        "direction": "outgoing",
                        "label": r.label.name})
    return HttpResponse(simplejson.dumps(result))
