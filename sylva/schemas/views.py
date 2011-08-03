# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect

from graphs.models import Graph
from schemas.forms import NodeTypeForm
from schemas.models import NodeType, RelationshipType


@login_required()
def schema_edit(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    nodetypes = NodeType.objects.filter(schema__graph__id=graph_id)
    reltypes = None
    form = NodeTypeForm()
    if request.POST:
        data = request.POST.copy()
        form = NodeTypeForm(data=data)
        if form.is_valid():
            node_type = form.save(commit=False)
            node_type.schema = graph.schema
            node_type.save()
            redirect_url = reverse("dashboard")
            return redirect(redirect_url)
    return render_to_response('schemas_edit.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes,
                               "node_type_form": form},
                              context_instance=RequestContext(request))
