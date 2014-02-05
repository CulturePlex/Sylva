# -*- coding: utf-8 -*-
import json

from django.db import transaction
from django.core.urlresolvers import reverse
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from graphs.models import Graph, Schema
from data.models import Data
from schemas.forms import (NodeTypeForm, NodePropertyFormSet,
                           RelationshipTypeForm, RelationshipTypeFormSet,
                           TypeDeleteForm, TypeDeleteConfirmForm,
                           SchemaImportForm, ElementTypeChangedForm,
                           ElementTypeDeletedForm)
from schemas.forms import ON_DELETE_CASCADE
# from schemas.forms import ON_DELETE_NOTHING
from django.forms.formsets import formset_factory
from schemas.models import NodeType, RelationshipType


@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_edit(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = None
    return render_to_response('schemas_edit.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes},
                              context_instance=RequestContext(request))


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_nodetype_delete(request, graph_slug, nodetype_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetype = get_object_or_404(NodeType, id=nodetype_id)
    count = graph.nodes.count(label=nodetype.id)
    redirect_url = reverse("schema_edit", args=[graph.slug])
    if count == 0:
        form = TypeDeleteConfirmForm()
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteConfirmForm(data=data)
            if form.is_valid():
                confirm = bool(int(form.cleaned_data["confirm"]))
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
                               "item_type_object": nodetype,
                               "form": form,
                               "type_id": nodetype_id},
                              context_instance=RequestContext(request))


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_nodetype_create(request, graph_slug):
    return schema_nodetype_editcreate(request, graph_slug)


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_nodetype_edit(request, graph_slug, nodetype_id):
    return schema_nodetype_editcreate(request, graph_slug, nodetype_id)


