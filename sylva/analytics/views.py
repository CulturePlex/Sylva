# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from celery.result import AsyncResult

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse)

from guardian.decorators import permission_required

from analytics.models import Analytic
from base.decorators import is_enabled
from graphs.models import Graph, Data


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytic(request, graph_slug):
    return render_to_response('analytics.html',
                              {"graph_slug": graph_slug},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def dump(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('dump')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def connected_components(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('connected_components')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_connected_components(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'connected_components'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def graph_coloring(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('graph_coloring')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_graph_coloring(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'graph_coloring'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def kcore(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('kcore')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_kcore(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'kcore'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def pagerank(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('pagerank')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_pagerank(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'pagerank'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def shortest_path(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('shortest_path')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_shortest_path(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'shortest_path'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def triangle_counting(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('triangle_counting')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_triangle_counting(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'triangle_counting'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def betweenness_centrality(request, graph_slug):
    data = []
    if request.is_ajax():
        graph = get_object_or_404(Graph, slug=graph_slug)
        analytic = graph.analysis.run('betweenness_centrality')
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_eta_betweenness_centrality(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = 'betweenness_centrality'
    estimation = graph.analysis.estimate(algorithm)
    data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def task_state(request, graph_slug):
    data = []
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            if task.ready():
                analytic = Analytic.objects.filter(
                    dump__graph__slug=graph_slug,
                    task_id=task_id).latest()
                data = "{0}{1}".format(settings.MEDIA_URL,
                                       analytic.results.name)
            else:
                data = False

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def get_analytic(request, graph_slug):
    data = []
    if request.is_ajax():
        if ('analytic_id' in request.POST.keys() and
                request.POST['analytic_id']):
            analytic_id = request.POST['analytic_id']
            analytic = Analytic.objects.get(pk=analytic_id)
            results_url = "{0}{1}".format(settings.MEDIA_URL,
                                          analytic.results.name)
            data = [results_url, analytic.algorithm]

    json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')
