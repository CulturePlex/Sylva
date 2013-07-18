# -*- coding: utf-8 -*-
from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from graphs.models import Graph

# Globally disable default 'delete selected'
admin.site.disable_action('delete_selected')


def delete_graph(modeladmin, request, queryset):
    for graph in queryset:
        graph.relationships.delete()
        graph.nodes.delete()
        graph.delete()
delete_graph.short_description = "Delete selected graphs and related elements"


class GraphAdmin(GuardedModelAdmin):
    user_owned_objects_field = "owner"
    actions = [delete_graph]

admin.site.register(Graph, GraphAdmin)
