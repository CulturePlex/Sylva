# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def get(value, key, default=None):
    return unicode(value.get(key, default))


@register.filter
def list_analytics(graph, algorithm):
    l = graph.analytics.filter(algorithm=algorithm).order_by(
        '-task_start')[:10]
    return l
