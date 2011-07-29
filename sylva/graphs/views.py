# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from graphs.forms import GraphForm
from graphs.models import Graph


@login_required()
def graph_view(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    return render_to_response('graphs_view.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))


@login_required()
def graph_edit(request, graph_id):
    return render_to_response('graphs_edit.html',
                              {},
                              context_instance=RequestContext(request))


@login_required()
def graph_create(request):
    form = GraphForm()
    if request.POST:
        data = request.POST.copy()
        form = GraphForm(data=data)
        if form.is_valid():
            graph = form.save(commit=False)
            graph.owner = request.user
            graph.save()
            redirect_url = reverse("dashboard")
            return redirect(redirect_url)
    return render_to_response('graphs_create.html',
                              {"form": form},
                              context_instance=RequestContext(request))


@login_required()
def graph_collaborators(request, graph_id):
    graph = get_object_or_404(Graph, id=graph_id)
    return render_to_response('graphs_collaborators.html',
                              {"graph": graph},
                              context_instance=RequestContext(request))
