# -*- coding: utf-8 -*-
from json import dumps

from django.db import transaction
from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import (render_to_response, get_object_or_404,
                              redirect, HttpResponse)
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from data.models import Data, MediaNode
from data.forms import (NodeForm, RelationshipForm, TypeBaseFormSet,
                        MediaFileFormSet, MediaLinkFormSet,
                        ItemDeleteConfirmForm,
                        ITEM_FIELD_NAME)
from graphs.models import Graph
from schemas.models import NodeType, RelationshipType


def create_data(properties, data_list, add_edge_extras=False):
    data = []
    #TODO In the preview we must cut the number of nodes better
    for element in data_list:
        row = []
        if add_edge_extras:
            row.append(element.source.display)
            row.append(element.target.display)
        for p in properties:
            row.append(element.get(p, ""))
        row.append(element.id)
        data.append(row)
    return data


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def nodes_list(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data_preview = []
    for type_element in graph.schema.nodetype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties, type_element.all()[:5])
        data_preview.append([type_element.name, properties, data,
                             type_element.id])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def nodes_lookup(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.GET.copy()
    if (request.is_ajax() or settings.DEBUG) and data:
        node_type_id = data.keys()[0]
        node_type = get_object_or_404(NodeType, id=node_type_id)
        q = data[node_type_id]
        properties = node_type.properties.filter(display=True)
        if not properties:
            properties = node_type.properties.all()[:2]
        query = graph.Q()
        for prop in properties:
            query |= graph.Q(prop.key, icontains=q)
        nodes = node_type.filter(query)[:10]
        json_nodes = []
        for node in nodes:
            json_nodes.append({
                "id": node.id,
                "display": node.display
            })
        return HttpResponse(dumps(json_nodes),
                            status=200, mimetype='application/json')
    raise Http404(_("Mismatch criteria for matching the search."))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def nodes_list_full(request, graph_slug, node_type_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    type_element = get_object_or_404(NodeType, id=node_type_id)
    data_preview = []
    properties = [p.key for p in type_element.properties.all()]
    data = create_data(properties, type_element.all())
    data_preview.append([type_element.name, properties, data])
    nodes = type_element.all()
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                               "option_list": data_preview,
                               "nodes": nodes,
                               "node_type": type_element
                               }, context_instance=RequestContext(request))


@permission_required("data.add_data", (Data, "graph__slug", "graph_slug"))
def nodes_create(request, graph_slug, node_type_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
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
    outgoing_formsets = SortedDict()
    prefixes = []
    for relationship in nodetype.outgoing_relationships.all():
        arity = relationship.arity_target
        if arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=arity,
                                                  extra=1)
        else:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  can_delete=True,
                                                  extra=1)
        relationship_slug = "o_%s%s" % (relationship.name, relationship.id)
        formset_prefix = slugify(relationship_slug).replace("-", "_")
        prefixes.append({"key": formset_prefix,
                         "value": u"→ %s (%s)" % (relationship.name,
                                                  relationship.target.name)})
        outgoing_formset = RelationshipFormSet(itemtype=relationship,
                                               instance=nodetype,
                                               prefix=formset_prefix,
                                               data=data)
        outgoing_formsets[formset_prefix] = outgoing_formset
    incoming_formsets = SortedDict()
    for relationship in nodetype.incoming_relationships.all():
        arity = relationship.arity_source
        if arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=arity,
                                                  extra=1)
        else:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  can_delete=True,
                                                  extra=1)
        relationship_slug = "i_%s%s" % (relationship.name, relationship.id)
        formset_prefix = slugify(relationship_slug).replace("-", "_")
        prefixes.append({"key": formset_prefix,
                         "value": u"← %s (%s)" % (relationship.name,
                                                  relationship.source.name)})
        incoming_formset = RelationshipFormSet(itemtype=relationship,
                                               instance=nodetype,
                                               prefix=formset_prefix,
                                               data=data)
        incoming_formsets[formset_prefix] = incoming_formset
    if (data and node_form.is_valid()
            and mediafile_formset.is_valid() and medialink_formset.is_valid()
            and all([rf.is_valid() for rf in outgoing_formsets.values()])
            and all([rf.is_valid() for rf in incoming_formsets.values()])):
        with transaction.commit_manually():
            try:
                node = node_form.save()
                for outgoing_formset in outgoing_formsets.values():
                    for outgoing_form in outgoing_formset.forms:
                        outgoing_form.save(related_node=node)
                for incoming_formset in incoming_formsets.values():
                    for incoming_form in incoming_formset.forms:
                        incoming_form.save(related_node=node)
                # Manage files and links
                mediafiles = mediafile_formset.save(commit=False)
                medialinks = medialink_formset.save(commit=False)
                if mediafiles or medialinks:
                    media_node = MediaNode.objects.create(node_id=node.id,
                                                          data=graph.data)
                    for mediafile in mediafiles:
                        mediafile.media_node = media_node
                        mediafile.save()
                    for medialink in medialinks:
                        medialink.media_node = media_node
                        medialink.save()
            except:
                transaction.rollback()
            else:
                transaction.commit()
        redirect_url = reverse("nodes_list_full",
                               args=[graph.slug, node_type_id])
        return redirect(redirect_url)
    return render_to_response('nodes_editcreate.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "prefixes": prefixes,
         "outgoing_formsets": outgoing_formsets,
         "incoming_formsets": incoming_formsets,
         "mediafile_formset": mediafile_formset,
         "medialink_formset": medialink_formset,
         "action": u"%s %s" % (_("New"), nodetype.name)},
        context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"))
