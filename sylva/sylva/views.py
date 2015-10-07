# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from guardian.shortcuts import get_objects_for_user
from rest_framework.authtoken.models import Token
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
    if (settings.OPTIONS.get("ENABLE_SIGNUP", False) or
            (request.user.is_authenticated() and request.user.is_superuser)):
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


@login_required()
def api_index(request):
    # We filter the tokens by user to show the user's token
    user = request.user
    user_tokens = Token.objects.filter(user=user)

    token = ""
    if len(user_tokens) > 0:
        token = user_tokens[0]
        token = token.key

    return render_to_response('api.html',
                              {"token": token},
                              context_instance=RequestContext(request))


@login_required()
def api_token(request, username):
    # We create the token for the user and return it
    # First, we check if we want to refresh or create a token
    data = request.POST
    data_form = data.items()

    user = request.user
    profile = user.profile

    user_tokens = Token.objects.filter(user=user)
    if len(user_tokens) > 0:
        token = user_tokens[0]
    else:
        token = None

    if len(data_form) > 0:
        # We check if the user already has a token
        # In that case we generate another one
        if token:
            token.delete()

        token = Token.objects.create(user=user)
        token = token.key

    return render_to_response('api_token.html',
                              {"user": user,
                               "profile": profile,
                               "token": token},
                              context_instance=RequestContext(request))
