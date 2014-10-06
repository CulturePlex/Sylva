# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse)
from django.template import RequestContext
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from sylva.decorators import is_enabled
from graphs.models import Data, Graph
from queries.grammar import QueryParser
from schemas.models import NodeType, RelationshipType
from queries.forms import SaveQueryForm

# from .parser import parse_query
ASC = "asc"
DESC = "desc"


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_list(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    # We create the variables in the session
    request.session['query'] = None
    request.session['query_aliases'] = None
    request.session['query_fields'] = None
    request.session['results_count'] = None
    # We add order for the list of queries
    order_by = request.GET.get('order_by', 'default')
    order_dir = request.GET.get('dir', 'desc')
    if order_by == 'default':
        queries = graph.queries.all()
    else:
        if order_dir == 'desc':
            order_dir = 'asc'
            reverse_order = True
        elif order_dir == 'asc':
            order_dir = 'desc'
            reverse_order = False
        queries = graph.queries.all().order_by(order_by)
        queries = sorted(queries, reverse=reverse_order)
        if not queries:
            messages.error(request,
                           _("Error: You are trying to sort a \
                             column with some none values"))
            queries = graph.queries.all()
    return render_to_response('queries/queries_list.html',
                              {"graph": graph,
                               "queries": queries,
                               "dir": order_dir,
                               "order_by": order_by},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_new(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(schema__graph__slug=graph_slug)
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    form = SaveQueryForm()
    # We get the query_dicts of the session variable if they exist
    query_dict = request.session['query']
    query_aliases = request.session['query_aliases']
    query_fields = request.session['query_fields']
    if request.POST:
        data = request.POST.copy()
        form = SaveQueryForm(data=data)
        if form.is_valid():
            with transaction.atomic():
                query = form.save(commit=False)
                graph.queries.add(query)
                # We treat the results_count
                results_count = request.session['results_count']
                if results_count:
                    query.results_count = results_count
                    query.last_run = datetime.now()
                else:
                    query.results_count = 0
                query.save()
                graph.save()
                return render_to_response('queries/queries_list.html',
                                          {"graph": graph,
                                           "queries_link": queries_link,
                                           "queries": graph.queries.all()},
                                          context_instance=RequestContext(
                                              request))
    else:
        return render_to_response('queries/queries_new.html',
                                  {"graph": graph,
                                   "queries_link": queries_link,
                                   "node_types": nodetypes,
                                   "relationship_types": reltypes,
                                   "form": form,
                                   "query_dict": query_dict,
                                   "query_aliases": query_aliases,
                                   "query_fields": query_fields},
                                  context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_new_results(request, graph_slug):
    # We get the information to mantain the las query in the builder
    query = request.POST.get("query", "").strip()
    query_aliases = request.POST.get("query_aliases", "").strip()
    query_fields = request.POST.get("query_fields", "").strip()
    request.session['query'] = query
    request.session['query_aliases'] = query_aliases
    request.session['query_fields'] = query_fields

    graph = get_object_or_404(Graph, slug=graph_slug)
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    queries_new = (reverse("queries_new", args=[graph.slug]),
                   _("New"))
    # query = "notas of autor with notas that start with lista"
    # see https://gist.github.com/versae/9241069
    query_dict = json.loads(query)
    query_results = graph.query(query_dict, headers=True)
    headers = True
    results = [r for r in query_results]
    # We store the results count in the session variable.
    # The ' - 1' is because the headers
    request.session['results_count'] = len(results) - 1
    # TODO: Try to make the response streamed
    return render_to_response('queries/queries_new_results.html',
                              {"graph": graph,
                               "queries_link": queries_link,
                               "queries_new": queries_new,
                               "headers": headers,
                               "results": results},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_edit(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(
        schema__graph__slug=graph_slug)
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    query = graph.queries.get(pk=query_id)
    # We check if we are going to edit the query
    if request.POST:
        data = request.POST.copy()
        form = SaveQueryForm(data=data, instance=query)
        if form.is_valid():
            with transaction.atomic():
                query = form.save(commit=False)
                # We treat the results_count
                results_count = request.session["results_count"]
                if results_count:
                    query.results_count = results_count
                    query.last_run = datetime.now()
                else:
                    query.results_count = 0
                query.save()
                return render_to_response('queries/queries_list.html',
                                          {"graph": graph,
                                           "queries": graph.queries.all()},
                                          context_instance=RequestContext(
                                              request))
    # We have to get the values of the query to introduce them into the form
    form = SaveQueryForm(instance=query)
    query_dict = json.dumps(query.query_dict)
    query_aliases = json.dumps(query.query_aliases)
    query_fields = json.dumps(query.query_fields)
    return render_to_response('queries/queries_new.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes,
                               "queries_link": queries_link,
                               "form": form,
                               "query_dict": query_dict,
                               "query_aliases": query_aliases,
                               "query_fields": query_fields},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_results(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    query = graph.queries.get(pk=query_id)
    # query = "notas of autor with notas that start with lista"
    # see https://gist.github.com/versae/9241069
    results = graph.query(query.query_dict, headers=True)
    headers = True
    # json_results = json.dumps([r for r in results])
    # TODO: Try to make the response streamed
    return render_to_response('queries/queries_new_results.html',
                              {"graph": graph,
                               "queries_link": queries_link,
                               "headers": headers,
                               "results": results},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    return render_to_response('queries/queries_query.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def parse_query_results(request, graph_slug):
    query = request.POST.get("query", "").strip()
    if request.is_ajax() and query:
        graph = get_object_or_404(Graph, slug=graph_slug)
        query_parser = QueryParser(graph)
        # query = "notas of autor with notas that start with lista"
        # see https://gist.github.com/versae/9241069
        query_dict = query_parser.parse(unicode(query))
        results = graph.query(query_dict)
        # json_results = json.dumps([r for r in results])
        # TODO: Try to make the response streamed
        # return render_to_response('queries/queries_new_results.html',
        #                           {"results": json_results},
        #                           context_instance=RequestContext(request))
        return HttpResponse(json.dumps([r for r in results]),
                            status=200,
                            mimetype='application/json')


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_query_collaborators(request, graph_slug):
    if request.is_ajax() and "term" in request.GET:
        graph = get_object_or_404(Graph, slug=graph_slug)
        term = request.GET["term"]
        if graph and term:
            #collabs = graph.get_collaborators(include_anonymous=True,
            #                                  as_queryset=True)
            lookups = (Q(username__icontains=term) |
                       Q(first_name__icontains=term) |
                       Q(last_name__icontains=term) |
                       Q(email__icontains=term))
            no_collabs = User.objects.filter(lookups)
            no_collabs = no_collabs.exclude(id=request.user.id)
            collabs_dict = {}
            for collab in no_collabs:
                collabs_dict = {}
                full_name = collab.get_full_name()
                if full_name:
                    name = u"%s (%s)" % (full_name, collab.username)
                else:
                    name = collab.username
                    collabs_dict[collab.id] = name
            return HttpResponse(json.dumps(collabs_dict))
    return HttpResponse(json.dumps({}))