def nodes_edit(request, graph_slug, node_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node = graph.nodes.get(node_id)
    nodetype = get_object_or_404(NodeType, id=node.label)
    try:
        media_node = MediaNode.objects.get(node_id=node.id, data=graph.data)
    except MediaNode.MultipleObjectsReturned:
        media_nodes = MediaNode.objects.filter(node_id=node.id, data=graph.data)
        media_node = media_nodes.latest("id")
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
    # Outgoing relationships
#    initial = []
#    for relationship in node.relationships.all():
#        properties = relationship.properties
#        outgoing_type = RelationshipType.objects.get(id=relationship.label)
#        properties.update({
#            outgoing_type.id: relationship.target.id,
#            ITEM_FIELD_NAME: relationship.id,
#        })
#        initial.append(properties)
    prefixes = []
    outgoing_formsets = SortedDict()
    allowed_outgoing_relationships = nodetype.outgoing_relationships.all()
    for relationship in allowed_outgoing_relationships:
        initial = []
        graph_relationships = node.relationships.filter(label=relationship.id)
        for graph_relationship in graph_relationships:
            properties = graph_relationship.properties
            properties.update({
                relationship.id: graph_relationship.target.id,
                ITEM_FIELD_NAME: graph_relationship.id,
            })
            initial.append(properties)
        arity = relationship.arity_target
        if arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=arity,
                                                  extra=1)
        else:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  can_delete=True,
                                                  extra=1)
        relationship_slug = "o_%s%s_%s" % (relationship.name, relationship.id,
                                           relationship.target.id)
        formset_prefix = slugify(relationship_slug).replace("-", "_")
        prefixes.append({"key": formset_prefix,
                         "value": u"→ %s (%s)" % (relationship.name,
                                                  relationship.target.name)})
        outgoing_formset = RelationshipFormSet(itemtype=relationship,
                                               instance=nodetype,
                                               prefix=formset_prefix,
                                               initial=initial,
                                               data=data)
        outgoing_formsets[formset_prefix] = outgoing_formset
    # Incoming relationships
#    initial = []
#    for relationship in node.relationships.all():
#        properties = relationship.properties
#        incoming_type = RelationshipType.objects.get(id=relationship.label)
#        properties.update({
#            incoming_type.id: relationship.source.id,
#            ITEM_FIELD_NAME: relationship.id,
#        })
#        initial.append(properties)
    incoming_formsets = SortedDict()
    allowed_incoming_relationships = nodetype.get_incoming_relationships()
    for relationship in allowed_incoming_relationships:
        initial = []
        graph_relationships = node.relationships.filter(label=relationship.id)
        for graph_relationship in graph_relationships:
            properties = graph_relationship.properties
            properties.update({
                relationship.id: graph_relationship.source.id,
                ITEM_FIELD_NAME: graph_relationship.id,
            })
            initial.append(properties)
        arity = relationship.arity_source
        if arity > 0:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  max_num=arity,
                                                  extra=1)
        else:
            RelationshipFormSet = formset_factory(RelationshipForm,
                                                  formset=TypeBaseFormSet,
                                                  can_delete=True,
                                                  extra=1)
        relationship_slug = "i_%s%s_%s" % (relationship.name, relationship.id,
                                           relationship.source.id)
        formset_prefix = slugify(relationship_slug).replace("-", "_")
        prefixes.append({"key": formset_prefix,
                         "value": u"← %s (%s)" % (relationship.name,
                                                  relationship.source.name)})
        incoming_formset = RelationshipFormSet(itemtype=relationship,
                                               instance=nodetype,
                                               prefix=formset_prefix,
                                               initial=initial,
                                               data=data)
        incoming_formsets[formset_prefix] = incoming_formset
    # Save forms and formsets
    if (data and node_form.is_valid()
            and mediafile_formset.is_valid() and medialink_formset.is_valid()
            and all([rf.is_valid() for rf in outgoing_formsets.values()])
            and all([rf.is_valid() for rf in incoming_formsets.values()])):
        with transaction.commit_manually():
            try:
                node = node_form.save()
                for outgoing_formset in outgoing_formsets.values():
                    for outgoing_form in outgoing_formset.forms:
                        outgoing_form.save(related_node=node)
                for incoming_formset in incoming_formsets.values():
                    for incoming_form in incoming_formset.forms:
                        incoming_form.save(related_node=node)
                mediafiles = mediafile_formset.save(commit=False)
                medialinks = medialink_formset.save(commit=False)
                # Manage files and links
                if not media_node.pk and (mediafiles or medialinks):
                    media_node = MediaNode.objects.create(node_id=node.id,
                                                          data=graph.data)
                for mediafile in mediafiles:
                    mediafile.media_node = media_node
                    mediafile.save()
                for medialink in medialinks:
                    medialink.media_node = media_node
                    medialink.save()
                if media_node.pk and not media_node.files.exists() and \
                        not media_node.links.exists():
                    media_node.delete()
            except:
                transaction.rollback()
            else:
                transaction.commit()
        redirect_url = reverse("nodes_list_full",
                               args=[graph.slug, nodetype.id])
        return redirect(redirect_url)
    return render_to_response('nodes_editcreate.html',
        {"graph": graph,
         "nodetype": nodetype,
         "node_form": node_form,
         "node": node,
         "prefixes": prefixes,
         "outgoing_formsets": outgoing_formsets,
         "incoming_formsets": incoming_formsets,
         "mediafile_formset": mediafile_formset,
         "medialink_formset": medialink_formset,
         "action": _("Edit"),
         "delete": True},
        context_instance=RequestContext(request))


