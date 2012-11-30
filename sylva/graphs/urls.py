# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('graphs.views',
    # graph create
    url(r'^create/$', 'graph_create', name="graph_create"),

    # graph edit
    url(r'^(?P<graph_slug>[\w-]+)/edit/$', 'graph_edit', name="graph_edit"),

    # graph view
    url(r'^(?P<graph_slug>[\w-]+)/$', 'graph_view', name="graph_view"),

    # graph clone
    url(r'^(?P<graph_slug>[\w-]+)/clone/$', 'graph_clone', name="graph_clone"),

    # graph delete
    url(r'^(?P<graph_slug>[\w-]+)/delete/$', 'graph_delete', name="graph_delete"),

    # nodes view
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/$', 'graph_view',
        name="nodes_view"),

    # collaborators edit
    url(r'^(?P<graph_slug>[\w-]+)/collaborators/$', 'graph_collaborators',
        name="graph_collaborators"),
    url(r'^(?P<graph_slug>[\w-]+)/collaborators/lookup/$', 'graph_ajax_collaborators',
        name="graph_ajax_collaborators"),

    # user permissions update
    url(r'^(?P<graph_slug>[\w-]+)/collaborators/change_permission/$',
        'change_permission',
        name="change_permission"),

    # expand node ajax request (JSON)
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/expand/$',
        'expand_node', name="expand_node"),

    # graph data (JSON)
    url(r'^(?P<graph_slug>[\w-]+)/data/$', 'graph_data', name="graph_data"),

    # nodes data (JSON)
    url(r'^(?P<graph_slug>[\w-]+)/data/(?P<node_id>\d+)/$', 'graph_data',
        name="nodes_data"),
)
