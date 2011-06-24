# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# from django.contrib import admin
# from admin import admin_site
admin.autodiscover()

urlpatterns = patterns('',
    # base
    url(r'^', include('base.urls')),

    # accounts
    url(r'^accounts/signup/', "base.views.signup_redirect", name="signup"),
    url(r'^accounts/', include('userena.urls')),

    # i18n
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # messaging
    url(r'^messages/', include('userena.contrib.umessages.urls')),

    # data
    # url(r'^data/', include('data.urls')),

    # engines
    # url(r'^engines/', include('engines.urls')),

    # graphs
    # url(r'^graphs/', include('graphs.urls')),

    # operators
    # url(r'^operators/', include('operators.urls')),

    # schemas
    # url(r'^schemas/', include('schemas.urls')),

    # tools
    # url(r'^tools/', include('tools.urls')),

    # admin_media
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/', include(admin_site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',

        # static server
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),

        # static media server
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
   )
