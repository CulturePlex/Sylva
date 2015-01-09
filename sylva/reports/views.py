# -*- coding: utf-8 -*-
import datetime
import json
import os
import tempfile
import urlparse

from subprocess import Popen, STDOUT, PIPE
from time import time

from django.conf import settings
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext
from django.core.context_processors import csrf
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required

from models import ReportTemplate, Report
from graphs.models import Graph, Schema
from queries.models import Query

from sylva.decorators import is_enabled


settings.ENABLE_REPORTS = True


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def reports_index_view(request, graph_slug):
    pdf = request.GET.get('pdf', '')
    if pdf:
        pdf = True  # hmmm gotta fix this
    else:
        pdf = False
    c = {}
    c.update(csrf(request))  # Maybe pass this as constant?
    report_name = _("New Report")
    placeholder_name = _("Report Name")
    graph = get_object_or_404(Graph, slug=graph_slug)
    return render_to_response('reports_base.html', RequestContext(request, {
        'pdf': pdf,
        'graph': graph,
        'c': c,
        'report_name': report_name,
        'placeholder_name': placeholder_name
    }))


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def partial_view(request, graph_slug):
    name = request.GET.get('name', '')
    pattern = 'partials/{0}.html'.format(name)
    return render_to_response(pattern, RequestContext(request, {}))


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def preview_report_pdf(request, graph_slug):
    parsed_url = urlparse.urlparse(
        request.build_absolute_uri()
    )
    raster_path = finders.find('phantomjs/rasterize.js')
    temp_path = os.path.join(tempfile.gettempdir(), str(int(time() * 1000)))
    filename = '{0}.pdf'.format(temp_path)
    template_slug = request.GET.get('template', '')
    if request.GET.get('template', ''):
        download_name = '{0}.pdf'.format(request.GET['template'])
    else:
        download_name = temp_path
    url = '{0}://{1}{2}{3}#/preview/{4}'.format(
        parsed_url.scheme,
        parsed_url.netloc,
        reverse(reports_index_view, kwargs={'graph_slug': graph_slug}),
        '?pdf=true',
        template_slug
    )
    domain = parsed_url.hostname
    csrftoken = request.COOKIES.get('csrftoken', 'nocsrftoken')
    sessionid = request.COOKIES.get('sessionid', 'nosessionid')
    Popen([
        'phantomjs',
        raster_path,
        url,
        filename,
        domain,
        csrftoken,
        sessionid
    ], stdout=PIPE, stderr=STDOUT).wait()
    try:
        with open(filename) as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename={0}'.format(
                download_name
            )
            pdf.close()
    except IOError, e:
        response = HttpResponse('Sorry there has been a IOError:' + e.strerror)
    os.unlink(filename)
    return response


# Reports "API"
@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def templates_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if request.GET.get('queries', '') or request.GET.get('template', ''):
        response = {'template': None, 'queries': None}
        if request.GET.get('queries', ''):  # Get queries either for
                                            # new template or for edit.
            queries = graph.queries.plottable()
            # dummy series data
            # This will all change soon
            dummy_series = [
                [1, 6], [2, 6.5], [3, 7], [4, 7.5],
                [5, 8], [6, 8.5], [7, 9], [8, 9]
            ]
            response['queries'] = [{'series': dummy_series,
                                    'name': query.name, 'id': query.id,
                                    'results': query.query_dict['results']}
                                   for query in queries]
        if request.GET.get('template', ''):  # Get template for edit or preview
            template = get_object_or_404(
                ReportTemplate, slug=request.GET['template']
            )
            response['template'] = template.dictify()
            if not response['queries']:  # Get template queries for preview.
                queries = template.queries.all()
                # Will have to execute queries here
                response['queries'] = [{'series': query.execute(headers=True),
                                        'name': query.name, 'id': query.id,
                                        'results': query.query_dict['results']}
                                       for query in queries]
                #import ipdb; ipdb.set_trace()
    else:  # Get a list of all the reports.
        templates = graph.report_templates.order_by(
            '-last_run',
            '-start_date'
        )
        paginator = Paginator(templates, 10)
        page = request.GET.get('page')
        try:
            templates_paginator = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            templates_paginator = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            templates_paginator = paginator.page(paginator.num_pages)
        template_list = [
            template.dictify() for template in templates_paginator.object_list
        ]
        has_next = templates_paginator.has_next()
        if has_next:
            next_page_number = templates_paginator.next_page_number()
        else:
            next_page_number = None
        has_previous = templates_paginator.has_previous()
        if has_previous:
            previous_page_number = templates_paginator.previous_page_number()
        else:
            previous_page_number = None
        response = {
            'templates': template_list,
            'num_pages': paginator.num_pages,
            'total_count': paginator.count,
            'num_objects': len(template_list),
            'next_page_number': next_page_number,
            'page_number': templates_paginator.number,
            'previous_page_number': previous_page_number
        }
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def history_endpoint(request, graph_slug):
    if request.GET:
        if request.GET.get('template', ''):
            template = get_object_or_404(
                ReportTemplate, slug=request.GET['template']
            )
            report_dict = template.dictify()
            reports = template.reports.order_by('-date_run')
            paginator = Paginator(reports, 5)
            page = request.GET.get('page')
            try:
                reports_paginator = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                reports_paginator = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results
                reports_paginator = paginator.page(paginator.num_pages)
            report_list = [
                report.dictify() for report in reports_paginator.object_list
            ]
            has_next = reports_paginator.has_next()
            if has_next:
                next_page_number = reports_paginator.next_page_number()
            else:
                next_page_number = None
            has_previous = reports_paginator.has_previous()
            if has_previous:
                previous_page_number = reports_paginator.previous_page_number()
            else:
                previous_page_number = None
            report_dict['history'] = [
                {k: v for (k, v) in report.items() if k != 'table'}
                for report in report_list
            ]
            report_dict.update({
                'reports': report_list,
                'num_pages': paginator.num_pages,
                'total_count': paginator.count,
                'num_objects': len(report_list),
                'next_page_number': next_page_number,
                'page_number': reports_paginator.number,
                'previous_page_number': previous_page_number
            })
            response = report_dict
        if request.GET.get('report', ''):
            report = get_object_or_404(Report, id=request.GET['report'])
            response = report.dictify()
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def builder_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if request.POST:
        template = json.loads(request.body)['template']
        date_dict = template['start_date']
        start_date = datetime.datetime(
            int(date_dict['year']),
            int(date_dict['month']),
            int(date_dict['day']),
            int(date_dict['hour']),
            int(date_dict['minute'])
        )
        if template.get('slug', ''):
            new_template = get_object_or_404(
                ReportTemplate, slug=template['slug']
            )
            new_template.name = template['name']
            new_template.start_date = start_date
            new_template.frequency = template['frequency']
            new_template.layout = template['layout']
            new_template.description = template['description']
            new_template.save()
        else:
            new_template = ReportTemplate.objects.create(
                name=template['name'],
                start_date=start_date,
                frequency=template['frequency'],
                layout=template['layout'],
                description=template['description'],
                graph=graph
            )
        query_set = set()
        for row in template['layout']:
            query_set.update(set(cell['displayQuery'] for cell in row))
        queries = set(query for query in new_template.queries.all())
        query_ids = set(query.id for query in queries)
        for query in queries:
            if query.id not in query_set:
                new_template.queries.remove(query)
        for disp_query in query_set:
            if disp_query and disp_query not in query_ids:
                query = get_object_or_404(Query, id=disp_query)
                new_template.queries.add(query)
    return HttpResponse(json.dumps(template), content_type='application/json')
