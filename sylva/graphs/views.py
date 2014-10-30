# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA


from django.db import transaction, IntegrityError
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import (get_object_or_404, render_to_response, redirect,
                              HttpResponse)
from django.http import Http404
from django.utils.translation import gettext as _
from django.views.decorators.http import condition
from django.template import RequestContext
from django.template.loader import render_to_string
from django.templatetags.static import static

from guardian import shortcuts as guardian
from guardian.decorators import permission_required

from data.models import Data
from graphs.forms import (GraphForm, GraphDeleteConfirmForm, GraphCloneForm,
                          AddCollaboratorForm)
from graphs.models import Graph, PERMISSIONS
from graphs.utils import graph_last_modified
from queries.models import Query
from schemas.models import Schema
from sylva.decorators import is_enabled


def _jsonify_graph(graph, nodes_list, relations_list):
    """
    Returns a tuple with the elements of a graph jsonified. The 'graph'
    parameter is used for obtain all the types.
    """
    nodes = []
    rels = []
    nodetypes = {}
    reltypes = {}
    node_ids = []
    for nodetype in graph.schema.nodetype_set.all():
        nodetypes[nodetype.id] = {
            'id': nodetype.id,
            'name': nodetype.name,
            'color': nodetype.get_color(),
            'nodes': []
        }
    for reltype in graph.schema.relationshiptype_set.all():
        reltypes[reltype.id] = {
            'id': reltype.id,
            'name': reltype.name,
            'fullName': reltype.__unicode__(),
            'sourceName': reltype.source.name,
            'targetName': reltype.target.name,
            'color': reltype.get_color(),
            'colorMode': reltype.get_color_mode(),
            'relationships': []
        }
    for node in nodes_list:
        nodes.append(node.to_json())
        node_ids.append(str(node.id))
        nodetype = node.get_type()
        nodetypes[nodetype.id]['nodes'].append(str(node.id))
    for rel in relations_list:
        source_id = rel.source.id
        target_id = rel.target.id
        if (str(source_id) in node_ids and str(target_id) in node_ids):
            rel_json = rel.to_json()
            rels.append(rel_json)
            reltype = rel.get_type()
            reltypes[reltype.id]['relationships'].append(rel_json['id'])
    graph = {'nodes': nodes, 'edges': rels}
    return (graph, nodetypes, reltypes, node_ids)


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_view(request, graph_slug, node_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    is_graph_empty = graph.is_empty()
    is_schema_empty = graph.schema.is_empty()
    view_graph_ajax_url = ''
    edit_nodetype_color_ajax_url = reverse(
        'schemas.views.schema_nodetype_edit_color', args=[graph.slug])
    edit_reltype_color_ajax_url = reverse(
        'schemas.views.schema_reltype_edit_color', args=[graph.slug])
    graph_analytics_boxes_edit_position_url = reverse(
        'graph_analytics_boxes_edit_position', args=[graph.slug])
    run_query_url = reverse('run_query', args=[graph.slug, 0])[:-2]
    node = None
    if node_id:
        node = graph.nodes.get(node_id)
        view_graph_ajax_url = reverse('nodes_data',
                                      args=[graph.slug, node_id])
    else:
        view_graph_ajax_url = reverse('graph_data', args=[graph.slug])
    return render_to_response('graphs_view.html',
                              {"graph": graph,
                               "is_graph_empty": is_graph_empty,
                               "is_schema_empty": is_schema_empty,
                               "MAX_SIZE": settings.MAX_SIZE,
                               "node": node,
                               "view_graph_ajax_url":
                                  view_graph_ajax_url,
                               "edit_nodetype_color_ajax_url":
                                  edit_nodetype_color_ajax_url,
                               "edit_reltype_color_ajax_url":
                                  edit_reltype_color_ajax_url,
                               "graph_analytics_boxes_edit_position_url":
                                  graph_analytics_boxes_edit_position_url,
                               "run_query_url":
                                  run_query_url},
                              context_instance=RequestContext(request))


@permission_required("graphs.change_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_edit(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphForm(user=request.user, instance=graph)
    if request.POST:
        data = request.POST.copy()
        form = GraphForm(data=data, user=request.user, instance=graph)
        if form.is_valid():
            with transaction.atomic():
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


@permission_required("graphs.change_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_delete(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphDeleteConfirmForm()
    if request.POST:
        data = request.POST.copy()
        form = GraphDeleteConfirmForm(data=data)
        if form.is_valid():
            confirm = bool(int(form.cleaned_data["confirm"]))
            if confirm:
                graph.destroy()
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
            with transaction.atomic():
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


@is_enabled(settings.ENABLE_CLONING)
@login_required
@permission_required("schemas.view_schema", (Schema, "graph__slug",
                                             "graph_slug"),
                     return_403=True)
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_clone(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    form = GraphCloneForm(user=request.user)
    if request.POST:
        form = GraphCloneForm(data=request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                instance = form.cleaned_data["instance"]
                new_graph = form.save(commit=False)
                new_graph.name = graph.name + " " + _("[cloned]")
                new_graph.description = graph.description
                new_graph.relaxed = graph.relaxed
                new_graph.order = graph.order
                new_graph.public = graph.public
                new_graph.options = graph.options
                new_graph.owner = request.user
                data = Data.objects.create(instance=instance)
                new_graph.data = data
                schema = Schema.objects.create()
                new_graph.schema = schema
                try:
                    new_graph.save()
                except IntegrityError:
                    import time
                    new_graph.name += " " + str(int(time.time()))
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
                                                     "graph_slug"),
                     return_403=True)
def graph_collaborators(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    # Only graph owner was able to change collaborators
    # if request.user != graph.owner:
    #     return redirect('%s?next=%s' % (reverse("signin"), request.path))
    # users = User.objects.all().exclude(pk=settings.ANONYMOUS_USER_ID)
    all_collaborators = guardian.get_users_with_perms(graph)
    collaborators = all_collaborators.exclude(
        id__in=[graph.owner.id, request.user.id, settings.ANONYMOUS_USER_ID]
    )
    collaborators = list(collaborators)
    if request.POST:
        data = request.POST.copy()
        form = AddCollaboratorForm(data=data, graph=graph)
        if form.is_valid():
            new_collaborator = form.cleaned_data["new_collaborator"]
            guardian.assign_perm('view_graph', new_collaborator, graph)
            collaborators.append(new_collaborator)
        as_modal = bool(data.get("asModal", False))
    else:
        form = AddCollaboratorForm(graph=graph)
        as_modal = bool(request.GET.get("asModal", False))
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
    '''
    For the modal mini-framework, this view always returns an HTML, because
    after click in 'Add collaborator' it goes again the same page.
    '''
    if as_modal:
        base_template = 'empty.html'
        render = render_to_string
    else:
        base_template = 'base.html'
        render = render_to_response
    add_url = reverse("graph_collaborators", args=[graph_slug])
    broader_context = {"graph": graph,
                       "permissions": permissions_list,
                       "permissions_table": permissions_table,
                       "form": form,
                       "base_template": base_template,
                       "as_modal": as_modal,
                       "add_url": add_url}
    response = render('graphs_collaborators.html', broader_context,
                      context_instance=RequestContext(request))
    if as_modal:
        response = {'type': 'html',
                    'action': 'collaborators',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


@permission_required("graphs.change_collaborators",
                     (Graph, "slug", "graph_slug"), return_403=True)
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
                guardian.assign_perm(permission_str, user, aux[object_str])
        else:
            raise ValueError("Unknown %s permission: %s" % (object_str,
                                                            permission_str))
    return HttpResponse(json.dumps({}))


@permission_required("graphs.change_collaborators",
                     (Graph, "slug", "graph_slug"), return_403=True)
def graph_ajax_collaborators(request, graph_slug):
    if request.is_ajax() and "term" in request.GET:
        graph = get_object_or_404(Graph, slug=graph_slug)
        term = request.GET["term"]
        if graph and term:
            collabs = graph.get_collaborators(include_anonymous=True,
                                              as_queryset=True)
            lookups = (Q(username__icontains=term) |
                       Q(first_name__icontains=term) |
                       Q(last_name__icontains=term) |
                       Q(email__icontains=term))
            no_collabs = User.objects.filter(lookups)
            no_collabs = no_collabs.exclude(id=request.user.id)
            no_collabs = no_collabs.exclude(id__in=collabs)
            no_collabs_dict = {}
            for no_collab in no_collabs:
                full_name = no_collab.get_full_name()
                if full_name:
                    name = u"%s (%s)" % (full_name, no_collab.username)
                else:
                    name = no_collab.username
                no_collabs_dict[no_collab.id] = name
            return HttpResponse(json.dumps(no_collabs_dict))
    return HttpResponse(json.dumps({}))


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
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


@condition(last_modified_func=graph_last_modified)
@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_data(request, graph_slug, node_id=None):
    if (request.is_ajax() or settings.DEBUG):
        graph = get_object_or_404(Graph, slug=graph_slug)
        node = None
        nodes_list = []
        relations_list = []
        if node_id:
            node = graph.nodes.get(node_id)
            nodes_list = [node]
            relations_list = node.relationships.all()
            for rel in relations_list:
                if rel.source == node:
                    nodes_list.append(rel.target)
                else:
                    nodes_list.append(rel.source)
        else:
            nodes_list = graph.nodes.all()
            relations_list = graph.relationships.all()
        graph_json, nodetypes, reltypes, node_ids = _jsonify_graph(
            graph, nodes_list, relations_list)
        size = len(nodes_list)
        collapsibles = []
        positions = {}
        if 'collapsibles' in graph.get_options():
            collapsibles = graph.get_option('collapsibles')
            positions = graph.get_option('positions')
        search_loading_image = static('img/loading_24.gif')
        queries = {query.id: query.name
                   for query in graph.queries.order_by('-id')[:10].reverse()}
        # Maybe we can change the previous line if the query object would have
        # a mod_date.
        json_data = {
            'graph': graph_json,
            'nodetypes': nodetypes,
            'reltypes': reltypes,
            'nodeIds': node_ids,
            'size': size,
            'collapsibles': collapsibles,
            'positions': positions,
            'searchLoadingImage': search_loading_image,
            'queries': queries
        }
        return HttpResponse(json.dumps(json_data), status=200,
                            content_type='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX request)"))


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def graph_analytics_boxes_edit_position(request, graph_slug):
    if ((request.is_ajax() or settings.DEBUG) and request.POST):
        data = request.POST.copy()
        params = None
        for key in data:
            params = key
            break
        params = json.decode(params)
        graph = get_object_or_404(Graph, slug=graph_slug)
        with transaction.atomic():
            graph.set_option('collapsibles', params['collapsibles'])
            graph.set_option('positions', params['positions'])
            graph.save()
        return HttpResponse(status=200, content_type='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX POST request)"))


@permission_required("graphs.view_graph", (Graph, "slug", "graph_slug"),
                     return_403=True)
def run_query(request, graph_slug, query_id):
    if (request.is_ajax() or settings.DEBUG):
        get_object_or_404(Graph, slug=graph_slug)  # Only for checking
        query = get_object_or_404(Query, id=query_id)
        try:
            node_ids = query.execute(only_ids=True)
        except:
            node_ids = []
            print 'An error ocurred during the query execution'
        dev = []
        if node_ids:
            dev = [str(id) for sublist in node_ids for id in sublist]
            dev = sorted(set(dev))
        response = {'nodeIds': dev}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    raise Http404(_("Error: Invalid request (expected an AJAX POST request)"))
