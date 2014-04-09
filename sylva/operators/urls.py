# -*- coding: utf-8 -*-
# from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns(
    'operators.views',

    # query
    url(r'^(?P<graph_slug>[\w-]+)/builder/$', 'operator_builder',
        name="operator_builder"),
    url(r'^(?P<graph_slug>[\w-]+)/query/$', 'operator_query',
        name="operator_query"),
    url(r'^(?P<graph_slug>[\w-]+)/query/results/$', 'operator_query_results',
        name="operator_query_results"),
    url(r'^(?P<graph_slug>[\w-]+)/query/collaborators/$', 'graph_query_collaborators',
        name="graph_query_collaborators"),
    url(r'^(?P<graph_slug>[\w-]+)/builder/results/$', 'operator_builder_results',
        name="operator_builder_results"),
)
