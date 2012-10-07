# -*- coding: utf-8 -*-
import json

from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import (get_object_or_404, render_to_response, redirect,
                              HttpResponse)
from django.utils.translation import gettext as _
from django.template import RequestContext

from guardian import shortcuts as guardian
from guardian.decorators import permission_required

from data.models import Data
from graphs.forms import (GraphForm, GraphDeleteConfirmForm, GraphCloneForm,
                          AddCollaboratorForm)
from graphs.models import Graph, PERMISSIONS
from schemas.models import Schema


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"))
def graph_view(request, graph_slug):

    def jsonify_graph(graph, n_elements=settings.PREVIEW_NODES, full=False):
        """
        Returns a tuple with the elements of a subgraph jsonified. The format
        is (nodes, edges, preview_nodes, preview_edges)
        The preview subgraph is composed by the first random "n_elements"
        nodes traversed from the first one
        """
        nodes = {}
        edges = []
        partial_edges = []
        partial_nodes = {}
        partial_nodes_ids = []
        nodes_display = {}
        for node in graph.nodes.all():
            json_node = node.to_json()
            nodes[node.display] = json_node
            nodes_display[node.id] = node.display
        for rel in graph.relationships.all():
            source_id = rel.source.id
            target_id = rel.target.id
            if (source_id in nodes_display
                    and target_id in nodes_display):
                edge = {
                    'id': rel.id,
                    'source': nodes_display[source_id],
                    'type': rel.label_display,
                    'target': nodes_display[target_id],
                    'properties': rel.properties
                }
                edges.append(edge)
                if len(partial_nodes_ids) <= n_elements:
                    if source_id not in partial_nodes_ids:
                        node_display = nodes_display[source_id]
                        partial_nodes[node_display] = nodes[node_display]
                        partial_nodes_ids.append(source_id)
                    elif target_id not in partial_nodes_ids:
                        node_display = nodes_display[target_id]
                        partial_nodes[node_display] = nodes[node_display]
                        partial_nodes_ids.append(target_id)
                if (source_id in partial_nodes_ids
                        and target_id in partial_nodes_ids):
                    partial_edges.append(edge)
        return (nodes, edges, partial_nodes, partial_edges)

    graph = get_object_or_404(Graph, slug=graph_slug)

    total_nodes, total_edges, nodes, edges = jsonify_graph(graph)
    size = graph.nodes.count()
    return render_to_response('graphs_view.html',
                              {"graph": graph,
                               "nodes": json.dumps(nodes),
                               "edges": json.dumps(edges),
                               "total_nodes": json.dumps(total_nodes),
                               "total_edges": json.dumps(total_edges),
                               "size": size,
                                "MAX_SIZE": settings.MAX_SIZE,
                               },
                              context_instance=RequestContext(request))


@permission_required("graphs.change_graph", (Graph, "slug", "graph_slug"))
def graph_edit(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphForm(user=request.user, instance=graph)
    if request.POST:
        data = request.POST.copy()
        form = GraphForm(data=data, user=request.user, instance=graph)
        if form.is_valid():
            with transaction.commit_on_success():
                # instance = form.cleaned_data["instance"]
                graph = form.save(commit=False)
                graph.save()
            redirect_url = reverse("graph_view", args=[graph.slug])
            return redirect(redirect_url)
    remove = bool(request.GET.get("remove", False))
    return render_to_response('graphs_edit.html',
                              {"graph": graph,
                               "remove": remove,
                               "form": form},
                              context_instance=RequestContext(request))


@permission_required("graphs.change_graph", (Graph, "slug", "graph_slug"))
def graph_delete(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphDeleteConfirmForm()
    if request.POST:
        data = request.POST.copy()
        form = GraphDeleteConfirmForm(data=data)
        if form.is_valid():
            confirm = bool(int(form.cleaned_data["confirm"]))
            if confirm:
                graph.relationships.delete()
                graph.nodes.delete()
                graph.delete()
                redirect_url = reverse("dashboard")
            else:
                redirect_url = reverse("graph_view", args=[graph.slug])
            return redirect(redirect_url)
    remove = bool(request.GET.get("remove", False))
    return render_to_response('graphs_delete.html',
                              {"graph": graph,
                               "remove": remove,
                               "form": form},
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


@permission_required("schemas.view_schema", (Schema, "graph__slug",
                                             "graph_slug"))
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"))
def graph_clone(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphCloneForm(user=request.user)
    if request.POST:
        form = GraphCloneForm(data=request.POST, user=request.user)
        if form.is_valid():
            with transaction.commit_on_success():
                instance = form.cleaned_data["instance"]
                new_graph = form.save(commit=False)
                new_graph.name = graph.name + " " + _("[cloned]")
                new_graph.description = graph.description
                new_graph.relaxed = graph.relaxed
                new_graph.public = graph.public
                new_graph.order = graph.order
                new_graph.public = graph.public
                new_graph.options = graph.options
                new_graph.owner = request.user
                data = Data.objects.create(instance=instance)
                new_graph.data = data
                schema = Schema.objects.create()
                new_graph.schema = schema
                new_graph.save()
                options = form.cleaned_data["options"]
                clone_data = False
                if options:
                    clone_data = 'data' in options
                graph.clone(new_graph, clone_data=clone_data)
            redirect_url = reverse("dashboard")
            return redirect(redirect_url)
    return render_to_response('graphs_clone.html',
                              {"graph": graph,
                               "form": form},
                              context_instance=RequestContext(request))


@permission_required("graphs.change_collaborators", (Graph, "slug",
                                                     "graph_slug"))
def graph_collaborators(request, graph_slug):
    # Only graph owner should be able to do this
    graph = get_object_or_404(Graph, slug=graph_slug)
    if request.user != graph.owner:
        return redirect('%s?next=%s' % (reverse("signin"), request.path))
    # users = User.objects.all().exclude(pk=settings.ANONYMOUS_USER_ID)
    all_collaborators = guardian.get_users_with_perms(graph)
    collaborators = all_collaborators.exclude(id__in=[request.user.id,
                                              settings.ANONYMOUS_USER_ID])
    collaborators = list(collaborators)
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
    # graph_permissions = guardian.get_perms_for_model(graph)
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


@permission_required("graphs.change_collaborators",
                     (Graph, "slug", "graph_slug"))
def change_permission(request, graph_slug):
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
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
    return HttpResponse(json.dumps({}))


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"))
def expand_node(request, graph_slug, node_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    node = graph.nodes.get(node_id)
    edges = []
    nodes = {}
    for edge in node.relationships.all():
        edges.append(edge.to_json())
        nodes[edge.source.display] = edge.source.to_json()
        nodes[edge.target.display] = edge.target.to_json()
    node_neighbors = {"edges": edges, "nodes": nodes}
    return HttpResponse(json.dumps(node_neighbors))
