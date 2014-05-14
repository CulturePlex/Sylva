# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.conf import settings
from django.http import Http404
from django.shortcuts import (render_to_response, get_object_or_404,
                              HttpResponse)
from django.template import RequestContext
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from data.models import Data
from graphs.models import Graph
from schemas.models import NodeType, RelationshipType


def search(request, graph_slug, node_type_id=None, relationship_type_id=None):
    graph = get_object_or_404(Graph, slug=graph_slug)
    if request.GET:
        data = request.GET.copy()
    else:
        data = request.POST.copy()
    node_results = []
    relationship_results = []
    if data:
        q = data.get("q", "")
        analytics = bool(data.get("analytics", False))
        display = bool(data.get("display", True))

        if node_type_id:
            node_types = NodeType.objects.filter(id=node_type_id,
                                                 schema__graph=graph)
        else:
            node_types = graph.schema.nodetype_set.all()
        for node_type in node_types:
            result = {}
            result["type"] = node_type
            result["key"] = node_type.name
            query = graph.Q()
            if display:
                properties = node_type.properties.filter(display=True)
                if not properties:
                    properties = node_type.properties.all()[:2]
            else:
                properties = node_type.properties.all()
            for prop in properties:
                query |= graph.Q(prop.key, icontains=q, nullable=True)
            nodes = node_type.filter(query)
            if nodes:
                result["list"] = nodes
                node_results.append(result)
        # Everything before this point is for normal and analytics mode searchs
        if analytics:
            if ((request.is_ajax() or settings.DEBUG) and request.POST):
                node_ids = []
                for node_result in node_results:
                    node_ids.extend(
                        [str(node.id) for node in node_result["list"]])
                result = {'nodeIds': node_ids}
                return HttpResponse(json.dumps(result), status=200,
                                    mimetype='application/json')
            raise Http404(
                _("Error: Invalid request (expected an AJAX request)"))
        else:
            # Beyond this point everythin is for normal search
            if relationship_type_id:
                filter_args = {
                    "id": relationship_type_id,
                    "schema__graph": graph}
                relationship_types = RelationshipType.objectsfilter(
                    **filter_args)
            else:
                relationship_types = graph.schema.relationshiptype_set.all()
            for relationship_type in relationship_types:
                result = {}
                result["type"] = relationship_type
                result["key"] = relationship_type.name
                query = graph.Q()
                if display:
                    properties = relationship_type.properties.filter(
                        display=True)
                    if not properties:
                        properties = relationship_type.properties.all()[:2]
                else:
                    properties = relationship_type.properties.all()
                for prop in properties:
                    query |= graph.Q(prop.key, icontains=q, nullable=True)
                rels = graph.relationships
                relationships = rels.filter(query, label=relationship_type.id)
                if relationships:
                    result["list"] = relationships
                    relationship_results.append(result)
    return render_to_response('search_results.html', {
                              "graph": graph,
                              "node_results": node_results,
                              "relationship_results": relationship_results,
                              "file_results": []},
                              context_instance=RequestContext(request))


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_search(request, graph_slug):
    return search(request, graph_slug)


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_nodetype_search(request, graph_slug, node_type_id=None):
    return search(request, graph_slug, node_type_id=node_type_id)


@permission_required("data.view_data", (Data, "graph__slug", "graph_slug"),
                     return_403=True)
def graph_relationshiptype_search(request, graph_slug,
                                  relationship_type_id=None):
    return search(request, graph_slug,
                  relationship_type_id=relationship_type_id)
