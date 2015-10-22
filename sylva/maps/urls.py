# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('maps.views',
    # map view
    url(r'^(?P<graph_slug>[\w-]+)/$', 'map_view', name="map_view"),
)
