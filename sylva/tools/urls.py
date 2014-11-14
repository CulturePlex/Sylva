# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('tools.views',
    # import tool
    url(r'^(?P<graph_slug>[\w-]+)/import/$', 'graph_import_tool',
        name="tool_import"),

    # ajax creation methods
    url(r'^(?P<graph_slug>[\w-]+)/ajax-nodes/create/$',
        'ajax_nodes_create', name="ajax_nodes_create"),
    url(r'^(?P<graph_slug>[\w-]+)/ajax-relationships/create/$',
        'ajax_relationships_create', name="ajax_relationships_create"),

    # export GEXF (Gephi)
    url(r'^(?P<graph_slug>[\w-]+)/export/gexf/$', 'graph_export_gexf',
        name="graph_export_gexf"),
    # export CSV
    url(r'^(?P<graph_slug>[\w-]+)/export/csv/$', 'graph_export_csv',
        name="graph_export_csv"),
    # export query as CSV
    url(r'^(?P<graph_slug>[\w-]+)/export/query_csv/$',
        'graph_export_queries_csv',
        name="graph_export_queries_csv"),
)
