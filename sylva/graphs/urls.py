# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('graphs.views',
    # create
    url(r'^create/$', 'graph_create', name="graph_create"),

    # edit
    url(r'^(?P<graph_slug>[\w-]+)/edit/$', 'graph_edit', name="graph_edit"),

    # view
    url(r'^(?P<graph_slug>[\w-]+)/$', 'graph_view', name="graph_view"),

    # clone
    url(r'^(?P<graph_slug>[\w-]+)/clone/$', 'graph_clone', name="graph_clone"),

    # delete
    url(r'^(?P<graph_slug>[\w-]+)/delete/$', 'graph_delete', name="graph_delete"),

    # collaborators edit
    url(r'^(?P<graph_slug>[\w-]+)/collaborators/$', 'graph_collaborators',
        name="graph_collaborators"),

    # user permissions update
    url(r'^(?P<graph_slug>[\w-]+)/collaborators/change_permission/$',
        'change_permission',
        name="change_permission"),

    # expand node ajax request
    url(r'^(?P<graph_slug>[\w-]+)/nodes/(?P<node_id>\d+)/expand/$',
        'expand_node',
        name="expand_node"),
)
