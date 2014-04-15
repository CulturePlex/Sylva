# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('analytics.views',
    # analytic test
    url(r'^(?P<graph_slug>[\w-]+)/analytics/$', 'test_analytics',
        name="test_analytics"),
)