@permission_required("data.delete_data", (Data, "graph__slug", "graph_slug"))
def nodes_delete(request, graph_slug, node_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node = graph.nodes.get(node_id)
    nodetype = get_object_or_404(NodeType, id=node.label)
#    relationshiptype = get_object_or_404(RelationshipType,
#                                         id=relationshiptype_id)
#    count = len(graph.relationships.filter(label=relationshiptype.id,
#                                           properties=False))
#    redirect_url = reverse("schema_edit", args=[graph.slug])
#    if count == 0:
#        form = TypeDeleteConfirmForm()
#        if request.POST:
#            data = request.POST.copy()
#            form = TypeDeleteConfirmForm(data=data)
#            if form.is_valid():
#                confirm = form.cleaned_data["confirm"]
#                if confirm:
#                    relationshiptype.delete()
#                    return redirect(redirect_url)
#    else:
    form = ItemDeleteConfirmForm()
    if request.POST:
        data = request.POST.copy()
        form = ItemDeleteConfirmForm(data=data)
        if form.is_valid():
            confirm = form.cleaned_data["confirm"]
            if confirm:
                for relationship in node.relationships.all():
                    relationship.delete()
                media_node = None
                try:
                    media_node = MediaNode.objects.get(node_id=node.id,
                                                       data=graph.data)
                except MediaNode.MultipleObjectsReturned:
                    media_nodes = MediaNode.objects.filter(node_id=node.id,
                                                           data=graph.data)
                    media_node = media_nodes.latest("id")
                except MediaNode.DoesNotExist:
                    pass
                if media_node:
                    media_node.delete()
                node.delete()
                redirect_url = reverse("nodes_list", args=[graph.slug])
                return redirect(redirect_url)
    return render_to_response('nodes_delete.html',
                              {"graph": graph,
                               "item_type_label": _("Node"),
                               "item_type": "node",
                               "item_type_id": nodetype.id,
                               "item_type_name": nodetype.name,
                               "item_type_count": None,  # count,
                               "item_type_object": nodetype,
                               "form": form,  # form,
                               "item": node,
                               "action": _("Delete")
                               },
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def relationships_list(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data_preview = []
    for type_element in graph.schema.relationshiptype_set.all():
        properties = [p.key for p in type_element.properties.all()]
        data = create_data(properties, type_element.all()[:5], True)
        columns = ["source", "target"]
        columns.extend(properties)
        type_element_name = u"(%s) %s (%s)" % (type_element.source.name,
                                               type_element.name,
                                               type_element.target.name)
        data_preview.append([type_element_name,
            columns,
            data,
            type_element.id])
    return render_to_response('relationships_list.html',
                              {"graph": graph,
                                  "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def relationships_list_full(request, graph_slug, relationship_type_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    type_element = get_object_or_404(RelationshipType,
                                    id=relationship_type_id)
    data_preview = []
    properties = [p.key for p in type_element.properties.all()]
    data = create_data(properties, type_element.all(), True)
    columns = ["source", "target"]
    columns.extend(properties)
    data_preview.append([type_element.name,
        columns,
        data])
    return render_to_response('nodes_list.html',
                              {"graph": graph,
                               "option_list": data_preview},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def node_relationships(request, graph_slug, node_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node = graph.nodes.get(int(node_id))
    incoming = []
    for r in node.relationships.incoming():
        label = get_object_or_404(RelationshipType, id=r.label)
        incoming.append({"node_id": r.source.id,
                        "node_display": r.source.display,
                        "direction": "incoming",
                        "label": label.name})
    outgoing = []
    for r in node.relationships.outgoing():
        label = get_object_or_404(RelationshipType, id=r.label)
        outgoing.append({"node_id": r.target.id,
                        "node_display": r.target.display,
                        "direction": "outgoing",
                        "label": label.name})
    result = {'incoming': incoming, 'outgoing': outgoing}
    return HttpResponse(dumps(result))
