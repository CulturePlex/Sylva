# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('analytics.views',
    # dump
    url(r'^(?P<graph_slug>[\w-]+)/dump/$', 'dump',
        name="dump"),

    # analytic
    url(r'^(?P<graph_slug>[\w-]+)/analytic/$', 'analytic',
        name="analytic"),

    # connected components
    url(r'^(?P<graph_slug>[\w-]+)/connected_components/$',
        'connected_components', name="connected_components"),

    # graph coloring
    url(r'^(?P<graph_slug>[\w-]+)/graph_coloring/$',
        'graph_coloring', name="graph_coloring"),

    # kcore
    url(r'^(?P<graph_slug>[\w-]+)/kcore/$',
        'kcore', name="kcore"),

    # pagerank
    url(r'^(?P<graph_slug>[\w-]+)/pagerank/$',
        'pagerank', name="pagerank"),

    # shortest path
    url(r'^(?P<graph_slug>[\w-]+)/shortest_path/$',
        'shortest_path', name="shortest_path"),

    # triangle counting
    url(r'^(?P<graph_slug>[\w-]+)/triangle_counting/$',
        'triangle_counting', name="triangle_counting"),

    # betweenness centrality
    url(r'^(?P<graph_slug>[\w-]+)/betweenness_centrality/$',
        'betweenness_centrality', name="betweenness_centrality"),

    # task state
    url(r'^(?P<graph_slug>[\w-]+)/task_state/$',
        'task_state', name="task_state"),

    # get results
    url(r'^(?P<graph_slug>[\w-]+)/get_results/$',
        'get_results', name="get_results"),
)
