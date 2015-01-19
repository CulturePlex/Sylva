# -*- coding: utf-8 -*-
import datetime
import json
import os
import tempfile
import urlparse

from collections import defaultdict
from subprocess import Popen, STDOUT, PIPE
from time import time

from dateutil import relativedelta
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
    pdf = request.GET.get('pdf', False)
    if pdf:
        pdf = True
    graph = get_object_or_404(Graph, slug=graph_slug)
    return render_to_response('reports_base.html', RequestContext(request, {
        'pdf': pdf,
        'graph': graph
    }))


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def partial_view(request, graph_slug):
    name = request.GET.get('name', '')
    pattern = 'partials/{0}.html'.format(name)
    return render_to_response(pattern, RequestContext(request, {}))


# Reports "API"
@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def list_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    templates = graph.report_templates.order_by(
        '-last_run',
        '-start_date'
    )
    page = request.GET.get('page', "")
    pgntr, output, next_page_num, prev_page_num = paginate(
        templates, 10, page
    )
    templates = [template.dictify() for template in output.object_list]
    response = {
        'templates': templates,
        'num_pages': pgntr.num_pages,
        'total_count': pgntr.count,
        'num_objects': len(templates),
        'next_page_number': next_page_num,
        'page_number': output.number,
        'previous_page_number': prev_page_num
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def templates_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    response = {'template': None, 'queries': None}
    # Get queries either for new template or for edit.
    if request.GET.get('queries', ''):
        queries = graph.queries.plottable()
        dummy_series = [
            ["color", "count1", "count2", "count3", "count4", "count5"],
            ["yellow", 6, 7, 8, 9, 10],
            ["blue", 6.5, 5.5, 8, 7, 11],
            ["purple", 4.5, 5.5, 6, 9, 9.5],
            ["red", 5, 5.5, 4.5, 3, 6],
            ["green", 5, 6, 7.5, 9, 10]
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
            response['queries'] = [{'series': query.execute(headers=True),
                                    'name': query.name, 'id': query.id,
                                    'results': query.query_dict['results']}
                                   for query in queries]
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("schemas.view_schema",
                     (Schema, "graph__slug", "graph_slug"), return_403=True)
def history_endpoint(request, graph_slug):
    response = {"reports": []}
    if request.GET.get('template', ''):
        template = get_object_or_404(
            ReportTemplate, slug=request.GET['template']
        )
        # Sort reports into buckets depending on periodicity
        # So here I can build and paginate buckets then query
        # reports only back to oldest bucket, then fill the buckets 
        # and send them off.
        first_date_run = template.reports.earliest('date_run').date_run
        if first_date_run:
            periodicity = template.frequency
            first_date_run = template.reports.earliest('date_run').date_run
            now = datetime.datetime.now()
            if periodicity == "h":
                start = first_date_run.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                interval = datetime.timedelta(days=1)
            elif periodicity == "d":
                weekday = first_date_run.weekday()
                if weekday == 6:
                    start = first_date_run
                else:
                    start = first_date_run - timedelta(days=weekday + 1)
                start = start.replace(
                        hour=0, minute=0, second=0, microsecond=0
                ) 
                interval = datetime.timedelta(weeks=1)
            elif periodicity == "w":
                start = first_date_run.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                ) 
                interval = relativedelta.relativedelta(months=1)
            else:
                start = first_date_run.replace(
                    month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                ) 
                interval = relativedelta.relativedelta(years=1) 
            bucket = start + interval
            buckets = [start, bucket]
            while bucket < now:
                buckets.append(bucket)
                bucket += interval
            page = request.GET.get('page', "")
            pgntr, output, next_page_num, prev_page_num = paginate(
                buckets, 5, page
            )
            oldest = output.object_list[0]
            reports = template.reports.filter(date_run__gte=oldest).order_by('-date_run')
            report_buckets = defaultdict(list)
            for report in reports:
                bucket = _get_bucket(report.date_run, buckets)
                report_buckets[bucket].append(report.dictify())
            report_buckets = [
                {"bucket": b, "reports": r} for (b, r) in report_buckets.items()
            ]
            response = {
                'name': template.name,
                'reports': report_buckets,
                'num_pages': pgntr.num_pages,
                'total_count': pgntr.count,
                'num_objects': len(report_buckets),
                'next_page_number': next_page_num,
                'page_number': output.number,
                'previous_page_number': prev_page_num
            }
    elif request.GET.get('report', ''):
        report = get_object_or_404(Report, id=request.GET['report'])
        response = report.dictify()

    return HttpResponse(json.dumps(response), content_type='application/json')


def _get_bucket(date, buckets):
    # Little search algo.
    while len(buckets) > 1:
        ndx = len(buckets) / 2
        if date >= buckets[ndx]:
            buckets = buckets[ndx:]
        else:
            buckets = buckets[:ndx]
    return buckets[0].isoformat()


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
        # Take another look at this.
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
    # Hmm this response is weird.
    return HttpResponse(json.dumps(template), content_type='application/json')


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


def paginate(itrbl, per_page, page):
    paginator = Paginator(itrbl, per_page, page)
    try:
        output = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        output = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        output = paginator.page(paginator.num_pages)
    has_next = output.has_next()
    if has_next:
        next_page_number = output.next_page_number()
    else:
        next_page_number = None
    has_previous = output.has_previous()
    if has_previous:
        previous_page_number = output.previous_page_number()
    else:
        previous_page_number = None
    return paginator, output, next_page_number, previous_page_number
