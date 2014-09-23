# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Query


class QueryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Query, QueryAdmin)
