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
    url(r'^(?P<graph_id>\d+)/edit/$', 'graph_edit', name="graph_edit"),

    # view
    url(r'^(?P<graph_id>\d+)/$', 'graph_view', name="graph_view"),

    # collaborators edit
    url(r'^(?P<graph_id>\d+)/collaborators/$', 'graph_collaborators',
        name="graph_collaborators"),

    # user permissions update
    url(r'^(?P<graph_id>\d+)/collaborators/change_permission/$',
        'change_permission',
        name="change_permission"),
)
