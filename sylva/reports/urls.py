# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('reports.views',
    url(r'^(?P<graph_slug>[\w-]+)/$', 'reports_index_view'),
    url(r'^(?P<graph_slug>[\w-]+)/reports$', 'reports_endpoint'),
    url(r'^(?P<graph_slug>[\w-]+)/queries$', 'queries_endpoint'),
)
