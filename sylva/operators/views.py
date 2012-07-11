# -*- coding: utf-8 -*-
import json

from django.db import transaction
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import gettext as _

from guardian.decorators import permission_required

from graphs.models import Graph, Schema
from schemas.forms import (NodeTypeForm, NodePropertyFormSet,
                           RelationshipTypeForm, RelationshipTypeFormSet,
                           TypeDeleteForm, TypeDeleteConfirmForm,
                           ON_DELETE_NOTHING, ON_DELETE_CASCADE,
                           SchemaImportForm)
from schemas.models import NodeType, RelationshipType


@permission_required("data.view_data",
                     (Graph, "slug", "graph_slug"))
def operator_query(request, graph_slug):
    graph = get_object_or_404(Graph, slug=graph_slug)
    nodetypes = NodeType.objects.filter(schema__graph__slug=graph_slug)
    reltypes = RelationshipType.objects.filter(schema__graph__slug=graph_slug)
    return render_to_response('operator_query.html',
                              {"graph": graph,
                               "node_types": nodetypes,
                               "relationship_types": reltypes},
                              context_instance=RequestContext(request))
