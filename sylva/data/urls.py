# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('data.views',
    # list nodes
    url(r'^(?P<graph_id>\d+)/nodes/$', 'nodes_list', name="nodes_list"),
    url(r'^(?P<graph_id>\d+)/types/(?P<node_type_id>\d+)/create/$', 
        'nodes_create', name="nodes_create"),
    url(r'^(?P<graph_id>\d+)/nodes/(?P<node_type_id>\d+)/$', 
        'nodes_list_full', name="nodes_list_full"),

    # list relationships
    url(r'^(?P<graph_id>\d+)/relationships/$', 'relationships_list',
        name="relationships_list"),
    url(r'^(?P<graph_id>\d+)/relationships/(?P<relationship_type_id>\d+)/$', 
        'relationships_list_full', name="relationships_list_full"),
)
