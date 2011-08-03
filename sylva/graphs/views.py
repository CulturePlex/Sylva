# -*- coding: utf-8 -*-
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from data.models import Data
from graphs.forms import GraphForm
from graphs.models import Graph
from schemas.models import Schema


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
    form = GraphForm(user=request.user)
    if request.POST:
        data = request.POST.copy()
        form = GraphForm(data=data, user=request.user)
        if form.is_valid():
            with transaction.commit_on_success(): 
                instance = form.cleaned_data["instance"]
                graph = form.save(commit=False)
                graph.owner = request.user
                data = Data.objects.create(instance=instance)
                graph.data = data
                schema = Schema.objects.create()
                graph.schema = schema
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
