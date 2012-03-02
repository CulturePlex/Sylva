# -*- coding: utf-8 -*-
from django.template import Library
from django.db.models import Count

register = Library()

@register.inclusion_tag('graphs_info.html')
def graph_info(graph):
    return {'graph': graph}
