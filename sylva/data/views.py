# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.template import RequestContext


@login_required()
def edit(request):
    return render_to_response('dashboard.html',
                              {},
                              context_instance=RequestContext(request))
