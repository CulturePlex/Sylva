# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('payments.views',
    url(r'^subscribe/basic/$', 'subscription_edit_create',
        {'plan_id': '2'}, name='subscription_basic'),
    url(r'^subscribe/premium/$', 'subscription_edit_create',
        {'plan_id': '3'}, name='subscription_premium'),
    url(r'^unsubscribe/$', 'subscription_cancel', name='subscription_cancel'),
    url(r'^welcome/$', 'subscription_welcome', name='subscription_welcome'),
    url(r'^plans/$', 'subscription_plans', name='subscription_plans'),
    url(r'^subscriptions/$', 'subscription_list', name='subscription_list'),
)
