# -*- coding: utf-8 -*-
from django.template import Library
from django.db.models import Count

register = Library()

@register.inclusion_tag('graphs_info.html', takes_context=True)
def graph_info(context, graph):
    return {'graph': graph, 'user': context["user"]}

@register.inclusion_tag('toolbar.html', takes_context=True)
def toolbar(context, on):
    return {'on': on, 'graph': context["graph"]}
