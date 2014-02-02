# -*- coding: utf-8 -*-
import json
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext
from django.core.context_processors import csrf
from guardian.decorators import permission_required


#@permission_required('reports.view_report',
                     #(Report, 'graph__slug', 'graph_slug'), return_403=True)
def reports_index_view(request, graph_slug):
    c = {}
    c.update(csrf(request))
    return render_to_response('reports_index.html', RequestContext(request, {
        'graph_slug': graph_slug,
        'c': c
    }))


#@permission_required('reports.view_report',
                     #(Report, 'graph__slug', 'graph_slug'), return_403=True)
def reports_endpoint(request, graph_slug):
    reports = [
        {'name': 'report1', 'slug': 'report1',
         'queries': ['query1', 'query3'], 'frequency': 'weekly',
         'start_time': 'Sun Feb 03 2014 09:25:00 GMT-0500 (EST)',
         'description': 'a report'},
        {'name': 'report2', 'slug': 'report2',
         'queries': ['query5', 'query2'], 'frequency': 'daily',
         'start_time': 'Sun Feb 04 2014 09:25:00 GMT-0500 (EST)',
         'description': 'a report'},
        {'name': 'report3', 'slug': 'report3',
         'queries': ['query4', 'query5'], 'frequency': 'weekly',
         'start_time': 'Sun Feb 05 2014 09:25:00 GMT-0500 (EST)',
         'description': 'a report'},
    ]
    if request.POST:
        post = json.loads(request.body)
        new_report = post['report']
        json_data = json.dumps(new_report)
    else:
        json_data = json.dumps(reports)
    return HttpResponse(json_data, mimetype='application/json')


#@permission_required('queries.view_query',
                     #(Query, 'graph__slug', 'graph_slug'), return_403=True)
def queries_endpoint(request, graph_slug):
    queries = [
        {'name': 'query1'},
        {'name': 'query2'},
        {'name': 'query3'},
        {'name': 'query4'},
        {'name': 'query5'}
    ]
    json_data = json.dumps(queries)
    return HttpResponse(json_data, mimetype='application/json')
