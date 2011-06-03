# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('base.views',

    # Index
    url(r'^$', 'index', name="index"),
)
