# -*- coding: utf-8 -*-
import json
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext
from django.core.context_processors import csrf


# @permission_required()
def reports_index_view(request, graph_slug):
    graph_slug = 'my_graph'
    c = {}
    c.update(csrf(request))
    return render_to_response('reports_index.html', RequestContext(request, {
        'graph_slug': graph_slug,
        'c': c
    }))


#@permission_required()
def reports_endpoint(request):
    reports = [
        {'name': 'report1', 'slug': 'report1',
         'queries': ['query1', 'query3']},
        {'name': 'report2', 'slug': 'report2',
         'queries': ['query5', 'query2']},
        {'name': 'report3', 'slug': 'report3',
         'queries': ['query4', 'query5']},
    ]
    if request.POST:
        post = json.loads(request.body)
        new_report = post['report']
        json_data = json.dumps(new_report)
    elif request.GET:
        graph_slug = request.GET['graph']
        json_data = json.dumps(reports)
    return HttpResponse(json_data, mimetype='application/json')


# @permission_required()
def queries_endpoint(request):
    queries = [
        {'name': 'query1'},
        {'name': 'query2'},
        {'name': 'query3'},
        {'name': 'query4'},
        {'name': 'query5'}
    ]
    print request.GET['graph']
    json_data = json.dumps(queries)
    return HttpResponse(json_data, mimetype='application/json')
