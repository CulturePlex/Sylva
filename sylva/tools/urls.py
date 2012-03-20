# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('tools.views',
    # import tool
    url(r'^(?P<graph_slug>[\w-]+)/import/$', 'graph_import_tool',
        name="tool_import"),

    # ajax creation methods
    url(r'^(?P<graph_slug>[\w-]+)/ajax-node/create/$', 
        'ajax_node_create', name="ajax_node_create"),
    url(r'^(?P<graph_slug>[\w-]+)/ajax-relationship/create/$', 
        'ajax_relationship_create', name="ajax_relationship_create"),

    # export tool
    url(r'^(?P<graph_slug>[\w-]+)/export/$', 'graph_export_tool',
        name="tool_export"),
)
