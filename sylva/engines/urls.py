# -*- coding: utf-8 -*-
# from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('engines.views',
    # edit
    url(r'/(?P<engine_id>\d+)/edit/^', 'edit', name="engine_edit"),
)
