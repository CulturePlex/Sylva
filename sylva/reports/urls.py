# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('reports.views',
    url(r'^$', 'reports_index_view', name='reports_index_view'),
)
