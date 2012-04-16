# -*- coding: utf-8 -*-
from json import dumps

from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import (render_to_response, get_object_or_404,
                             redirect, HttpResponse)
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from data.models import Data, MediaNode
from data.forms import (NodeForm, RelationshipForm, TypeBaseFormSet,
                        MediaFileFormSet, MediaLinkFormSet,
                        ItemDeleteConfirmForm,
                        ITEM_FIELD_NAME)
from graphs.models import Graph
from schemas.models import NodeType, RelationshipType


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def graph_search(request, graph_slug, node_type_id=None,
                 relationship_type_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    data = request.GET.copy()
    results = []
    if data:
        q = data.get("q", "")
        display = bool(data.get("display", True))
        if node_type_id:
            node_types = NodeType.objects.filter(id=node_type_id)
        else:
            node_types = graph.schema.nodetype_set.all()
        for node_type in node_types:
            result = {}
            result["type"] = node_type
            result["key"] = node_type.name
            query_list = []
            if display:
                properties = node_type.properties.filter(display=True)
                if not properties:
                    properties = node_type.properties.all()[:2]
            else:
                properties = node_type.properties.all()
            for prop in properties:
                query = {
                    "property": prop.key,
                    "match": q,
                    "lookup": "contains",
                }
                query_list.append(query)
            nodes = graph.nodes.filter(label=node_type.id, *query_list)
            result["list"] = nodes
            results.append(result)
        json_nodes = []
        for node in nodes:
            json_nodes.append({
                "id": node.id,
                "display": node.display
            })
    return render_to_response('search_results.html', {
                                "graph": graph,
                                "results": results,
                              }, context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def graph_nodetype_search(request, graph_slug, node_type_id=None):
    return graph_search(request, graph_slug, node_type_id=node_type_id)


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"))
def graph_relationshiptype_search(request, graph_slug,
                                  relationship_type_id=None):
    return graph_search(request, graph_slug,
                        relationship_type_id=relationship_type_id)
