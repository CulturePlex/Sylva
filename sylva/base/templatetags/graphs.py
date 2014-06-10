# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import Library
from django.utils.translation import gettext as _

from data.models import Data
from search.forms import SearchForm
from schemas.models import Schema


register = Library()


@register.inclusion_tag('graphs_info.html', takes_context=True)
def graph_info(context, graph, show_edit=None):
    return {'graph': graph,
            'show_edit': bool(show_edit),
            'user': context["user"]}


@register.inclusion_tag('toolbar.html', takes_context=True)
def toolbar(context, on):
    request = context.get("request", None)
    if request:
        search_form = SearchForm(data=request.GET)
    else:
        search_form = SearchForm()
    return {'on': on,
            'graph': context["graph"],
            'node_type': context.get("node_type", None),
            'search_form': search_form,
            'ENABLE_CLONING': settings.ENABLE_CLONING}


@register.inclusion_tag('breadcrumb.html', takes_context=True)
def breadcrumb(context, *links):
    breads = []
    for link in links:
        if isinstance(link, Data):
            breads.append((link.get_absolute_url(), _("Data")))
        elif isinstance(link, Schema):
            breads.append((link.get_absolute_url(), _("Schema")))
        elif hasattr(link, "get_absolute_url"):
            breads.append((link.get_absolute_url(), link))
        else:
            breads.append(("", link))
    return {'links': breads,
            'graph': context.
            get("graph", None)}


@register.inclusion_tag('graphs_visualization.html', takes_context=True)
def graph_visualization(context, graph, analytics=True):
    analysis = graph.gdb.analysis()
    if analysis:
        algorithms = analysis.get_algorithms()
    else:
        algorithms = []
    return {'analytics': bool(analytics),
            'algorithms': algorithms,
            'graph': graph,
            'OPTIONS': context.get("OPTIONS", None)}
