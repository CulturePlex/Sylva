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

    # list relationships
    url(r'^(?P<graph_id>\d+)/relationships/$', 'relationships_list',
        name="relationships_list"),
)
