# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from accounts.forms import UserProfileEditForm

# API imports
from data import api as data_api
from graphs import api as graphs_api
from schemas import api as schemas_api

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('sylva.views',
    # index
    url(r'^$', 'index', name="index"),
    # dashboard
    url(r'^dashboard/$', 'dashboard', name="dashboard"),
    # introductory guide
    url(r'^get-started/$', TemplateView.as_view(template_name="get_started.html"),
        name="get_started"),
    # user guide
    url(r'^guide/$', TemplateView.as_view(template_name="user_guide.html"),
        name="user_guide"),
)

urlpatterns += patterns('',
    # accounts
    url(r'^accounts/(?P<username>[\w-]+)/edit/', "userena.views.profile_edit",
        {'edit_profile_form': UserProfileEditForm}),
    url(r'^accounts/signin/', "sylva.views.signin_redirect", name="signin"),
    url(r'^accounts/signup/', "sylva.views.signup_redirect", name="signup"),
    url(r'^accounts/', include('userena.urls')),

    # python i18n
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # js i18n
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),

    # messaging
    url(r'^messages/', include('userena.contrib.umessages.urls')),

    # data
    url(r'^data/', include('data.urls')),

    # engines
    url(r'^engines/', include('engines.urls')),

    # graphs
    url(r'^graphs/', include('graphs.urls')),

    # schemas
    url(r'^schemas/', include('schemas.urls')),

    # search
    url(r'^search/', include('search.urls')),

    # tools
    url(r'^tools/', include('tools.urls')),

    # tinyMCE
    url(r'^tinymce/', include('tinymce.urls')),

    # admin_media
    url(r'^admin/', include(admin.site.urls)),

    # payments
    url(r'^payments/', include('payments.urls')),
    url(r'^zebra/', include('zebra.urls', namespace="zebra",
                            app_name='zebra')),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    url(r'^terms/$', 'flatpage', {'url': '/terms/'}, name='terms'),
    url(r'^privacy/$', 'flatpage', {'url': '/privacy/'}, name='privacy'),
)

if settings.ENABLE_QUERIES:
    urlpatterns += patterns('',
        # queries
        url(r'^queries/', include('queries.urls')),
    )

if settings.ENABLE_REPORTS:
    urlpatterns += patterns('',
        # reports
        url(r'^reports/', include('reports.urls')),
    )

if settings.ENABLE_ANALYTICS:
    urlpatterns += patterns('',
        # analytics
        url(r'^analytics/', include('analytics.urls')),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        # login as any user
        url(r"^su/", include("django_su.urls")),

        # static server
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),

        # static media server
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
    try:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
    except ImportError:
        pass

if settings.TEST and not settings.DEBUG:
    urlpatterns += patterns('',
        # static server
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),

        # static media server
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )

# API url patterns
urlpatterns += patterns('sylva.views',
    # index url for API
    url(r'^api/$', 'api_index', name='api_index'),
    # url to get API token
    url(r'^api/token/$', 'api_token', name='api_token'),
)

urlpatterns += patterns('',
    # url to GET and POST over graphs
    url(r'^api/graphs/$',
        graphs_api.GraphsView.as_view(), name='api_graphs'),

    # url to GET, PATCH, PUT and DELETE over a graph
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/$',
        graphs_api.GraphView.as_view(), name='api_graph'),

    # url to GET and POST over node types
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/types/nodes/$',
        schemas_api.NodeTypesView.as_view(), name='api_node_types'),

    # url to GET and POST over relationship types
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/types/relationships/$',
        schemas_api.RelationshipTypesView.as_view(),
        name='api_relationship_types'),

    # url to GET and POST over a node type
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/nodes/(?P<type_slug>[\w-]+)/$',
        schemas_api.NodeTypeView.as_view(),
        name='api_node_type'),

    # url to GET and POST over a relationship type
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/relationships/(?P<type_slug>[\w-]+)/$',
        schemas_api.RelationshipTypeView.as_view(),
        name='api_relationship_type'),

    # url to GET, PATCH and PUT over a node type schema
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/nodes/(?P<type_slug>[\w-]+)/schema/$',
        schemas_api.NodeTypeSchemaView.as_view(),
        name='api_node_type_schema'),

    # url to GET, PATCH and PUT over a relationship type schema
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/relationships/(?P<type_slug>[\w-]+)/schema/$',
        schemas_api.RelationshipTypeSchemaView.as_view(),
        name='api_relationship_type_schema'),

    # url to GET, PATCH and PUT over a node type schema properties
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/nodes/(?P<type_slug>[\w-]+)/schema/properties/$',
        schemas_api.NodeTypeSchemaPropertiesView.as_view(),
        name='api_node_type_schema_properties'),

    # url to GET, PATCH and PUT over a relationship type schema properties
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/relationships/(?P<type_slug>[\w-]+)/schema/properties/$',
        schemas_api.RelationshipTypeSchemaPropertiesView.as_view(),
        name='api_relationship_type_schema_properties'),

    # url to GET and POST over a node type
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/nodes/(?P<type_slug>[\w-]+)/nodes/$',
        data_api.NodesView.as_view(),
        name='api_nodes'),

    # url to GET and POST over a relationship type
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/relationships/(?P<type_slug>[\w-]+)/relationships/$',
        data_api.RelationshipsView.as_view(),
        name='api_relationships'),

    # url to GET, PATCH, PUT and DELETE over a node
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/nodes/(?P<type_slug>[\w-]+)/nodes/(?P<node_id>\d+)/$',
        data_api.NodeView.as_view(),
        name='api_node'),

    # url to GET, PATCH, PUT and DELETE over a relationship
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)'
        '/types/relationships/(?P<type_slug>[\w-]+)/relationships/'
        '(?P<relationship_id>\d+)/$',
        data_api.RelationshipView.as_view(),
        name='api_relationship'),

    # urls for export with the API
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/export/graph/$',
        graphs_api.GraphCompleteExportView.as_view(),
        name='api_export_graph'),

    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/export/schema/$',
        graphs_api.GraphSchemaExportView.as_view(),
        name='api_export_schema'),

    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/export/data/$',
        graphs_api.GraphDataExportView.as_view(),
        name='api_export_data'),

    # urls for import with the API
    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/import/graph/$',
        graphs_api.GraphCompleteImportView.as_view(),
        name='api_import_graph'),

    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/import/schema/$',
        graphs_api.GraphSchemaImportView.as_view(),
        name='api_import_schema'),

    url(r'^api/graphs/(?P<graph_slug>[\w-]+)/import/data/$',
        graphs_api.GraphDataImportView.as_view(),
        name='api_import_data'),
)
