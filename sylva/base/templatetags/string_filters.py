# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def replacechar(value, chars):
    return value.replace(chars[0], chars[1])
