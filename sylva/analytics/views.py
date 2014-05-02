# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse)
from celery.result import AsyncResult

from guardian.decorators import permission_required

from base.decorators import is_enabled
from graphs.models import Graph, Data
import pandas as pd
from collections import defaultdict


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.analytic",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def analytic(request, graph_slug):
    return render_to_response('analytics.html',
                              {"graph_slug": graph_slug},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.dump",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def dump(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('dump')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.connected_components",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def connected_components(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('connected_components')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.graph_coloring",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def graph_coloring(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('graph_coloring')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.kcore",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def kcore(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('kcore')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.pagerank",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def pagerank(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('pagerank')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.shortest_path",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def shortest_path(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('shortest_path')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.triangle_counting",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def triangle_counting(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('triangle_counting')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.betweenness_centrality",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def betweenness_centrality(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('betweenness_centrality')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.task_state",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def task_state(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            data = task.ready()
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.get_results",
                    (Data, "graph__slug", "graph_slug"), return_403=True)
def get_results(request, graph_slug):
    data = 'Fail'
    if request.is_ajax():
        if 'task_id' in request.GET.keys() and request.GET['task_id']:
            task_id = request.GET['task_id']
            algorithm = request.GET['algorithm']
            result = ""
            if algorithm == 'pagerank':
                result = 'pagerank'
            elif algorithm == 'connected_components':
                result = 'componentid'
            elif algorithm == 'graph_coloring':
                result = 'colorid'
            elif algorithm == 'kcore':
                result = 'coreid'
            elif algorithm == 'shortest_path':
                result = 'distance'
            elif algorithm == 'triangle_counting':
                result = 'triangle_count'
            elif algorithm == 'betweenness_centrality':
                result = 'betweenness_centrality'

            graph = get_object_or_404(Graph, slug=graph_slug)
            analytic = graph.analytics.filter(task_id=task_id)[0]
            url_results = analytic.results + '.csv'
            dt = pd.read_csv(url_results)
            counters = defaultdict(int)
            for k, v in dt[[result]].itertuples():
                counters[v] += 1
            data = counters.items()
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')
