# -*- coding: utf-8 -*-
# from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns(
    'queries.views',

    # list of queries
    url(r'^(?P<graph_slug>[\w-]+)/$', 'queries_list',
        name="queries_list"),

    # current query builder
    url(r'^(?P<graph_slug>[\w-]+)/new/$', 'queries_new',
        name="queries_new"),
    url(r'^(?P<graph_slug>[\w-]+)/new/results/$', 'queries_new_results',
        name="queries_new_results"),

    # edit and run query
    url(r'^(?P<graph_slug>[\w-]+)/query/(?P<query_id>\d+)/edit/$',
        'queries_query_edit',
        name="queries_query_edit"),
    url(r'^(?P<graph_slug>[\w-]+)/query/(?P<query_id>\d+)/results/$',
        'queries_query_results',
        name="queries_query_results"),

    # delete query
    url(r'^(?P<graph_slug>[\w-]+)/query/(?P<query_id>\d+)/delete/$',
        'queries_query_delete',
        name="queries_query_delete"),

    # another urls
    url(r'^(?P<graph_slug>[\w-]+)/query/$', 'queries_query',
        name="queries_query"),
    url(r'^(?P<graph_slug>[\w-]+)/query/collaborators/$',
        'graph_query_collaborators',
        name="graph_query_collaborators"),
)
