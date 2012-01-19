# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tools.views',
    # import tool
    url(r'^(?P<graph_id>\d+)/import_tool/$', 'graph_import_tool',
        name="import_tool"),

    # ajax creation methods
    url(r'^(?P<graph_id>\d+)/ajax-node/create/$', 
        'ajax_node_create', name="ajax_node_create"),
)
