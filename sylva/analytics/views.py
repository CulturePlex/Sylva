# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import (get_object_or_404, render_to_response,
                              HttpResponse)
from celery.result import AsyncResult

from guardian.decorators import permission_required

from base.decorators import is_enabled
from graphs.models import Graph, Data


@is_enabled(settings.ENABLE_ANALYTICS)
@permission_required("analytics.test_analytics", (Data, "graph__slug", "graph_slug"), return_403=True)
def test_analytics(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    analytic = graph.analysis.run('pagerankAux')
    status = AsyncResult(analytic.task_id)

    while not status.ready():
        print status.ready()

    return HttpResponse(json.dumps({analytic.results}))
