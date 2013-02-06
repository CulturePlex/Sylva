# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('payments.views',
    url(r'^subscribe/basic/$', 'subscription_edit_create',
        {'plan_name': 'Basic'}, name='subscription_edit_create'),
    url(r'^subscribe/premium/$', 'subscription_edit_create',
        {'plan_name': 'Premium'}, name='subscription_edit_create'),
    url(r'^unsubscribe/$', 'subscription_cancel', name='subscription_cancel'),
    url(r'^welcome/$', 'subscription_welcome', name='subscription_welcome'),
)
