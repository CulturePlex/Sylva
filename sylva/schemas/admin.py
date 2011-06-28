# -*- coding: utf-8 -*-
from django.contrib import admin

from schemas.models import (Schema, NodeType, RelationshipType, NodeProperty,
                            RelationshipProperty)


admin.site.register(Schema)
admin.site.register(NodeType)
admin.site.register(RelationshipType)
admin.site.register(NodeProperty)
admin.site.register(RelationshipProperty)
