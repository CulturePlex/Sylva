# -*- coding: utf-8 -*-
import datetime
import json
import os
import urlparse

from dateutil import relativedelta
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required
from guardian.shortcuts import get_perms
from reports.forms import ReportTemplateForm
from reports.utils import phantom_process
from reports.models import ReportTemplate, Report
from graphs.models import Graph
from queries.models import Query

from sylva.decorators import is_enabled


SECRET = getattr(settings, "REPORTS_SECRET", "")


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def reports_index_view(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    # We get the modal variable
    as_modal = bool(request.GET.get("asModal", False))
    user = request.user
    if as_modal:
        render = render_to_string
    else:
        render = render_to_response
    perms = get_perms(user, graph)
    broader_context = {
        "graph": graph,
        "view_reports": 'view_graph_reports' in perms,
        "add_reports": 'add_graph_reports' in perms,
        "edit_reports": 'change_graph_reports' in perms,
        "delete_reports": 'delete_graph_reports' in perms,
        "as_modal": as_modal}
    response = render('reports_base.html',
                      context_instance=RequestContext(request,
                                                      broader_context))
    if as_modal:
        response = {'type': 'html',
                    'action': 'reports_main',
                    'html': response}
        return HttpResponse(json.dumps(response), status=200,
                            content_type='application/json')
    else:
        return response


@csrf_exempt
def pdf_gen_view(request, graph_slug, template_slug):

    def render(request, graph_slug, template_slug):
        graph = get_object_or_404(Graph, slug=graph_slug)
        template = get_object_or_404(ReportTemplate, slug=template_slug)
        queries = template.queries.all()
        as_modal = bool(request.GET.get("asModal", False))
        queries = [{'series': query.execute(headers=True), 'name': query.name,
                    'id': query.id, 'results': query.query_dict['results']}
                   for query in queries]
        template_dict = template.dictify()
        resp = {"table": template_dict["layout"], "queries": queries}

        if as_modal:
            render = render_to_string
        else:
            render = render_to_response
        broader_context = {"graph": graph,
                           "template": template_dict,
                           "resp": json.dumps(resp),
                           "prev": True,
                           "as_modal": as_modal}
        response = render('pdf.html',
                          context_instance=RequestContext(request,
                                                          broader_context))
        if as_modal:
            response = {'type': 'html',
                        'action': 'reports_pdf',
                        'html': response}
            return HttpResponse(json.dumps(response), status=200,
                                content_type='application/json')
        else:
            return response

    @login_required
    @is_enabled(settings.ENABLE_REPORTS)
    @permission_required("graphs.add_graph_reports",
                         (Graph, "slug", "graph_slug"), return_403=True)
    def protected(request, **kwargs):
        return render(request, graph_slug, template_slug)

    if request.POST.get("secret", "") or settings.DEBUG:
        secret = request.POST.get("SECRET", "nosecret")
        if secret == SECRET or settings.DEBUG:
            return render(request, graph_slug, template_slug)
        else:
            return protected(request, graph_slug=graph_slug,
                             template_slug=template_slug)
    else:
        return protected(request, graph_slug=graph_slug,
                         template_slug=template_slug)


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def partial_view(request, graph_slug):
    name = request.GET.get('name', '')
    pattern = 'partials/{0}.html'.format(name)
    return render_to_response(pattern, RequestContext(request, {}))


# Reports "API"
@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def list_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    templates = graph.report_templates.order_by(
        '-last_run',
        '-start_date'
    )
    page = request.GET.get('page', 1)
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
def templates_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    response = {'template': None, 'queries': None}
    # Get queries either for new template or for edit.
    queries = request.GET.get('queries', '')
    template = request.GET.get('template', '')

    def go(request, response, graph, **kwargs):
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
        return HttpResponse(json.dumps(response),
                            content_type='application/json')

    @permission_required("graphs.add_graph_reports",
                         (Graph, "slug", "graph_slug"), return_403=True)
    def new(request, response, graph, graph_slug, **kwargs):
        return go(request, response, graph)

    @permission_required("graphs.view_graph_reports",
                         (Graph, "slug", "graph_slug"), return_403=True)
    def preview(request, response, graph, graph_slug, **kwargs):
        return go(request, response, graph)

    @permission_required("graphs.change_graph_reports",
                         (Graph, "slug", "graph_slug"), return_403=True)
    def edit(request, response, graph, **kwargs):
        return go(request, response, graph)

    if queries and template:
        return edit(request, response, graph, graph_slug=graph_slug)
    elif template and not queries:
        return preview(request, response, graph, graph_slug=graph_slug)
    else:
        return new(request, response, graph, graph_slug=graph_slug)


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.delete_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def delete_endpoint(request, graph_slug):
    response = {}
    if request.method == "POST":
        template_slug = json.loads(request.body)['template']
        template = get_object_or_404(
            ReportTemplate, slug=template_slug
        )
        template.delete()
    elif request.GET.get("template"):
        template = get_object_or_404(
            ReportTemplate, slug=request.GET["template"]
        )
        response = template.dictify()
        response.update({"num_reports": template.reports.count()})
    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def history_endpoint(request, graph_slug):
    response = {"reports": []}
    if request.GET.get('template', ''):
        template = get_object_or_404(
            ReportTemplate, slug=request.GET['template']
        )
        # Sort reports into buckets depending on periodicity
        try:
            first_date_run = template.reports.earliest('date_run').date_run
            periodicity = template.frequency
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
                    start = first_date_run - datetime.timedelta(
                        days=weekday + 1
                    )
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
            bucket = start
            buckets = [bucket]
            while bucket < now:
                buckets.append(bucket)
                bucket += interval
            page = request.GET.get('page', 1)
            buckets.reverse()
            pgntr, output, next_page_num, prev_page_num = paginate(
                buckets, 5, page
            )
            oldest = output.object_list[-1]
            newest = output.object_list[0] + interval
            reports = template.reports.filter(
                Q(date_run__gte=oldest) & Q(date_run__lt=newest)
            ).order_by('-date_run')
            if len(output.object_list) == 1:
                report_buckets = {output.object_list[0].isoformat(): []}
            else:
                report_buckets = {k.isoformat(): [] for k in
                                  output.object_list}
            for report in reports:
                bucket = _get_bucket(report.date_run, output.object_list)
                report_buckets[bucket].append(report.dictify())
            report_buckets = [
                {"bucket": b,
                 "reports": r} for (b, r) in report_buckets.items()
            ]
            response = {
                'name': template.name,
                'slug': template.slug,
                'reports': report_buckets,
                'num_pages': pgntr.num_pages,
                'total_count': pgntr.count,
                'num_objects': len(report_buckets),
                'next_page_number': next_page_num,
                'page_number': output.number,
                'previous_page_number': prev_page_num
            }
        except ObjectDoesNotExist:
            pass
    elif request.GET.get('report', ''):
        report = get_object_or_404(Report, id=request.GET['report'])
        response = report.dictify()
    return HttpResponse(json.dumps(response), content_type='application/json')


def _get_bucket(date, buckets):
    for bucket in buckets:
        if bucket < date:
            return bucket.isoformat()


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def fullscreen_view(request, graph_slug, template_slug, report_id):
    graph = get_object_or_404(Graph, slug=graph_slug)
    report = get_object_or_404(Report, id=report_id)
    template = get_object_or_404(ReportTemplate, slug=template_slug)
    template = template.dictify()
    template.update({"date": report.date_run})
    response = report.dictify()
    return render_to_response("pdf.html", RequestContext(request, {
        "graph": graph,
        "template": template,
        "resp": json.dumps(response)
    }))


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.add_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def builder_endpoint(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    template = {}
    if request.method == "POST":
        template = json.loads(request.body)['template']
        date = template['date'].split("/")
        time = template['time'].split(":")
        try:
            start_date = datetime.datetime(int(date[2]),
                                           int(date[0]),
                                           int(date[1]),
                                           int(time[0]),
                                           int(time[1]))
        except (ValueError, IndexError):
            start_date = ""
        if template.get('slug', ''):

            @permission_required("graphs.change_graph_reports",
                                 (Graph, "slug", "graph_slug"),
                                 return_403=True)
            def do_edit(request, template, **kwargs):
                template_inst = get_object_or_404(
                    ReportTemplate, slug=template['slug']
                )
                last_run = template_inst.last_run
                f = ReportTemplateForm({
                    "name": template['name'],
                    "start_date": start_date,
                    "frequency": template['frequency'],
                    "layout": template['layout'],
                    "description": template['description'],
                    "graph": graph.id,
                    "is_disabled": template['is_disabled']},
                    instance=template_inst)
                if not f.is_valid():
                    template["errors"] = f.errors
                    new_template = None
                else:
                    new_template = f.save()
                    for old in new_template.email_to.all():
                        if old.username not in template["collabs"]:
                            new_template.email_to.remove(old)
                    new_template.last_run = last_run
                    new_template.save()

                return new_template

            new_template = do_edit(request, template, graph_slug=graph_slug)
            if isinstance(new_template, HttpResponse):
                return new_template

        else:
            f = ReportTemplateForm({"name": template['name'],
                                    "start_date": start_date,
                                    "frequency": template['frequency'],
                                    "layout": template['layout'],
                                    "description": template['description'],
                                    "is_disabled": template["is_disabled"],
                                    "graph": graph.id})
            if not f.is_valid():
                template["errors"] = f.errors
            else:
                new_template = f.save()
        if not template.get("errors", ""):
            for collab in template["collabs"]:
                collab = User.objects.get(username=collab["id"])
                new_template.email_to.add(collab)
            query_set = set()
            for row in template['layout']['layout']:
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
            new_template.save()
    return HttpResponse(json.dumps(template), content_type='application/json')


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def preview_report_pdf(request, graph_slug):
    parsed_url = urlparse.urlparse(
        request.build_absolute_uri()
    )
    template_slug = request.GET.get('template', '')
    domain = parsed_url.hostname
    csrftoken = request.COOKIES.get('csrftoken', 'nocsrftoken')
    sessionid = request.COOKIES.get('sessionid', 'nosessionid')
    filename = phantom_process(
        parsed_url.scheme,
        parsed_url.netloc,
        pdf_gen_view,
        graph_slug,
        template_slug,
        domain,
        csrftoken,
        sessionid,
        SECRET
    )
    try:
        with open(filename) as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename={0}'.format(
                filename
            )
            pdf.close()
    except IOError, e:
        response = HttpResponse('Sorry there has been a IOError:' + e.strerror)
    try:
        os.unlink(filename)
    except IOError, e:
        response = HttpResponse('Sorry there has been a IOError:' + e.strerror)
    return response


@login_required
@is_enabled(settings.ENABLE_REPORTS)
@permission_required("graphs.view_graph_reports",
                     (Graph, "slug", "graph_slug"), return_403=True)
def pdf_view(request, graph_slug, report_id):
    report = Report.objects.get(pk=int(report_id))
    filename = os.path.join(settings.MEDIA_ROOT, report.report_file.name)
    try:
        with open(filename) as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename={0}'.format(
                filename
            )
            pdf.close()
    except IOError, e:
        response = HttpResponse('Sorry there has been a IOError:' + e.strerror)
    return response


def paginate(itrbl, per_page, page):
    paginator = Paginator(itrbl, per_page)
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
