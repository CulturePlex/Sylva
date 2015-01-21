# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import (get_object_or_404, render_to_response, redirect,
                              HttpResponse)
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from sylva.decorators import is_enabled
from graphs.models import Data, Graph
from queries.grammar import QueryParser
from schemas.models import NodeType, RelationshipType
from queries.forms import (SaveQueryForm, QueryDeleteConfirmForm,
                           QueryOptionsForm)

# from .parser import parse_query

# Constants

AGGREGATE = 'aggregate'
AGGREGATES = ["Count", "Max", "Min", "Sum", "Average", "Deviation"]
ASC = 'asc'
DEFAULT = 'default'
DEFAULT_ROWS_NUMBER = 100
DEFAULT_SHOW_MODE = "per_page"
DESC = 'desc'
ID = 'id'
NEW = 'new'
NEW_QUERY = 'new_query'
NO_ORDER = 'no_order'
ORDER_DIR_ASC = ''
ORDER_DIR_DESC = '-'


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_list(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)

    # We create the variables in the session
    request.session['query_id'] = None
    request.session['query'] = None
    request.session['query_aliases'] = None
    request.session['query_fields'] = None
    request.session['results_count'] = None
    request.session['data'] = None

    # We add order for the list of queries
    order_by_field = request.GET.get('order_by', 'id')
    order_dir = request.GET.get('dir', '-')
    page_dir = request.GET.get('page_dir', '-')
    # We get the modal variable
    as_modal = bool(request.GET.get("asModal", False))

    if order_by_field == ID:
        queries = graph.queries.all()
    else:
        page_dir = order_dir
        order_by = "{0}{1}".format(order_dir, order_by_field)
        queries = graph.queries.all().order_by(order_by)
        if not queries:
            messages.error(request,
                           _("Error: You are trying to sort a \
                              column with some none values"))
            queries = graph.queries.all()
        elif order_dir == ORDER_DIR_ASC:
            order_dir = ORDER_DIR_DESC
        elif order_dir == ORDER_DIR_DESC:
            order_dir = ORDER_DIR_ASC

    # We add pagination for the list of queries
    page = request.GET.get('page')
    page_size = settings.DATA_PAGE_SIZE
    paginator = Paginator(queries, page_size)
    try:
        paginated_queries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_queries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_queries = paginator.page(paginator.num_pages)

    if as_modal:
        base_template = 'empty.html'
        render = render_to_string
    else:
        base_template = 'base.html'
        render = render_to_response
    add_url = reverse("queries_list", args=[graph_slug])
    broader_context = {"graph": graph,
                       "queries": paginated_queries,
                       "order_by": order_by_field,
                       "dir": order_dir,
                       "page_dir": page_dir,
                       "base_template": base_template,
                       "as_modal": as_modal,
                       "add_url": add_url}
    response = render('queries/queries_list.html', broader_context,
                      context_instance=RequestContext(request))
    if as_modal:
        response = {'type': 'html',
                    'action': 'queries_list',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_new(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(schema__graph__slug=graph_slug)
    redirect_url = reverse("queries_list", args=[graph.slug])

    # We declare the forms needed
    form = SaveQueryForm()
    query_options_form = QueryOptionsForm()
    # Breadcrumbs variable
    queries_link = (redirect_url, _("Queries"))
    # We get the modal variable
    as_modal = bool(request.GET.get("asModal", False))
    # We get the query_dicts of the session variable if they exist
    query_id = request.session.get('query_id', None)
    query_dict = None
    query_aliases = None
    query_fields = None
    # Variable to control the save as new to show the form
    save_as_new = False

    # We check if we have the variables in the request.session
    if 'query_id' not in request.session:
        request.session['query_id'] = None
    if 'query' not in request.session:
        request.session['query'] = None
    if 'query_aliases' not in request.session:
        request.session['query_aliases'] = None
    if 'query_fields' not in request.session:
        request.session['query_fields'] = None
    if 'results_count' not in request.session:
        request.session['results_count'] = None

    # If query_id is 'new' means that we need to get the variables of the
    # session to load the query
    if query_id == NEW:
        query_dict = request.session.get('query', None)
        query_aliases = request.session.get('query_aliases', None)
        query_fields = request.session.get('query_fields', None)
        # We need to check the name and the description for the save as new
        query_name = request.session.get('query_name', None)
        query_description = request.session.get('query_description', None)
        # Variable save as new equals to True
        save_as_new = True

        # We create the data dictionary for the form for the save as new
        data = dict()
        data['graph'] = graph
        data['name'] = query_name
        data['description'] = query_description
        data['query_dict'] = query_dict
        data['query_fields'] = query_fields
        data['query_aliases'] = query_aliases
        data['results_count'] = 0
        data['last_run'] = datetime.now()

        # And we add the data to the form
        form = SaveQueryForm(data=data)

    if request.POST:
        data = request.POST.copy()
        form = SaveQueryForm(data=data)
        if form.is_valid():
            with transaction.atomic():
                query = form.save(commit=False)
                graph.queries.add(query)
                # We treat the results_count
                results_count = request.session.get('results_count', None)
                if results_count:
                    query.results_count = results_count
                    query.last_run = datetime.now()
                else:
                    query.results_count = 0
                query.save()
                graph.save()
                return redirect(redirect_url)
    else:
        if as_modal:
            base_template = 'empty.html'
            render = render_to_string
        else:
            base_template = 'base.html'
            render = render_to_response
        add_url = reverse("queries_new", args=[graph_slug])
        broader_context = {"graph": graph,
                           "queries_link": queries_link,
                           "node_types": nodetypes,
                           "relationship_types": reltypes,
                           "form": form,
                           "query_options_form": query_options_form,
                           "save_as_new": save_as_new,
                           "query_dict": query_dict,
                           "query_aliases": query_aliases,
                           "query_fields": query_fields,
                           "base_template": base_template,
                           "as_modal": as_modal,
                           "add_url": add_url}
        response = render('queries/queries_new.html', broader_context,
                          context_instance=RequestContext(request))
        if as_modal:
            response = {'type': 'html',
                        'action': 'queries_new',
                        'html': response}
            return HttpResponse(json.dumps(response), status=200,
                                content_type='application/json')
        else:
            return response


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_new_results(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)

    # Breadcrumbs variables
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    queries_new = (reverse("queries_new", args=[graph.slug]),
                   _("New"))
    # We declare the form with the results options
    form = QueryOptionsForm()
    # We get the order
    order_by_field = request.GET.get('order_by', 'default')
    order_dir = request.GET.get('dir', 'desc')
    page_dir = request.GET.get('page_dir', 'desc')
    select_order_by = None
    # We get the modal variable
    as_modal = bool(request.GET.get("asModal", False))
    # We get the information to mantain the last query in the builder
    query = request.POST.get("query", "").strip()
    query_aliases = request.POST.get("query_aliases", "").strip()
    query_fields = request.POST.get("query_fields", "").strip()

    request.session['query_id'] = NEW
    if query is not '':
        request.session['query'] = query
        request.session['query_aliases'] = query_aliases
        request.session['query_fields'] = query_fields
        query_dict = json.loads(query)
    else:
        query_dict = json.loads(request.session.get('query', None))

    # We check if we have options in the form or we use saved options
    if request.POST:
        data = request.POST.copy()
        request.session['data'] = data
        # We add the new choice in the form
        new_choice_order_by = data.get('select_order_by')
        form = QueryOptionsForm(data=data,
                                new_choice=new_choice_order_by)
        if form.is_valid():
            rows_number = form.cleaned_data["rows_number"]
            show_mode = form.cleaned_data["show_mode"]
            select_order_by = form.cleaned_data["select_order_by"]
            dir_order_by = form.cleaned_data["dir_order_by"]
    else:
        data = request.session.get('data', None)
        # We add the new choice in the form
        new_choice_order_by = data.get('select_order_by')
        form = QueryOptionsForm(data=data,
                                new_choice=new_choice_order_by)
        if form.is_valid():
            rows_number = form.cleaned_data["rows_number"]
            show_mode = form.cleaned_data["show_mode"]
            select_order_by = form.cleaned_data["select_order_by"]
            dir_order_by = form.cleaned_data["dir_order_by"]

    headers = True
    if order_by_field == DEFAULT and select_order_by == DEFAULT:
        query_results = graph.query(query_dict, headers=headers)
    elif order_by_field == NO_ORDER:
        query_results = graph.query(query_dict, headers=headers)
    else:
        if order_by_field == DEFAULT and select_order_by != DEFAULT:
            order_by_field = select_order_by
            order_dir = dir_order_by
        page_dir = order_dir
        # We check the properties of the results to see if we have
        # aggregates. This is for a special treatment in the order_by.
        aggregate = order_by_field.split('(')[0]
        has_aggregate = aggregate in AGGREGATES
        if has_aggregate:
            alias = AGGREGATE
            value = order_by_field.replace('`', '')
            order_by = (alias, value, order_dir)
        else:
            # We split the header to get the alias and the property
            order_by_values = order_by_field.split('.')
            alias = order_by_values[0]
            prop = order_by_values[1]
            order_by = (alias, prop, order_dir)
        query_results = graph.query(query_dict,
                                    order_by=order_by, headers=headers)
        if not query_results:
            messages.error(request,
                           _("Error: You are trying to sort a \
                              column with some none values"))
            query_results = graph.query(query_dict, headers=headers)
        # We need the order_dir for the icons in the frontend
        if order_dir == ASC:
            order_dir = DESC
        elif order_dir == DESC:
            order_dir = ASC

    # We save the values to export as CSV
    request.session["csv_results"] = query_results
    request.session["query_name"] = NEW_QUERY
    # We store the results count in the session variable.
    query_results_length = len(query_results)
    request.session['results_count'] = query_results_length

    headers_results = []
    if query_results_length > 1:
        # We treat the headers
        if headers:
            # If the results have headers, we get the position 0
            # and then the results.
            headers_results = query_results[0]
        request.session['results_count'] = query_results_length - 1
        query_results = query_results[1:]
    else:
        query_results = []

    # We add pagination for the list of queries
    page = request.GET.get('page', 1)
    try:
        if show_mode == "per_page":
            page_size = rows_number
            paginator = Paginator(query_results, page_size)
        else:
            page_size = settings.DATA_PAGE_SIZE
            query_results = query_results[:rows_number]
            paginator = Paginator(query_results, page_size)
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_results = paginator.page(paginator.num_pages)

    if as_modal:
        base_template = 'empty.html'
        render = render_to_string
    else:
        base_template = 'base.html'
        render = render_to_response
    add_url = reverse("queries_new_results", args=[graph_slug])
    broader_context = {"graph": graph,
                       "queries_link": queries_link,
                       "queries_new": queries_new,
                       "headers": headers_results,
                       "results": paginated_results,
                       "order_by": order_by_field,
                       "dir": order_dir,
                       "page_dir": page_dir,
                       "csv_results": query_results,
                       "base_template": base_template,
                       "as_modal": as_modal,
                       "add_url": add_url}
    response = render('queries/queries_new_results.html', broader_context,
                      context_instance=RequestContext(request))
    if as_modal:
        response = {'type': 'html',
                    'action': 'queries_results',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_edit(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(
        schema__graph__slug=graph_slug)
    redirect_url = reverse("queries_list", args=[graph.slug])
    query = graph.queries.get(pk=query_id)

    # Breadcrumbs variable
    queries_link = (redirect_url, _("Queries"))
    # We get the modal variable
    as_modal = bool(request.GET.get("asModal", False))
    # We declare the form for the results options
    query_options_form = QueryOptionsForm()
    # We get the query_dicts
    query_dict = json.dumps(query.query_dict)
    query_aliases = json.dumps(query.query_aliases)
    query_fields = json.dumps(query.query_fields)

    # We check if we have the variables in the request.session
    if 'query_id' not in request.session \
            or request.session['query_id'] is None:
        request.session['query_id'] = query.id
    if 'query' not in request.session \
            or request.session['query'] is None:
        request.session['query'] = query_dict
    if 'query_aliases' not in request.session \
            or request.session['query_aliases'] is None:
        request.session['query_aliases'] = query_aliases
    if 'query_fields' not in request.session \
            or request.session['query_fields'] is None:
        request.session['query_fields'] = query_fields

    # We get the session query id to check if the dicts saved in the session
    # are for this query
    session_query_id = request.session.get('query_id', None)
    # We check if the query saved and the query edited are different
    # In that case, we use the query edited
    different_queries = query.query_dict != request.session.get('query', None)
    # We compare the session query fields and the new query fields.
    # This is because we can change the sorting params.
    different_sorting_params = (query.query_fields !=
                                request.session.get('query_fields', None))

    # We check if we are going to edit the query
    if request.POST:
        data = request.POST.copy()
        form = SaveQueryForm(data=data, instance=query)
        if form.is_valid():
            with transaction.atomic():
                query = form.save(commit=False)
                # We treat the results_count
                results_count = request.session.get('results_count', None)
                if results_count:
                    query.results_count = results_count
                    query.last_run = datetime.now()
                else:
                    query.results_count = 0
                query.save()
                return redirect(redirect_url)

    # We have to get the values of the query to introduce them into the form
    form = SaveQueryForm(instance=query)

    # If the queries have changed and the id is the same, we use the dicts
    # of the session
    if different_queries and session_query_id == query.id:
        query_dict = request.session.get('query', None)
        query_aliases = request.session.get('query_aliases', None)
        query_fields = request.session.get('query_fields', None)
    if different_sorting_params and session_query_id == query.id:
        query_fields = request.session.get('query_fields', None)

    if as_modal:
        base_template = 'empty.html'
        render = render_to_string
    else:
        base_template = 'base.html'
        render = render_to_response
    add_url = reverse("queries_new", args=[graph_slug])
    broader_context = {"graph": graph,
                       "node_types": nodetypes,
                       "relationship_types": reltypes,
                       "queries_link": queries_link,
                       "query": query,
                       "form": form,
                       "query_options_form": query_options_form,
                       "query_dict": query_dict,
                       "query_aliases": query_aliases,
                       "query_fields": query_fields,
                       "base_template": base_template,
                       "as_modal": as_modal,
                       "add_url": add_url}
    response = render('queries/queries_new.html', broader_context,
                      context_instance=RequestContext(request))
    if as_modal:
        response = {'type': 'html',
                    'action': 'queries_new',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_results(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    query = graph.queries.get(pk=query_id)

    # Breadcrumbs variables
    queries_link = (reverse("queries_list", args=[graph.slug]),
                    _("Queries"))
    queries_name = (reverse("queries_query_edit", args=[graph.slug, query.id]),
                    query.name)
    # We declare the form to get the options for the results table
    form = QueryOptionsForm()
    # We get the information to mantain the last query in the builder
    query_dict = request.POST.get("query", "").strip()
    query_aliases = request.POST.get("query_aliases", "").strip()
    query_fields = request.POST.get("query_fields", "").strip()
    # We get the order
    order_by_field = request.GET.get('order_by', 'default')
    order_dir = request.GET.get('dir', 'desc')
    page_dir = request.GET.get('page_dir', 'desc')

    # Variable to control if the query has changed to show the save
    # buttons
    query_has_changed = False

    # The next comparisions are because we can execute the queries
    # directly from the list of queries. So, we could obtain empty
    # query dicts, empty query fields...

    # We check if the query saved and the query edited are different
    # In that case, we use the query edited
    if query_dict == '' or query_dict is None:
        query_dict = request.session.get('query')
        if query_dict is None:
            query_dict = query.query_dict
    else:
        query_dict = json.loads(query_dict)
    different_queries = query.query_dict != query_dict

    if query_aliases == '' or query_aliases is None:
        query_aliases = request.session.get('query_aliases')
        if query_aliases is None:
            query_aliases = query.query_aliases

    # We compare the session query fields and the new query fields.
    # This is because we can change the sorting params.
    if query_fields == '' or query_fields is None:
        query_fields = request.session.get('query_fields')
        if query_fields is None:
            query_fields = query.query_fields
    else:
        query_fields = json.loads(query_fields)
    different_sorting_params = query.query_fields != query_fields

    # We get the default sorting params values, in case that we execute
    # the query from the list of queries.
    sortingParams = query.query_fields["sortingParams"]
    rows_number = sortingParams["rows_number"]
    show_mode = sortingParams["show_mode"]
    select_order_by = sortingParams["select_order_by"]
    dir_order_by = sortingParams["dir_order_by"]

    # We check if we have options in the form
    if request.POST:
        data = request.POST.copy()
        request.session['data'] = data
        # We add the new choice in the form
        new_choice_order_by = data.get('select_order_by')
        form = QueryOptionsForm(data=data,
                                new_choice=new_choice_order_by)
        if form.is_valid():
            rows_number = form.cleaned_data["rows_number"]
            show_mode = form.cleaned_data["show_mode"]
            select_order_by = form.cleaned_data["select_order_by"]
            dir_order_by = form.cleaned_data["dir_order_by"]
    elif not request.POST and (
            query.id == request.session.get('query_id', None)):
        data = request.session.get('data', None)
        # We add the new choice in the form
        new_choice_order_by = None
        if data:
            new_choice_order_by = data.get('select_order_by', None)
        form = QueryOptionsForm(data=data,
                                new_choice=new_choice_order_by)
        if form.is_valid():
            rows_number = form.cleaned_data["rows_number"]
            show_mode = form.cleaned_data["show_mode"]
            select_order_by = form.cleaned_data["select_order_by"]
            dir_order_by = form.cleaned_data["dir_order_by"]

    headers = True
    # This part of the code is similar to the same part in the
    # "queries_new_results". The main difference are the blocks
    # to check if we have modify the query or the sorting params
    # to change the correspondent values in the session.
    if order_by_field == DEFAULT and select_order_by == DEFAULT:
        if different_queries and (
                query.id == request.session.get('query_id', None)):
            # We check if the type of query_dict is appropiate
            if not isinstance(query_dict, dict):
                query_dict = json.loads(query_dict)
            query_results = graph.query(query_dict, headers=headers)
            request.session['query'] = json.dumps(query_dict)
            request.session['query_aliases'] = query_aliases
            request.session['query_fields'] = query_fields
            # Let's check if the sorting params are different
            if different_sorting_params:
                # We check if the type of query_field is appropiate
                if isinstance(query_fields, dict):
                    query_fields = json.dumps(query_fields)
                request.session['query_fields'] = query_fields
            query_has_changed = True
        else:
            query_results = query.execute(headers=headers)
            request.session['query'] = query.query_dict
            request.session['query_aliases'] = query.query_aliases
            request.session['query_fields'] = query.query_fields
    elif order_by_field == NO_ORDER:
        if different_queries and (
                query.id == request.session.get('query_id', None)):
            # We check if the type of query_dict is appropiate
            if not isinstance(query_dict, dict):
                query_dict = json.loads(query_dict)
            query_results = graph.query(query_dict, headers=headers)
            request.session['query'] = json.dumps(query_dict)
            request.session['query_aliases'] = query_aliases
            request.session['query_fields'] = query_fields
            # Let's check if the sorting params are different
            if different_sorting_params:
                # We check if the type of query_field is appropiate
                if isinstance(query_fields, dict):
                    query_fields = json.dumps(query_fields)
                request.session['query_fields'] = query_fields
            query_has_changed = True
        else:
            query_results = query.execute(headers=headers)
            request.session['query'] = query.query_dict
            request.session['query_aliases'] = query.query_aliases
            request.session['query_fields'] = query.query_fields
    else:
        if order_by_field == DEFAULT and select_order_by != DEFAULT:
            order_by_field = select_order_by
            order_dir = dir_order_by
        page_dir = order_dir
        # We check the properties of the results to see if we have
        # aggregates. This is for a special treatment in the order_by.
        aggregate = order_by_field.split('(')[0]
        has_aggregate = aggregate in AGGREGATES
        if has_aggregate:
            alias = AGGREGATE
            value = order_by_field.replace('`', '')
            order_by = (alias, value, order_dir)
        else:
            # We split the header to get the alias and the property
            order_by_values = order_by_field.split('.')
            alias = order_by_values[0]
            prop = order_by_values[1]
            order_by = (alias, prop, order_dir)
        if different_queries and (
                query.id == request.session.get('query_id', None)):
            # We check if the type of query_dict is appropiate
            if not isinstance(query_dict, dict):
                query_dict = json.loads(query_dict)
            query_results = graph.query(query_dict, order_by=order_by,
                                        headers=headers)
            request.session['query'] = json.dumps(query_dict)
            if query_aliases == "" or query_fields == "":
                query_aliases = request.session['query_aliases']
                query_fields = request.session['query_fields']
            else:
                request.session['query_aliases'] = query_aliases
                # We check if the type of query_field is appropiate
                if isinstance(query_fields, dict):
                    query_fields = json.dumps(query_fields)
                request.session['query_fields'] = query_fields
            query_has_changed = True
        else:
            query_results = query.execute(order_by=order_by, headers=headers)
            # Let's check if the sorting params are different
            if different_sorting_params:
                # We check if the type of query_field is appropiate
                if isinstance(query_fields, dict):
                    query_fields = json.dumps(query_fields)
                request.session['query_fields'] = query_fields
                query_has_changed = True
        if not query_results:
            messages.error(request,
                           _("Error: You are trying to sort a \
                              column with some none values"))
            query_results = query.execute(headers=headers)
        if order_dir == ASC:
            order_dir = DESC
        elif order_dir == DESC:
            order_dir = ASC

    # We assign the query id to the query_id of the session
    request.session['query_id'] = query.id
    # We save the values to export as CSV
    request.session["csv_results"] = query_results
    request.session["query_name"] = query.name

    # We store the results count in the session variable.
    query_results_length = len(query_results)
    request.session['results_count'] = query_results_length
    # We store the datetime of execution
    query.last_run = datetime.now()
    # And then the results
    headers_results = []
    if query_results_length > 1:
        # We treat the headers
        if headers:
            # If the results have headers, we get the position 0
            headers_results = query_results[0]
        request.session['results_count'] = query_results_length - 1
        query_results = query_results[1:]
        # query.results_count = request.session.get('results_count', None)
    else:
        query_results = []

    # We save the new changes of the query
    query.save()

    # We add pagination for the list of queries
    page = request.GET.get('page', 1)
    page_size = rows_number
    try:
        if show_mode == DEFAULT_SHOW_MODE:
            page_size = rows_number
            paginator = Paginator(query_results, page_size)
        else:
            page_size = settings.DATA_PAGE_SIZE
            query_results = query_results[:rows_number]
            paginator = Paginator(query_results, page_size)
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_results = paginator.page(paginator.num_pages)
    # TODO: Try to make the response streamed
    return render_to_response('queries/queries_new_results.html',
                              {"graph": graph,
                               "query": query,
                               "query_has_changed": query_has_changed,
                               "queries_link": queries_link,
                               "queries_name": queries_name,
                               "headers": headers_results,
                               "results": paginated_results,
                               "order_by": order_by_field,
                               "dir": order_dir,
                               "page_dir": page_dir,
                               "csv_results": query_results},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_delete(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    query = graph.queries.get(id=query_id)
    redirect_url = reverse("queries_list", args=[graph.slug])
    # Breadcrumbs variable
    queries_link = (redirect_url, _("Queries"))
    form = QueryDeleteConfirmForm()
    if request.POST:
        data = request.POST.copy()
        form = QueryDeleteConfirmForm(data=data)
        if form.is_valid():
            confirm = bool(int(form.cleaned_data["confirm"]))
            if confirm:
                # here we remove the associated reports
                query.report_templates.all().delete()
                query.delete()
            return redirect(redirect_url)
    return render_to_response('queries/queries_query_delete.html',
                              {"graph": graph,
                               "form": form,
                               "queries_link": queries_link,
                               "query_name": query.name},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def queries_query_modify(request, graph_slug, query_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    query = graph.queries.get(id=query_id)

    queries_list_url = reverse("queries_list", args=[graph.slug])
    edit_query_url = reverse("queries_query_edit", args=[graph.slug, query.id])
    new_query_url = reverse("queries_new", args=[graph.slug])

    # We get the neccesary values for the query dictionary
    query_name = query.name
    query_description = query.description
    query_dict = request.session['query']
    query_fields = request.session['query_fields']
    query_aliases = request.session['query_aliases']

    # We create the data dictionary
    data = dict()
    data['graph'] = graph
    data['name'] = query_name
    data['description'] = query_description
    data['query_dict'] = query_dict
    data['query_fields'] = query_fields
    data['query_aliases'] = query_aliases
    data['results_count'] = 0
    data['last_run'] = datetime.now()

    # Let's save the results
    if request.POST:
        if 'modify-query' in request.POST:
            form = SaveQueryForm(data=data, instance=query)
            if form.is_valid():
                with transaction.atomic():
                    query = form.save(commit=False)
                    # We treat the results_count
                    results_count = request.session.get('results_count', None)
                    if results_count:
                        query.results_count = results_count
                        query.last_run = datetime.now()
                    else:
                        query.results_count = 0
                    query.save()
                    return redirect(queries_list_url)
            else:
                return redirect(edit_query_url)
        elif 'save-as-new' in request.POST:
            # We change the query id in session to load the dicts
            request.session['query_id'] = NEW
            request.session['query_name'] = _(NEW) + ' ' + query_name
            request.session['query_description'] = _(NEW) + ' ' + query_description
            return redirect(new_query_url)
    else:
        return redirect(edit_query_url)


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
                            content_type='application/json')


@is_enabled(settings.ENABLE_QUERIES)
@login_required
@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_query_collaborators(request, graph_slug):
    if request.is_ajax() and "term" in request.GET:
        graph = get_object_or_404(Graph, slug=graph_slug)
        term = request.GET["term"]
        if graph and term:
            # collabs = graph.get_collaborators(include_anonymous=True,
            #                                   as_queryset=True)
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
