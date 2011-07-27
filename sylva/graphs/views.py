# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from graphs.forms import GraphForm


@login_required()
def edit(request, graph_id):
    return render_to_response('dashboard.html',
                              {},
                              context_instance=RequestContext(request))


@login_required()
def create(request):
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
