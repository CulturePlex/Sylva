# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('data.views',
    # edit
    url(r'/(?P<data_id>\d+)/edit/^', 'edit', name="data_edit"),
)
