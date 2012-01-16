# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def get(dict, key, default=None):
    return value.get(key, default)
