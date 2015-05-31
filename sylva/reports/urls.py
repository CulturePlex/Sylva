# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('reports.views',
    url(r'^(?P<graph_slug>[\w-]+)/$',
        'reports_index_view', name="reports"),
    url(r'^(?P<graph_slug>[\w-]+)/list$',
        'list_endpoint', name='list'),
    url(r'^(?P<graph_slug>[\w-]+)/templates$',
        'templates_endpoint', name='templates'),
    url(r'^(?P<graph_slug>[\w-]+)/history$',
        'history_endpoint', name='history'),
    url(r'^(?P<graph_slug>[\w-]+)/builder$',
        'builder_endpoint', name='builder'),
    url(r'^(?P<graph_slug>[\w-]+)/delete$',
        'delete_endpoint', name='delete'),
    url(r'^(?P<graph_slug>[\w-]+)/pdf/preview$',
        'preview_report_pdf', name='preview'),
    url(r'^(?P<graph_slug>[\w-]+)/pdf/(?P<report_id>[\w-]+)$',
        'pdf_view', name='pdf'),
    url(r'^(?P<graph_slug>[\w-]+)/pdfgen/(?P<template_slug>[\w-]+)$',
        'pdf_gen_view', name='pdf_gen'),
    url((r'^(?P<graph_slug>[\w-]+)/(?P<template_slug>[\w-]+)/' +
         '(?P<report_id>[\w-]+)$'),
        'fullscreen_view', name='fullscreen_view'),
    url(r'^(?P<graph_slug>[\w-]+)/partials$',
        'partial_view', name='partials'),
)
