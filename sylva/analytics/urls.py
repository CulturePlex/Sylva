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

    # eta connected components
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_connected_components/$',
        'get_eta_connected_components',
        name="get_eta_connected_components"),

    # graph coloring
    url(r'^(?P<graph_slug>[\w-]+)/graph_coloring/$',
        'graph_coloring', name="graph_coloring"),

    # eta graph coloring
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_graph_coloring/$',
        'get_eta_graph_coloring',
        name="get_eta_graph_coloring"),

    # kcore
    url(r'^(?P<graph_slug>[\w-]+)/kcore/$',
        'kcore', name="kcore"),

    # eta kcore
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_kcore/$',
        'get_eta_kcore',
        name="get_eta_kcore"),

    # pagerank
    url(r'^(?P<graph_slug>[\w-]+)/pagerank/$',
        'pagerank', name="pagerank"),

    # eta pagerank
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_pagerank/$',
        'get_eta_pagerank',
        name="get_eta_pagerank"),

    # shortest path
    url(r'^(?P<graph_slug>[\w-]+)/shortest_path/$',
        'shortest_path', name="shortest_path"),

    # eta shortest path
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_shortest_path/$',
        'get_eta_shortest_path',
        name="get_eta_shortest_path"),

    # triangle counting
    url(r'^(?P<graph_slug>[\w-]+)/triangle_counting/$',
        'triangle_counting', name="triangle_counting"),

    # eta triangle counting
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_triangle_counting/$',
        'get_eta_triangle_counting',
        name="get_eta_triangle_counting"),

    # betweenness centrality
    url(r'^(?P<graph_slug>[\w-]+)/betweenness_centrality/$',
        'betweenness_centrality', name="betweenness_centrality"),

    # eta betweenness centrality
    url(r'^(?P<graph_slug>[\w-]+)/get_eta_betweenness_centrality/$',
        'get_eta_betweenness_centrality',
        name="get_eta_betweenness_centrality"),

    # task state
    url(r'^(?P<graph_slug>[\w-]+)/task_state/$',
        'task_state', name="task_state"),

    # get analytic
    url(r'^(?P<graph_slug>[\w-]+)/get_analytic/$',
        'get_analytic', name="get_analytic"),
)
