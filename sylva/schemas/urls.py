# -*- coding: utf-8 -*-
# from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('schemas.views',
    # edit
    url(r'^(?P<graph_slug>[\w-]+)/$', 'schema_edit', name="schema_edit"),

    # node type create
    url(r'^(?P<graph_slug>[\w-]+)/types/create/$', 'schema_nodetype_create',
        name="schema_nodetype_create"),

    # node type edit
    url(r'^(?P<graph_slug>[\w-]+)/types/(?P<nodetype_id>\d+)/edit/$',
        'schema_nodetype_edit',
        name="schema_nodetype_edit"),

    # node type delete
    url(r'^(?P<graph_slug>[\w-]+)/types/(?P<nodetype_id>\d+)/delete/$',
        'schema_nodetype_delete',
        name="schema_nodetype_delete"),

    # node type properties mend
    url(r'^(?P<graph_slug>[\w-]+)/types/(?P<nodetype_id>\d+)/properties/$',
        'schema_nodetype_properties_mend',
        name="schema_nodetype_properties_mend"),

    # relationship type create
    url(r'^(?P<graph_slug>[\w-]+)/allowed/create/$',
        'schema_relationshiptype_create',
        name="schema_relationshiptype_create"),

    # relationship type edit
    url(r'^(?P<graph_slug>[\w-]+)/allowed/(?P<relationshiptype_id>\d+)/edit/$',
        'schema_relationshiptype_edit',
        name="schema_relationshiptype_edit"),

    # relationship type delete
    url(r'^(?P<graph_slug>[\w-]+)/allowed/(?P<relationshiptype_id>\d+)/delete/$',
        'schema_relationshiptype_delete',
        name="schema_relationshiptype_delete"),

    # relationship type properties mend
    url(r'^(?P<graph_slug>[\w-]+)/allowed/(?P<relationshiptype_id>\d+)/properties/$',
        'schema_relationshiptype_properties_mend',
        name="schema_relationshiptype_properties_mend"),

    # export schema
    url(r'^(?P<graph_slug>[\w-]+)/diagram/$',
        'schema_diagram_positions',
        name="schama_diagram_positions"),

    # export schema
    url(r'^(?P<graph_slug>[\w-]+)/export/$',
        'schema_export',
        name="schema_export"),

    # import schema
    url(r'^(?P<graph_slug>[\w-]+)/import/$',
        'schema_import',
        name="schema_import"),

)
