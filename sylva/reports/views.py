# -*- coding: utf-8 -*-
import json
from django.conf import settings
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext
from django.core.context_processors import csrf
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required

from base.decorators import is_enabled
from graphs.models import Graph, Schema

settings.ENABLE_REPORTS = True


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def reports_index_view(request, graph_slug):
    c = {}
    c.update(csrf(request))
    report_name = _("New Report")
    placeholder_name = _("Report Name")
    graph = get_object_or_404(Graph, slug=graph_slug)
    return render_to_response('reports_base.html', RequestContext(request, {
        'graph': graph,
        'c': c,
        'report_name': report_name,
        'placeholder_name': placeholder_name,
    }))


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def reports_endpoint(request, graph_slug):
    reports = [{
        'name': 'report1',
        'slug': 'report1',
        'table': [[{
            'col': 0,
            'colspan': '1',
            'id': 'cell1',
            'row': 0,
            'rowspan': '1',
            'query': 'query3'
        }, {
            'col': 1,
            'colspan': '1',
            'id': 'cell2',
            'row': 0,
            'rowspan': '1',
            'query': ''
        }], [{
            'col': 0,
            'colspan': '1',
            'id': 'cell3',
            'row': 1,
            'rowspan': '1',
            'query': 'query1'
        }, {
            'col': 1,
            'colspan': '1',
            'id': 'cell4',
            'row': 1,
            'rowspan': '1',
            'query': 'query2'
        }]],
        'numRows': 2,
        'numCols': 2,
        'periodicity': 'weekly',
        'start_time': '08:30',
        'start_date': "11/02/2014",
        'description': 'Report1 will now form the beginning of the tests',
        'history': [
            {'date': "11/03/2014", 'id': 1},
            {'date': "11/05/2014", 'id': 2},
            {'date': "11/02/2014", 'id': 3}
        ]
    },
        {'name': 'report2', 'slug': 'report2',
         'queries': {'cell1': 'query2'}, 'periodicity': 'daily',
         'start_time': '09:30', 'start_date': "11/02/2014",
         'description': 'a report'},

        {'name': 'report3', 'slug': 'report3',
         'queries': {'cell0': 'query3'}, 'periodicity': 'weekly',
         'start_time': '10:30', 'start_date': "11/02/2014",
         'description': 'a report'},
    ]
    if request.POST:
        post = json.loads(request.body)
        new_report = post['report']
        json_data = json.dumps(new_report)
    elif request.GET.get('slug', ''):
        ##import ipdb; ipdb.set_trace()
        slug = request.GET['slug']
        for report in reports:
            if report['slug'] == slug:
                json_data = json.dumps([report])
    else:
        json_data = json.dumps(reports)
    return HttpResponse(json_data, mimetype='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def queries_endpoint(request, graph_slug):
    queries = [
        {'name': 'query1'},
        {'name': 'query2'},
        {'name': 'query3'},
        {'name': 'query4'},
        {'name': 'query5'}
    ]
    json_data = json.dumps(queries)
    print json_data
    return HttpResponse(json_data, mimetype='application/json')
