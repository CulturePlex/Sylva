# -*- coding: utf-8 -*-
import simplejson

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.shortcuts import (render_to_response, get_object_or_404,
                             redirect, HttpResponse)
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from data.models import Data, MediaNode
from data.forms import (NodeForm, RelationshipForm, TypeBaseFormSet,
                        MediaFileFormSet, MediaLinkFormSet,
                        ITEM_FIELD_NAME)
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
        mediafile_formset = MediaFileFormSet(data=data, files=request.FILES,
                                             prefix="__files")
        medialink_formset = MediaLinkFormSet(data=data, files=request.FILES,
                                             prefix="__links")
    else:
        data = None
        mediafile_formset = MediaFileFormSet(prefix="__files")
        medialink_formset = MediaLinkFormSet(prefix="__links")
    node_form = NodeForm(itemtype=nodetype, data=data)
    outgoing_formsets = {}
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
        outgoing_formset = RelationshipFormSet(itemtype=relationship,
                                                   instance=nodetype,
                                                   prefix=formset_prefix,
                                                   data=data)
        outgoing_formsets[formset_prefix] = outgoing_formset
    incoming_formsets = {}
    for relationship in nodetype.incoming_relationships.all():
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
        incoming_formset = RelationshipFormSet(itemtype=relationship,
                                                   instance=nodetype,
                                                   prefix=formset_prefix,
                                                   data=data)
        incoming_formsets[formset_prefix] = incoming_formset
    if (data and node_form.is_valid()
        and mediafile_formset.is_valid() and  medialink_formset.is_valid()
        and all([rf.is_valid() for rf in outgoing_formsets.values()])
        and all([rf.is_valid() for rf in incoming_formsets.values()])):
        # TODO: This should be under a transaction
        node = node_form.save()
        for outgoing_formset in outgoing_formsets.values():
            for outgoing_form in outgoing_formset.forms:
                outgoing_form.save(related_node=node)
        for incoming_formset in incoming_formsets.values():
            for incoming_form in incoming_formset.forms:
                incoming_form.save(related_node=node)
        # Manage files and links
        mediafiles = mediafile_formset.save(commit=False)
        media_node = MediaNode.objects.create(node_id=node.id, data=graph.data)
        for mediafile in mediafiles:
            mediafile.media_node = media_node
            mediafile.save()
        medialinks = medialink_formset.save(commit=False)
        for medialink in medialinks:
            medialink.media_node = media_node
            medialink.save()
        redirect_url = reverse("nodes_list_full", args=[graph.id, node_type_id])
        return redirect(redirect_url)
    return render_to_response('nodes_editcreate.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "outgoing_formsets": outgoing_formsets,
         "incoming_formsets": incoming_formsets,
         "mediafile_formset": mediafile_formset,
         "medialink_formset": medialink_formset,
         "action": _("New")},
        context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__id", "graph_id"))
def nodes_edit(request, graph_id, node_id):
    graph = get_object_or_404(Graph, id=graph_id)
    node = graph.nodes.get(node_id)
    nodetype = get_object_or_404(NodeType, id=node.label)
    try:
        media_node = MediaNode.objects.get(node_id=node.id, data=graph.data)
    except MediaNode.DoesNotExist:
        media_node = MediaNode()
    if request.POST:
        data = request.POST.copy()
        mediafile_formset = MediaFileFormSet(instance=media_node,
                                             data=data, files=request.FILES,
                                             prefix="__files")
        medialink_formset = MediaLinkFormSet(instance=media_node,
                                             data=data, files=request.FILES,
                                             prefix="__links")
    else:
        data = None
        mediafile_formset = MediaFileFormSet(instance=media_node,
                                             data=data, prefix="__files")
        medialink_formset = MediaLinkFormSet(instance=media_node,
                                             data=data, prefix="__links")
    node_initial = node.properties.copy()
    node_initial.update({ITEM_FIELD_NAME: node.id})
    node_form = NodeForm(itemtype=nodetype, initial=node_initial, data=data)
    initial = []
    # Outgoing relationships
    for relationship in node.relationships.all():
        properties = relationship.properties
        outgoing_type = RelationshipType.objects.get(id=relationship.label)
        properties.update({
            outgoing_type.name: relationship.target.id,
            ITEM_FIELD_NAME: relationship.id,
        })
        initial.append(properties)
    outgoing_formsets = {}
    allowed_outgoing_relationships = nodetype.outgoing_relationships.all()
    for relationship in allowed_outgoing_relationships:
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
        outgoing_formset = RelationshipFormSet(itemtype=relationship,
                                                   instance=nodetype,
                                                   prefix=formset_prefix,
                                                   initial=initial,
                                                   data=data)
        outgoing_formsets[formset_prefix] = outgoing_formset
    # Incoming relationships
    for relationship in node.relationships.all():
        properties = relationship.properties
        incoming_type = RelationshipType.objects.get(id=relationship.label)
        properties.update({
            incoming_type.name: relationship.source.id,
            ITEM_FIELD_NAME: relationship.id,
        })
        initial.append(properties)
    incoming_formsets = {}
    allowed_incoming_relationships = nodetype.incoming_relationships.all()
    for relationship in allowed_incoming_relationships:
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
        incoming_formset = RelationshipFormSet(itemtype=relationship,
                                                   instance=nodetype,
                                                   prefix=formset_prefix,
                                                   initial=initial,
                                                   data=data)
        incoming_formsets[formset_prefix] = incoming_formset
    # Save forms and formsets
    if (data and node_form.is_valid()
        and mediafile_formset.is_valid() and  medialink_formset.is_valid()
        and all([rf.is_valid() for rf in outgoing_formsets.values()])
        and all([rf.is_valid() for rf in incoming_formsets.values()])):
        # TODO: This should be under a transaction
        node = node_form.save()
        for outgoing_formset in outgoing_formsets.values():
            for outgoing_form in outgoing_formset.forms:
                outgoing_form.save(related_node=node)
        for incoming_formset in incoming_formsets.values():
            for incoming_form in incoming_formset.forms:
                incoming_form.save(related_node=node)
        mediafiles = mediafile_formset.save(commit=False)
        # Manage files and links
        for mediafile in mediafiles:
            mediafile.media_node = media_node
            mediafile.save()
        medialinks = medialink_formset.save(commit=False)
        for medialink in medialinks:
            medialink.media_node = media_node
            medialink.save()
        redirect_url = reverse("nodes_list_full", args=[graph.id, nodetype.id])
        return redirect(redirect_url)
    return render_to_response('nodes_editcreate.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "outgoing_formsets": outgoing_formsets,
         "incoming_formsets": incoming_formsets,
         "mediafile_formset": mediafile_formset,
         "medialink_formset": medialink_formset,
         "action": _("Edit")},
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
                        "label": label.name})
    return HttpResponse(simplejson.dumps(result))
