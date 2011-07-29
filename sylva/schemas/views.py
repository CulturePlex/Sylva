# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from graphs.models import Graph


@login_required()
def schema_edit(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    return render_to_response('schemas_edit.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))
