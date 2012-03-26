# -*- coding: utf-8 -*-
from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from graphs.models import Graph


class GraphAdmin(GuardedModelAdmin):
    user_owned_objects_field = "owner"

admin.site.register(Graph, GraphAdmin)
