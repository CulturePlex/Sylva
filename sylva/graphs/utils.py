# -*- coding: utf-8 -*-
from graphs.models import Graph


def graph_last_modified(request, graph_slug, *args, **kwargs):
    try:
        graph = Graph.objects.get(slug=graph_slug)
    except Graph.DoesNotExist:
        return None
    return graph.last_modified
