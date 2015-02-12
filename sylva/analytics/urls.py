# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'analytics.views',

    # Run an algorithm
    url(r'^(?P<graph_slug>[\w-]+)/run/$',
        'analytics_run', name="analytics_run"),

    # Estimate time for an algorithm
    url(r'^(?P<graph_slug>[\w-]+)/eta/$',
        'analytics_estimate', name="analytics_estimate"),

    # Get status of an algorithm
    url(r'^(?P<graph_slug>[\w-]+)/status/$',
        'analytics_status', name="analytics_status"),

    # Get analytic object
    url(r'^(?P<graph_slug>[\w-]+)/analytic/$',
        'analytics_analytic', name="analytics_analytic"),

    # Get the list of nodes or relationships of a specific dump
    url(r'^(?P<graph_slug>[\w-]+)/dump/$',
        'analytics_dump', name="analytics_dump"),

    # Stop the task execution
    url(r'^(?P<graph_slug>[\w-]+)/stop/$',
        'analytics_stop', name="analytics_stop"),
)
