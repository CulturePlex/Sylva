# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('base.views',
    # index
    url(r'^$', 'index', name="index"),
    # dashboard
    url(r'^dashboard/$', 'dashboard', name="dashboard"),
)
