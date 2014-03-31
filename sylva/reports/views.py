# -*- coding: utf-8 -*-
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext

queries = ['query1', 'query2', 'query3', 'query4', 'query5']


def reports_index_view(request):
    return render_to_response('reports_index.html', RequestContext(request, {}))
