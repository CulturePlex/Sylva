# -*- coding: utf-8 -*-
import json
from subprocess import Popen, STDOUT, PIPE

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
def preview_report_pdf(request, graph_slug):
    raster_path = '/home/dbshow/git/Sylva/sylva/reports/static/phantomjs/rasterize.js'
    filename = "/home/dbshow/git/Sylva/sylva/reports/static/phantomjs/pics/report_pdf_test.pdf"
    url = 'http://localhost:8000/reports/preliminaries-projection/#/preview/report1'
    csrftoken = request.COOKIES.get('csrftoken', 'nocsrftoken')
    sessionid = request.COOKIES.get('sessionid', 'nosessionid')
    Popen([
        'phantomjs',
        raster_path,
        url,
        filename,
        csrftoken,
        sessionid
    ], stdout=PIPE, stderr=STDOUT)
    with open('/home/dbshow/git/Sylva/sylva/reports/static/phantomjs/pics/report_pdf_test.pdf') as pdf:
        response = HttpResponse(pdf.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'inline;filename={0}'.format(filename)
        return response
    pdf.closed



    

@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def reports_endpoint(request, graph_slug):
    series = [
        ["5", 0.279767],
        ["2", 0.15],
        ["6", 0.484065],
        ["8", 0.1925],
        ["7", 0.918638],
        ["1", 0.1925],
        ["4", 0.394192],
        ["3", 0.182725]
    ]
    queries = [
        {'name': 'query1', 'series': series},
        {'name': 'query2', 'series': series},
        {'name': 'query3', 'series': series},
        {'name': 'query4', 'series': series},
        {'name': 'query5', 'series': series}
    ]
    reports = [{
        'queries': queries,
        'name': 'report1',
        'slug': 'report1',
        'table': [[{
            'col': 0,
            'colspan': '1',
            'id': 'cell1',
            'row': 0,
            'rowspan': '1',
            'displayQuery': 'query3',
            'chartType': 'line'
        }, {
            'col': 1,
            'colspan': '2',
            'id': 'cell2',
            'row': 0,
            'rowspan': '1',
            'displayQuery': 'query4',
            'chartType': 'scatter'
        }], [{
            'col': 0,
            'colspan': '1',
            'id': 'cell3',
            'row': 1,
            'rowspan': '1',
            'displayQuery': 'query1',
            'chartType': 'pie'
        }, {
            'col': 1,
            'colspan': '1',
            'id': 'cell4',
            'row': 1,
            'rowspan': '1',
            'displayQuery': 'query2',
            'chartType': 'column'
        }, {
            'col': 2,
            'colspan': '1',
            'id': 'cell5',
            'row': 1,
            'rowspan': '1',
            'displayQuery': 'query5',
            'chartType': 'column'
        }]],
        'numRows': 2,
        'numCols': 3,
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
    series = [
        ["5", 0.279767],
        ["2", 0.15],
        ["6", 0.484065],
        ["8", 0.1925],
        ["7", 0.918638],
        ["1", 0.1925],
        ["4", 0.394192],
        ["3", 0.182725]
    ]
    queries = [
        {'name': 'query1', 'series': series},
        {'name': 'query2', 'series': series},
        {'name': 'query3', 'series': series},
        {'name': 'query4', 'series': series},
        {'name': 'query5', 'series': series}
    ]
    json_data = json.dumps(queries)
    print json_data
    return HttpResponse(json_data, mimetype='application/json')
