# -*- coding: utf-8 -*-
from django.db import transaction
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from graphs.models import Graph, Schema
from schemas.forms import (NodeTypeForm, NodePropertyFormSet,
                           RelationshipTypeForm, RelationshipTypeFormSet,
                           TypeDeleteForm, TypeDeleteConfirmForm,
                           ON_DELETE_NOTHING, ON_DELETE_CASCADE)
from schemas.models import NodeType, RelationshipType


@permission_required("schemas.change_schema", (Schema, "graph__id", "graph_id"))
def schema_edit(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    nodetypes = NodeType.objects.filter(schema__graph__id=graph_id)
    reltypes = None
    return render_to_response('schemas_edit.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes},
                              context_instance=RequestContext(request))


@permission_required("schemas.delete_schema", (Schema, "graph__id", "graph_id"))
def schema_nodetype_delete(request, graph_id, nodetype_id):
    graph = get_object_or_404(Graph, id=graph_id)
    nodetype = get_object_or_404(NodeType, id=nodetype_id)
    count = len(graph.nodes.filter(label=nodetype.id, properties=False))
    redirect_url = reverse("schema_edit", args=[graph.id])
    if count == 0:
        form = TypeDeleteConfirmForm()
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteConfirmForm(data=data)
            if form.is_valid():
                confirm = form.cleaned_data["confirm"]
                if confirm:
                    nodetype.delete()
                    return redirect(redirect_url)
    else:
        form = TypeDeleteForm(count=count)
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteForm(data=data, count=count)
            if form.is_valid():
                option = form.cleaned_data["option"]
                if option == ON_DELETE_CASCADE:
                    graph.nodes.delete(label=nodetype.id)
                nodetype.delete()
                return redirect(redirect_url)
    return render_to_response('schemas_item_delete.html',
                              {"graph": graph,
                               "item_type_label": _("Type"),
                               "item_type": "node",
                               "item_type_id": nodetype_id,
                               "item_type_name": nodetype.name,
                               "item_type_count": count,
                               "form": form,
                               "type_id": nodetype_id},
                              context_instance=RequestContext(request))


@permission_required("schemas.edit_schema", (Schema, "graph__id", "graph_id"))
def schema_nodetype_create(request, graph_id):
    return schema_nodetype_editcreate(request, graph_id)


@permission_required("schemas.edit_schema", (Schema, "graph__id", "graph_id"))
def schema_nodetype_edit(request, graph_id, nodetype_id):
    return schema_nodetype_editcreate(request, graph_id, nodetype_id)


def schema_nodetype_editcreate(request, graph_id, nodetype_id=None):
    graph = get_object_or_404(Graph, id=graph_id)
    if nodetype_id:
        empty_nodetype = get_object_or_404(NodeType, id=nodetype_id)
    else:
        empty_nodetype = NodeType()
    form = NodeTypeForm(instance=empty_nodetype)
    formset = NodePropertyFormSet(instance=empty_nodetype)
    if request.POST:
        data = request.POST.copy()
        form = NodeTypeForm(data=data, instance=empty_nodetype)
        formset = NodePropertyFormSet(data=data, instance=empty_nodetype)
        if form.is_valid() and formset.is_valid():
            with transaction.commit_on_success():
                node_type = form.save(commit=False)
                node_type.schema = graph.schema
                node_type.save()
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.node = node_type
                    instance.save()
                redirect_url = reverse("schema_edit", args=[graph.id])
            return redirect(redirect_url)
    return render_to_response('schemas_item_edit.html',
                              {"graph": graph,
                               "item_type_label": _("Type"),
                               "item_type": "node",
                               "item_type_id": nodetype_id,
                               "form": form,
                               "fields_to_hide": ["plural_name",
                                                  "inverse", "plural_inverse",
                                                  "arity", "inheritance"],
                               "formset": formset},
                              context_instance=RequestContext(request))


@permission_required("schemas.edit_schema", (Schema, "graph__id", "graph_id"))
def schema_relationshiptype_create(request, graph_id):
    return schema_relationshiptype_editcreate(request, graph_id)


@permission_required("schemas.edit_schema", (Schema, "graph__id", "graph_id"))
def schema_relationshiptype_edit(request, graph_id, relationshiptype_id):
    return schema_relationshiptype_editcreate(request, graph_id,
                                       relationshiptype_id=relationshiptype_id)


def schema_relationshiptype_editcreate(request, graph_id,
                                       relationshiptype_id=None):
    graph = get_object_or_404(Graph, id=graph_id)
    if relationshiptype_id:
        empty_relationshiptype = get_object_or_404(RelationshipType,
                                                   id=relationshiptype_id)
    else:
        empty_relationshiptype = RelationshipType()
    initial = {"arity": None}
    for field_name in ["source", "name", "target", "inverse"]:
        if field_name in request.GET:
            initial[field_name] = request.GET.get(field_name)
    form = RelationshipTypeForm(initial=initial, schema=graph.schema,
                                instance=empty_relationshiptype)
    formset = RelationshipTypeFormSet(instance=empty_relationshiptype)
    if request.POST:
        data = request.POST.copy()
        form = RelationshipTypeForm(data=data, schema=graph.schema,
                                    instance=empty_relationshiptype)
        formset = RelationshipTypeFormSet(data=data,
                                          instance=empty_relationshiptype)
        if form.is_valid() and formset.is_valid():
            with transaction.commit_on_success():
                relationshiptype = form.save(commit=False)
                if (relationshiptype.source.schema != graph.schema
                    or relationshiptype.target.schema != graph.schema):
                        raise ValidationError("Operation not allowed")
                relationshiptype.schema = graph.schema
                relationshiptype.save()
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.relationship = relationshiptype
                    instance.save()
                redirect_url = reverse("schema_edit", args=[graph.id])
            return redirect(redirect_url)
    return render_to_response('schemas_item_edit.html',
                              {"graph": graph,
                               "item_type_label": _("Allowed Relationship"),
                               "item_type": "relationship",
                               "item_type_id": relationshiptype_id,
                               "form": form,
                               "fields_to_hide": ["plural_name",
                                                  "inverse", "plural_inverse",
                                                  "arity", "inheritance"],
                               "formset": formset},
                              context_instance=RequestContext(request))


@permission_required("schemas.edit_schema", (Schema, "graph__id", "graph_id"))
def schema_relationshiptype_delete(request, graph_id,
                                   relationshiptype_id):
    graph = get_object_or_404(Graph, id=graph_id)
    relationshiptype = get_object_or_404(RelationshipType,
                                         id=relationshiptype_id)
    count = len(graph.relationships.filter(label=relationshiptype.id,
                                           properties=False))
    redirect_url = reverse("schema_edit", args=[graph.id])
    if count == 0:
        form = TypeDeleteConfirmForm()
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteConfirmForm(data=data)
            if form.is_valid():
                confirm = form.cleaned_data["confirm"]
                if confirm:
                    relationshiptype.delete()
                    return redirect(redirect_url)
    else:
        form = TypeDeleteForm(count=count)
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteForm(data=data, count=count)
            if form.is_valid():
                option = form.cleaned_data["option"]
                if option == ON_DELETE_CASCADE:
                    graph.relationships.delete(label=relationshiptype.id)
                relationshiptype.delete()
                return redirect(redirect_url)
    return render_to_response('schemas_item_delete.html',
                              {"graph": graph,
                               "item_type_label": _("Allowed Relationship"),
                               "item_type": "relationship",
                               "item_type_id": relationshiptype_id,
                               "item_type_name": relationshiptype.name,
                               "item_type_count": count,
                               "form": form,
                               "type_id": relationshiptype_id},
                              context_instance=RequestContext(request))
