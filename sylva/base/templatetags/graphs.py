# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.translation import gettext as _

from data.models import Data
from schemas.models import Schema


register = Library()

@register.inclusion_tag('graphs_info.html', takes_context=True)
def graph_info(context, graph, show_edit=None):
    return {'graph': graph,
            'show_edit': bool(show_edit),
            'user': context["user"]}

@register.inclusion_tag('toolbar.html', takes_context=True)
def toolbar(context, on):
    return {'on': on,
            'graph': context["graph"],
            'node_type': context.get("node_type", None)}

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
            'graph': context.get("graph", None)}
