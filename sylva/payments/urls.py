# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('payments.views',
    url(r'^subscribe/$', 'subscription_create', name='subscription_create'),
    url(r'^unsubscribe/$', 'subscription_cancel', name='subscription_cancel'),
    url(r'^welcome/$', 'subscription_welcome', name='subscription_welcome'),
)
