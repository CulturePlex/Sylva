# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

import csv
from celery.result import AsyncResult
from sylva.celery import app

from django.conf import settings
from django.shortcuts import get_object_or_404, HttpResponse
from django.http import StreamingHttpResponse

from guardian.decorators import permission_required

from analytics.models import Analytic
from sylva.decorators import is_enabled
from graphs.models import Graph, Data


REVOKED = 'REVOKED'
STATUS_OK = 'OK'
STATUS_REVOKED = 'REVOKED'


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_run(request, graph_slug):
    data = []
    graph = get_object_or_404(Graph, slug=graph_slug)
    algorithm = request.POST.get("algorithm")
    subgraph = request.POST.get("subgraph")
    if subgraph:
        # We change the type from string to int
        subgraph = json.loads(subgraph)
        subgraph = [int(elem) for elem in subgraph]
    available_algorithms = graph.analysis.get_algorithms()
    if request.is_ajax() and algorithm in available_algorithms:
        analytic = graph.analysis.run(algorithm, subgraph)
        task = AsyncResult(analytic.task_id)
        data = [task.id, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


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
    return HttpResponse(json_data, content_type='application/json')


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
            # We need to take into account if the task has been revoked
            if task.ready() and task.status != REVOKED:
                # Sometimes, the execution is faster than the revoked flag. So
                # we need to control that (ValueError exception)
                try:
                    analytic = Analytic.objects.filter(
                        dump__graph__slug=graph_slug,
                        task_id=task_id).latest()
                    analytics_results[task_id] = [STATUS_OK,
                                                  analytic.results.url,
                                                  analytic.id,
                                                  analytic.task_start,
                                                  analytic.algorithm,
                                                  analytic.values.url]
                except ValueError:
                    analytics_results[task_id] = [STATUS_REVOKED]
            elif task.status == REVOKED:
                analytics_results[task_id] = [STATUS_REVOKED]
    data = analytics_results
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_analytic(request, graph_slug):
    data = []
    analytic_id = request.GET.get('id')
    if request.is_ajax() and analytic_id is not None:
        analytic = Analytic.objects.get(pk=analytic_id)
        data = [analytic.results.url, analytic.algorithm, analytic.values.url]
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


# @condition(etag_func=None)
@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_dump(request, graph_slug):

    def stream_response_generator(data_file, rels=False, duplicated=False,
                                  headers=False):
        stream_reader = csv.reader(data_file.file, delimiter=",")
        if rels is True:
            if headers is False:
                # We take the headers for eliminate them of the returned value
                headers_element = stream_reader.next()
            for row in stream_reader:
                yield json.dumps(row)
        else:
            # We take the headers for eliminate them of the returned value
            headers = stream_reader.next()
            if duplicated:
                for row in stream_reader:
                    for col in row:
                        yield 'data: ' + json.dumps(col) + '\n\n'
            else:
                nodes = set()
                for row in stream_reader:
                    for col in row:
                        if col not in nodes:
                            yield 'data: ' + json.dumps(col) + '\n\n'
                            nodes.add(col)
        yield 'data: "close"\n\n'

    analytic_id = request.GET.get('id')
    rels = bool(request.GET.get('rels'))
    if analytic_id is not None:
        analytic = Analytic.objects.get(pk=analytic_id)
        analytic_dump = analytic.dump
        data_file = analytic_dump.data_file
        return StreamingHttpResponse(stream_response_generator(
            data_file, rels), content_type='text/event-stream')
    else:
        return StreamingHttpResponse([], content_type='text/event-stream')


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("data.view_data",
                     (Data, "graph__slug", "graph_slug"), return_403=True)
def analytics_stop(request, graph_slug):
    task_id = request.POST.get('task_id')
    # We stop the algorith
    app.control.revoke(task_id, terminate=True)
    # We get the analytic to give the info to the user
    analytic = Analytic.objects.filter(dump__graph__slug=graph_slug,
                                       task_id=task_id).latest()
    data = [analytic.id, analytic.algorithm]
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')
