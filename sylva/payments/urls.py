# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('payments.views',
    url(r'^subscribe/basic/$', 'subscription_edit_create',
        {'plan_id': '2'}, name='subscription_basic'),
    url(r'^subscribe/premium/$', 'subscription_edit_create',
        {'plan_id': '3'}, name='subscription_premium'),
    url(r'^unsubscribe/$', 'subscription_cancel', name='subscription_cancel'),
    url(r'^welcome/$', 'subscription_welcome', name='subscription_welcome'),
    url(r'^plans/$', TemplateView.as_view(template_name='payments/plans.html'),
        name='subscription_plans'),
)
