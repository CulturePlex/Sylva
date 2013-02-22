# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from base.decorators import is_enabled
from engines.models import Instance


@login_required()
def edit(request):
    return render_to_response('dashboard.html',
                              {},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_PAYMENTS)
def instance_activate(request, instance_id):
    instance = get_object_or_404(Instance, pk=instance_id)
    if request.method == 'POST':
        data = request.POST.copy()
        attrs = ["schema", "username", "password", "host", "port", "path",
                 "query", "fragment", "options"]
        for attr in attrs:
            value = data.get(attr, None)
            if value:
                setattr(instance, attr, value)
        if (not instance.activated
                and data.get("activation", None) == instance.activation):
            instance.activation = None
            instance.activated = True
            instance.save()
        else:
            return HttpResponse(status=409)  # Conflict
        return HttpResponse(status=204)  # No Content
    else:
        return HttpResponse(status=304)  # Not Modified
