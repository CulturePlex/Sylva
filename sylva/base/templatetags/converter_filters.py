# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def to_javascript(value):
    return mark_safe("JSON.parse('{0}')".format(json.dumps(value)))
