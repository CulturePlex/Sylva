# -*- coding: utf-8 -*-
import simplejson

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import (get_object_or_404, render_to_response, redirect,
                                HttpResponse, HttpResponseRedirect)
from django.template import RequestContext

from guardian import shortcuts as guardian

from data.models import Data
from graphs.forms import GraphForm, AddCollaboratorForm
from graphs.models import Graph, PERMISSIONS
from schemas.models import Schema


@login_required()
def graph_view(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    return render_to_response('graphs_view.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))


@login_required()
def graph_edit(request, graph_id):
    return render_to_response('graphs_edit.html',
                              {},
                              context_instance=RequestContext(request))


@login_required()
def graph_create(request):
    form = GraphForm(user=request.user)
    if request.POST:
        data = request.POST.copy()
        form = GraphForm(data=data, user=request.user)
        if form.is_valid():
            with transaction.commit_on_success(): 
                instance = form.cleaned_data["instance"]
                graph = form.save(commit=False)
                graph.owner = request.user
                data = Data.objects.create(instance=instance)
                graph.data = data
                schema = Schema.objects.create()
                graph.schema = schema
                graph.save()
            redirect_url = reverse("dashboard")
            return redirect(redirect_url)
    return render_to_response('graphs_create.html',
                              {"form": form},
                              context_instance=RequestContext(request))


@login_required()
def graph_collaborators(request, graph_id):
    # Only graph owner should be able to do this
    graph = get_object_or_404(Graph, id=graph_id)
    if request.user != graph.owner:
        return redirect('%s?next=%s' % (reverse("signin"), request.path))
    users = User.objects.all()
    collaborators = list(guardian.get_users_with_perms(graph))
    if request.POST:
        data = request.POST.copy()
        form = AddCollaboratorForm(data=data, graph=graph,
                                collaborators=collaborators)
        if form.is_valid():
            user_id = form.cleaned_data["new_collaborator"]
            user = get_object_or_404(User, id=user_id)
            guardian.assign('view_graph', user, graph)
            collaborators.append(user)
    else:
        form = AddCollaboratorForm(graph=graph, collaborators=collaborators)
    graph_permissions = guardian.get_perms_for_model(graph)
    permissions_list = []
    permissions_table = []
    aux = (('graph', graph), ('schema', graph.schema), ('data', graph.data))
    for item in aux:
        for p in PERMISSIONS[item[0]].values():
            permissions_list.append(p)
    for user in collaborators:
        permission_row = {}
        permission_row['user_id'] = user.id
        permission_row['user_name'] = user.username
        permission_row['perms'] = []
        for item_str, item_obj in aux:
            user_permissions = guardian.get_perms(user, item_obj)
            for p in PERMISSIONS[item_str].keys():
                if p in user_permissions:
                    permission_row['perms'].append((item_str, p, True))
                else:
                    permission_row['perms'].append((item_str, p, False))
        permissions_table.append(permission_row) 
    #users = [u for u in users if u != graph.owner and u not in collaborators]
    return render_to_response('graphs_collaborators.html',
                              {"graph": graph,
                                  "permissions": permissions_list,
                                  "permissions_table": permissions_table,
                                  "form": form},
                              context_instance=RequestContext(request))


@login_required()
def change_permission(request, graph_id):
    if request.is_ajax():
        graph = get_object_or_404(Graph, id=graph_id)
        user_id = request.GET['user_id']
        object_str = request.GET['object_str']
        permission_str = request.GET['permission_str']
        user = get_object_or_404(User, id=user_id)
        # Owner permissions cannot be deleted
        if user == graph.owner:
            return HttpResponse("owner", status=500)
        aux = {'graph': graph,
                'schema': graph.schema,
                'data': graph.data}
        if permission_str in PERMISSIONS[object_str]:
            if permission_str in guardian.get_perms(user, aux[object_str]):
                guardian.remove_perm(permission_str, user, aux[object_str])
            else:
                guardian.assign(permission_str, user, aux[object_str])
        else:
            raise ValueError("Unknown %s permission: %s" % (object_str,
                                                            permission_str))
    return HttpResponse(simplejson.dumps({}))


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
