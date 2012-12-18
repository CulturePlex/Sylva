# -*- coding: utf-8 -*-
# from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('operators.views',
    # query
    url(r'^(?P<graph_slug>[\w-]+)/query/$', 'operator_query',
        name="operator_query"),

)
