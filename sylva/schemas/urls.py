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

    # node type edit
    url(r'^(?P<graph_id>\d+)/types/(?P<nodetype_id>\d+)/edit/$',
        'schema_nodetype_edit',
        name="schema_nodetype_edit"),

    # node type delete
    url(r'^(?P<graph_id>\d+)/types/(?P<nodetype_id>\d+)/delete/$',
        'schema_nodetype_delete',
        name="schema_nodetype_delete"),

    # relationship type create
    url(r'^(?P<graph_id>\d+)/allowed/create/$',
        'schema_relationshiptype_create',
        name="schema_relationshiptype_create"),

    # relationship type edit
    url(r'^(?P<graph_id>\d+)/allowed/(?P<relationshiptype_id>\d+)/edit/$',
        'schema_relationshiptype_edit',
        name="schema_relationshiptype_edit"),

    # relationship type delete
    url(r'^(?P<graph_id>\d+)/allowed/(?P<relationshiptype_id>\d+)/delete/$',
        'schema_relationshiptype_delete',
        name="schema_relationshiptype_delete"),
)
