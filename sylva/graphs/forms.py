# -*- coding: utf-8 -*-
from django.forms import ModelForm

from graphs.models import Graph


class GraphForm(ModelForm):

    class Meta:
        model = Graph
        fields = ("name", "description", "owner")
