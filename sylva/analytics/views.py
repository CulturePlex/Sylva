# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

import time
import csv

from celery.result import AsyncResult

from django.conf import settings
from django.shortcuts import get_object_or_404, HttpResponse
from django.http import StreamingHttpResponse
from django.views.decorators.http import condition

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
    analytics_results = dict()
    analytics_request = request.GET.get('analytics_request')
    analytics_executing = json.loads(analytics_request)
    if request.is_ajax() and analytics_executing is not None:
        for task_id in analytics_executing:
            task = AsyncResult(task_id)
            if task.ready():
                analytic = Analytic.objects.filter(
                    dump__graph__slug=graph_slug,
                    task_id=task_id).latest()
                analytics_results[task_id] = [analytic.results.url,
                    analytic.id, analytic.task_start, analytic.algorithm]
    data = analytics_results
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


# @condition(etag_func=None)
@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_dump(request, graph_slug):
    def stream_response_generator(data_file,
            rels=False, duplicated=False, headers=False):
        stream_reader = csv.reader(data_file.file, delimiter=",")
        if rels == True:
            if headers == False:
                # We take the headers for eliminate them of the returned value
                headers_element = stream_reader.next()
            for row in stream_reader:
                yield json.dumps(row)
                # Encourage browser to render incrementally
                yield " " * 1024
        else:
            # We take the headers for eliminate them of the returned value
            headers = stream_reader.next()
            if duplicated:
                for row in stream_reader:
                    for col in row:
                        yield json.dumps(col)
                        yield "\n"
                        # Encourage browser to render incrementally
                        yield " " * 1024
            else:
                nodes = set()
                for row in stream_reader:
                    for col in row:
                        if col not in nodes:
                            yield json.dumps(col)
                            yield "\n"
                            nodes.update(col)
                        # Encourage browser to render incrementally
                        yield " " * 1024

    analytic_id = request.GET.get('id')
    rels = bool(request.GET.get('rels'))
    if request.is_ajax() and analytic_id is not None:
        analytic = Analytic.objects.get(pk=analytic_id)
        analytic_dump = analytic.dump
        data_file = analytic_dump.data_file
        return StreamingHttpResponse(stream_response_generator(data_file, rels),
            content_type='application/javascript')
    else:
        return StreamingHttpResponse([], mimetype='text/html')
