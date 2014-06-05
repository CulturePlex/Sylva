# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from celery.result import AsyncResult

from django.conf import settings
from django.shortcuts import get_object_or_404, HttpResponse

from guardian.decorators import permission_required

from analytics.models import Analytic
from base.decorators import is_enabled
from graphs.models import Graph, Data


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_run(request, graph_slug):
    data = []
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = request.POST.get("algorithm")
    available_algorithms = graph.analysis.get_algorithms()
    if request.is_ajax() and algorithm in available_algorithms:
        analytic = graph.analysis.run(algorithm)
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_estimate(request, graph_slug):
    data = []
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = request.POST.get("algorithm")
    available_algorithms = graph.analysis.get_algorithms()
    if request.is_ajax() and algorithm in available_algorithms:
        estimation = graph.analysis.estimate(algorithm)
        data = [algorithm, estimation]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_status(request, graph_slug):
    data = []
    task_id = request.GET.get('id')
    if request.is_ajax() and task_id is not None:
        task = AsyncResult(task_id)
        if task.ready():
            analytic = Analytic.objects.filter(
                dump__graph__slug=graph_slug,
                task_id=task_id).latest()
            data = [analytic.results.url, analytic.id, analytic.task_start]
        else:
            data = False
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_analytic(request, graph_slug):
    data = []
    analytic_id = request.GET.get('id')
    if request.is_ajax() and analytic_id is not None:
        analytic = Analytic.objects.get(pk=analytic_id)
        data = [analytic.results.url, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')
