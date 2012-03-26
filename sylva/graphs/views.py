# -*- coding: utf-8 -*-
import simplejson

from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import (get_object_or_404, render_to_response, redirect,
                                HttpResponse, HttpResponseRedirect)
from django.template import RequestContext

from guardian import shortcuts as guardian
from guardian.decorators import permission_required

from data.models import Data
from graphs.forms import GraphForm, AddCollaboratorForm
from graphs.models import Graph, PERMISSIONS
from schemas.models import Schema, RelationshipType, NodeType

@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"))
def graph_view(request, graph_slug):

    def jsonify_graph(graph, n_elements):
        """
        Returns a tuple with the format (nodes, edges) with the 
        elements of a subgraph jsonified.
        The subgraph is composed by the first random "n_elements"
        nodes traversed from the first one
        """
        nodes = {}
        edges = []
        for n in graph.nodes.iterator():
            if n.display not in nodes:
                nodes[n.display] = n.to_json()
                for r in n.relationships.all():
                    labels = RelationshipType.objects.filter(id=r.label)
                    if labels:
                        nodes[r.target.display] = r.target.to_json()
                        edges.append(r.to_json())
                        if len(nodes) >= n_elements: break
            if len(nodes) >= n_elements: break
        return (nodes, edges)
        

    graph = get_object_or_404(Graph, slug=graph_slug)
    nodes, edges = jsonify_graph(graph, settings.PREVIEW_NODES)
    return render_to_response('graphs_view.html',
                              {"graph": graph,
                                "nodes": simplejson.dumps(nodes),
                                "edges": simplejson.dumps(edges)},
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
                instance = form.cleaned_data["instance"]
                graph = form.save(commit=False)
                graph.save()
            redirect_url = reverse("graph_view", args=[graph.slug])
            return redirect(redirect_url)
    return render_to_response('graphs_edit.html',
                              {"graph": graph,
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


@permission_required("graphs.change_collaborators", (Graph, "slug", "graph_slug"))
def graph_collaborators(request, graph_slug):
    # Only graph owner should be able to do this
    graph = get_object_or_404(Graph, slug=graph_slug)
    if request.user != graph.owner:
        return redirect('%s?next=%s' % (reverse("signin"), request.path))
    users = User.objects.all().exclude(pk=settings.ANONYMOUS_USER_ID)
    all_collaborators = guardian.get_users_with_perms(graph)
    collaborators = list(all_collaborators.exclude(id__in=[request.user.id,
                                                   settings.ANONYMOUS_USER_ID]))
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
    return HttpResponse(simplejson.dumps({}))


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
    return HttpResponse(simplejson.dumps(node_neighbors))
