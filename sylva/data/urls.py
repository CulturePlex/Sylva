# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('data.views',
    # nodes
    url(r'^(?P<graph_slug>[\w-]+)/nodes/$', 'nodes_list', name="nodes_list"),
    url(r'^(?P<graph_slug>[\w-]+)/nodes/lookup/$', 'nodes_lookup',
        name="nodes_lookup"),
    url(r'^(?P<graph_slug>[\w-]+)/types/(?P<node_type_id>\d+)/create/$',
        'nodes_create', name="nodes_create"),
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_type_id>\d+)/$',
        'nodes_list_full', name="nodes_list_full"),
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/relationships/$',
        'node_relationships', name="node_relationships"),
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/edit/$',
        'nodes_edit', name="nodes_edit"),
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/delete/$',
        'nodes_delete', name="nodes_delete"),

    # relationships
    url(r'^(?P<graph_slug>[\w-]+)/relationships/$', 'relationships_list',
        name="relationships_list"),
    url(r'^(?P<graph_slug>[\w-]+)/relationships/(?P<relationship_type_id>\d+)/$',
        'relationships_list_full', name="relationships_list_full"),
)
