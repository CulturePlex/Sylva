# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from guardian.shortcuts import get_objects_for_user
from userena.views import signin, signup

from graphs.models import Graph


def index(request):
    if request.user.is_authenticated():
        return redirect("dashboard")
    return render_to_response('index.html',
                              {'is_index': True},
                              context_instance=RequestContext(request))


def signin_redirect(request, *args, **kwargs):
    if request.user.is_authenticated() and request.user.is_superuser:
        return redirect("dashboard")
    return signin(request, *args, **kwargs)


def signup_redirect(request, *args, **kwargs):
    if request.user.is_authenticated() and request.user.is_superuser:
        return signup(request, *args, **kwargs)
    return redirect("index")


@login_required()
def dashboard(request):
    graphs = request.user.graphs.all()
    permissions = [("graphs.%s" % p) for p, v in Graph._meta.permissions]
    all_collaborations = get_objects_for_user(request.user, permissions,
                                              any_perm=True)
    collaborations = all_collaborations.exclude(pk__in=graphs)
    return render_to_response('dashboard.html',
                              {"graphs": graphs,
                               "collaborations": collaborations,
                               "instances": request.user.instances.all()},
                              context_instance=RequestContext(request))
