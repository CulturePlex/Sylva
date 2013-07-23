# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def get(value, key, default=None):
    return unicode(value.get(key, default))
