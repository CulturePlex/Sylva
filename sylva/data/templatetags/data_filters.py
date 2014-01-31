# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter(name='is_not_none')
def is_not_none(val):
    return val is not None and val is not u''


@register.filter(name='is_not_default')
def is_not_default(val):
    return val is not None and val is not u'default'
