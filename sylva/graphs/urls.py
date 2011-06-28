# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('graphs.views',
    # edit
    url(r'/(?P<graph_id>\d+)/edit/^', 'edit', name="graph_edit"),
)
