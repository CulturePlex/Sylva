# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('schemas.views',
    # edit
    url(r'^(?P<graph_id>\d+)/$', 'schema_edit', name="schema_edit"),

    # node type create
    url(r'^(?P<graph_id>\d+)/types/create/$', 'schema_nodetype_create',
        name="schema_nodetype_create"),

    # relationship type create
    url(r'^(?P<graph_id>\d+)/allowed/create/$',
        'schema_relationshiptype_create',
        name="schema_relationshiptype_create"),
)
