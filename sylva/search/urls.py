# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('search.views',
    # graph search
    url(r'^(?P<graph_slug>[\w-]+)/$', 'graph_search', name="graph_search"),

    # search by node type
    url(r'^(?P<graph_slug>[\w-]+)/types/(?P<node_type_id>\d+)/$',
        'graph_nodetype_search', name="graph_nodetype_search"),

    # search by relationship type
    url(r'^(?P<graph_slug>[\w-]+)/allowes/(?P<relationship_type_id>\d+)/$',
        'graph_relationshiptype_search', name="graph_relationshiptype_search"),
)
