# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('base.views',
    # index
    url(r'^$', 'index', name="index"),
    # dashboard
    url(r'^dashboard/$', 'dashboard', name="dashboard"),
    # introductory guide
    url(r'^get-started/$', TemplateView.as_view(template_name="get_started.html"),
        name="get_started"),
    # user guide
    url(r'^guide/$', TemplateView.as_view(template_name="user_guide.html"),
        name="user_guide"),
)
