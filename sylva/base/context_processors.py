# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site, RequestSite
from django.core.exceptions import ImproperlyConfigured


def project_name(request):
    return {'PROJECT_NAME': getattr(settings, "PROJECT_NAME", None)}


def google_api_key(request):
    return {'GOOGLE_API_KEY': getattr(settings, "GOOGLE_API_KEY", None),
            'GOOGLE_MAPS_API_KEY': getattr(settings,
                                           "GOOGLE_MAPS_API_KEY", None)}


def google_analytics_code(request):
    return {'GOOGLE_ANALYTICS_CODE': getattr(settings, "GOOGLE_ANALYTICS_CODE",
                                             None)}


def current_date(request):
    return {'CURRENT_DATE': datetime.now()}


def debug(request):
    return {'DEBUG': getattr(settings, "DEBUG", False)}


def logout(request):
    return {'LOGOUT_URL': getattr(settings, "LOGOUT_URL", "/accounts/logout/")}


def options(request):
    return {'OPTIONS': getattr(settings, "OPTIONS", {})}


def site(request):
    """Sets in the present context information about the current site."""

    # Current SiteManager already handles prevention of spurious
    # database calls. If the user does not have the Sites framework
    # installed, a RequestSite object is an appropriate fallback.
    try:
        models.get_app('sites')
        site_obj = Site.objects.get_current()
    except ImproperlyConfigured:
        site_obj = RequestSite(request)
    return {'site': site_obj}
