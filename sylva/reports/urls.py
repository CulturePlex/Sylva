# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('reports.views',
    url(r'^(?P<graph_slug>[\w-]+)/$', 'reports_index_view'),
    url(r'^report-builder$', 'reports_endpoint'),
    url(r'^queries$', 'queries_endpoint'),
)
