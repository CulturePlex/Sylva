# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from userena.views import signup


def index(request):
    if request.user.is_authenticated():
        return redirect("dashboard")
    return render_to_response('index.html',
                              {'is_index': True},
                              context_instance=RequestContext(request))

def signup_redirect(request, *args, **kwargs):
    if request.user.is_authenticated() and request.user.is_superuser:
        return signup(request, *args, **kwargs)
    return redirect("index")

@login_required()
def dashboard(request):
    return render_to_response('dashboard.html',
                              {},
                              context_instance=RequestContext(request))