def schema_nodetype_editcreate(request, graph_slug, nodetype_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if nodetype_id:
        empty_nodetype = get_object_or_404(NodeType, id=nodetype_id)
    else:
        empty_nodetype = NodeType()
    form = NodeTypeForm(instance=empty_nodetype)
    formset = NodePropertyFormSet(instance=empty_nodetype)
    changed_props = request.session.get('schema_changed_props', None)
    deleted_props = request.session.get('schema_deleted_props', None)
    if changed_props:
        del request.session['schema_changed_props']
    if deleted_props:
        del request.session['schema_deleted_props']
    if request.POST:
        data = request.POST.copy()
        form = NodeTypeForm(data=data, instance=empty_nodetype)
        formset = NodePropertyFormSet(data=data, instance=empty_nodetype)
        if form.is_valid() and formset.is_valid():
            with transaction.commit_on_success():
                node_type = form.save(commit=False)
                node_type.schema = graph.schema
                # Checking the color
                if 'color' not in node_type.get_options():
                    color = '#F206FF'
                    node_type.set_option('color', color)
                node_type.save()
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.node = node_type
                    instance.save()
                schema_modified = False
                if formset.deleted_objects:
                    schema_modified = True
                    deleted_props = []
                    for prop_type in formset.deleted_objects:
                        deleted_props.append({'key': prop_type.key})
                    request.session['schema_deleted_props'] = deleted_props
                if formset.changed_objects:
                    changed_props = []
                    for prop_type, prop_dict in formset.changed_objects:
                        if 'key' in prop_dict:
                            schema_modified = True
                            for data in formset.cleaned_data:
                                if 'key' in data and 'id' in data and \
                                        data['key'] == prop_type.key:
                                    changed_props.append({
                                        'key': data['id'].key,
                                        'new_key': data['key']
                                    })
                    request.session['schema_changed_props'] = changed_props
                if schema_modified:
                    messages.success(request, _("Your changes were saved"))
                    redirect_url = reverse("schema_nodetype_properties_mend",
                                           args=[graph.slug, node_type.id])
                else:
                    redirect_url = reverse("schema_edit", args=[graph.slug])
            return redirect(redirect_url)
    return render_to_response('schemas_item_edit.html',
                              {"graph": graph,
                               "item_type_label": _("Type"),
                               "item_type": "node",
                               "item_type_id": nodetype_id,
                               "form": form,
                               "fields_to_hide": ["plural_name",
                                                  "inverse", "plural_inverse",
                                                  "arity_source",
                                                  "arity_target",
                                                  "validation",
                                                  "inheritance"],
                               "item_type_object": empty_nodetype,
                               "formset": formset},
                              context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def schema_nodetype_properties_mend(request, graph_slug, nodetype_id):
    element_type = get_object_or_404(NodeType, id=nodetype_id)
    return schema_properties_mend(request, graph_slug, element_type)


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_relationshiptype_create(request, graph_slug):
    return schema_relationshiptype_editcreate(request, graph_slug)


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_relationshiptype_edit(request, graph_slug, relationshiptype_id):
    func = schema_relationshiptype_editcreate
    return func(request, graph_slug, relationshiptype_id=relationshiptype_id)


def schema_relationshiptype_editcreate(request, graph_slug,
                                       relationshiptype_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if relationshiptype_id:
        empty_relationshiptype = get_object_or_404(RelationshipType,
                                                   id=relationshiptype_id)
    else:
        empty_relationshiptype = RelationshipType()
    initial = {"arity_source": None, "arity_target": None}
    for field_name in ["source", "name", "target", "inverse"]:
        if field_name in request.GET:
            initial[field_name] = request.GET.get(field_name)
    form = RelationshipTypeForm(initial=initial, schema=graph.schema,
                                instance=empty_relationshiptype)
    formset = RelationshipTypeFormSet(instance=empty_relationshiptype)
    changed_props = request.session.get('schema_changed_props', None)
    deleted_props = request.session.get('schema_deleted_props', None)
    if changed_props:
        del request.session['schema_changed_props']
    if deleted_props:
        del request.session['schema_deleted_props']
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
                schema_modified = False
                if formset.deleted_objects:
                    schema_modified = True
                    deleted_props = []
                    for prop_type in formset.deleted_objects:
                        deleted_props.append({'key': prop_type.key})
                    request.session['schema_deleted_props'] = deleted_props
                if formset.changed_objects:
                    changed_props = []
                    for prop_type, prop_dict in formset.changed_objects:
                        if 'key' in prop_dict:
                            schema_modified = True
                            for data in formset.cleaned_data:
                                if 'key' in data and 'id' in data and \
                                        data['key'] == prop_type.key:
                                    changed_props.append({
                                        'key': data['id'].key,
                                        'new_key': data['key']
                                    })
                    request.session['schema_changed_props'] = changed_props
                if schema_modified:
                    redirect_url = \
                        reverse("schema_relationshiptype_properties_mend",
                                args=[graph.slug, relationshiptype.id])
                else:
                    redirect_url = reverse("schema_edit", args=[graph.slug])
            return redirect(redirect_url)
    return render_to_response('schemas_item_edit.html',
                              {"graph": graph,
                               "item_type_label": _("Allowed Relationship"),
                               "item_type": "relationship",
                               "item_type_id": relationshiptype_id,
                               "form": form,
                               "fields_to_hide": ["plural_name",
                                                  "inverse", "plural_inverse",
                                                  "arity_source",
                                                  "arity_target",
                                                  "validation",
                                                  "inheritance"],
                               "formset": formset},
                              context_instance=RequestContext(request))


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_relationshiptype_delete(request, graph_slug,
                                   relationshiptype_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    relationshiptype = get_object_or_404(RelationshipType,
                                         id=relationshiptype_id)
    count = graph.relationships.count(label=relationshiptype.id)
    redirect_url = reverse("schema_edit", args=[graph.slug])
    if count == 0:
        form = TypeDeleteConfirmForm()
        if request.POST:
            data = request.POST.copy()
            form = TypeDeleteConfirmForm(data=data)
            if form.is_valid():
                confirm = bool(int(form.cleaned_data["confirm"]))
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
                               "item_type_object": relationshiptype,
                               "form": form,
                               "type_id": relationshiptype_id},
                              context_instance=RequestContext(request))


@permission_required("data.change_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def schema_relationshiptype_properties_mend(request, graph_slug,
                                            relationshiptype_id):
    element_type = get_object_or_404(RelationshipType, id=relationshiptype_id)
    return schema_properties_mend(request, graph_slug, element_type)


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_export(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if graph.schema.is_empty():
        messages.error(request, _("You are trying to export an empty schema!"))
        return redirect(reverse('dashboard'))
    schema = graph.schema.export()
    response = HttpResponse(json.dumps(schema), mimetype='application/json')
    attachment = 'attachment; filename=%s_schema.json' % graph_slug
    response['Content-Disposition'] = attachment
    return response


@permission_required("schemas.change_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_import(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if not graph.schema.is_empty():
        messages.error(request, _("The schema already exists!"))
        return redirect(reverse('dashboard'))
    form = SchemaImportForm()
    if request.POST and request.FILES:
        form = SchemaImportForm(request.POST, request.FILES)
        try:
            data = request.FILES['file'].read()
            schema_dict = json.loads(data)
            graph.schema._import(schema_dict)
            return redirect(schema_edit, graph_slug)
        except ValueError:
            messages.error(request, _("An error occurred when processing "
                                      "the exported schema"))
    return render_to_response('schemas_import.html',
                              {"graph": graph,
                               "form": form},
                              context_instance=RequestContext(request))


@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def schema_diagram_positions(request, graph_slug):
    status = 200  # OK
    data = request.POST.copy()
    if request.is_ajax() and data and "diagram_positions" in data:
        graph = get_object_or_404(Graph, slug=graph_slug)
        graph.schema.set_option("diagram_positions", data["diagram_positions"])
        graph.schema.save()
        status = 204  # No Content
    return HttpResponse(status=status)


def schema_properties_mend(request, graph_slug, element_type):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if not 'schema_changed_props' in request.session and \
            not 'schema_deleted_props' in request.session:
        return redirect(reverse("schema_edit", args=[graph.slug]))
    changed_props = request.session.get('schema_changed_props', [])
    deleted_props = request.session.get('schema_deleted_props', [])
    ElementTypeChangedFormSet = formset_factory(ElementTypeChangedForm,
                                                extra=0)
    ElementTypeDeletedFormSet = formset_factory(ElementTypeDeletedForm,
                                                extra=0)
    changed_formset = ElementTypeChangedFormSet(initial=changed_props,
                                                prefix='changed')
    deleted_formset = ElementTypeDeletedFormSet(initial=deleted_props,
                                                prefix='deleted')
    if request.POST:
        data = request.POST.copy()
        if changed_props:
            changed_formset = ElementTypeChangedFormSet(data=data,
                                                        initial=changed_props,
                                                        prefix='changed')
        if deleted_props:
            deleted_formset = ElementTypeDeletedFormSet(data=data,
                                                        initial=deleted_props,
                                                        prefix='deleted')
        fixed = False
        if changed_props and deleted_props:
            if changed_formset.is_valid() and deleted_formset.is_valid():
                for cdata in changed_formset.cleaned_data:
                    mend_schema_property(element_type, cdata['option'],
                                         cdata['key'], cdata['new_key'])
                for cdata in deleted_formset.cleaned_data:
                    mend_schema_property(element_type, cdata['option'],
                                         cdata['key'])
                request.session.pop('schema_changed_props')
                request.session.pop('schema_deleted_props')
                fixed = True
        elif changed_props and changed_formset.is_valid():
            for cdata in changed_formset.cleaned_data:
                mend_schema_property(element_type, cdata['option'],
                                     cdata['key'], cdata['new_key'])
            request.session.pop('schema_changed_props')
            fixed = True
        elif deleted_props and deleted_formset.is_valid():
            for cdata in deleted_formset.cleaned_data:
                mend_schema_property(element_type, cdata['option'],
                                     cdata['key'])
            request.session.pop('schema_deleted_props')
            fixed = True
        if fixed:
            return redirect(reverse("schema_edit", args=[graph.slug]))
    return render_to_response('schemas_properties_mend.html',
                              {"graph": graph,
                               "item_type_label": _("Type"),
                               "element_type": element_type,
                               "changed_formset": changed_formset,
                               "deleted_formset": deleted_formset,
                               "changed_props": changed_props,
                               "deleted_props": deleted_props},
                              context_instance=RequestContext(request))


def mend_schema_property(element_type=None, action=None, key=None,
                         new_key=None):

    def _rename_schema_property(element_type=None, key=None, new_key=None):
        if element_type:
            elements = element_type.all()
            for element in elements:
                try:
                    element.set(new_key, element.get(key))
                    element.delete(key)
                except KeyError:
                    pass

    def _delete_schema_property(element_type=None, key=None):
        if element_type:
            elements = element_type.all()
            for element in elements:
                try:
                    element.delete(key)
                except KeyError:
                    pass

    if action == 'rename':
        _rename_schema_property(element_type, key, new_key)
    elif action == 'delete':
        _delete_schema_property(element_type, key)
