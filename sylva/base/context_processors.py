# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings

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
