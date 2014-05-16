# -*- coding: utf-8 -*-
from django import template

from analytics.models import Analytic

register = template.Library()


@register.filter
def get(value, key, default=None):
    return unicode(value.get(key, default))


@register.filter
def list_analytics(graph, algorithm):
    l = Analytic.objects.filter(
        algorithm=algorithm,
        dump__graph=graph).order_by('-task_start')[:10]
    return l
