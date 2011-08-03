# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.template import defaultfilters
from django.utils.translation import gettext as _

from schemas.models import (NodeType, NodeProperty,
                            RelationshipType, RelationshipProperty)

class NodeTypeForm(forms.ModelForm):

    class Meta:
        model = NodeType
        exclude = ("schema", )


class RelationshipTypeForm(forms.ModelForm):

    class Meta:
        model = RelationshipType


class NodePropertyForm(forms.ModelForm):

    class Meta:
        model = NodeProperty
        exclude = ("order", "node", "value")

    def save(self, *args, **kwargs):
        self.instance.node = self.initial["node"]
        super(NodePropertyForm, self).save(*args, **kwargs)

    def clean_key(self):
        return defaultfilters.slugify(self.cleaned_data["key"])


class RelationshipPropertyForm(forms.ModelForm):

    class Meta:
        model = RelationshipProperty
        exclude = ("order", "edge", "value")

    def save(self, *args, **kwargs):
        self.instance.edge = self.initial["edge"]
        super(RelationshipPropertyForm, self).save(*args, **kwargs)

    def clean_key(self):
        return defaultfilters.slugify(self.cleaned_data["key"])


class ValidRelationForm(forms.ModelForm):
    relation = forms.CharField(help_text=_("Relation name, like 'Knows' or 'Writes'"))

    class Meta:
        model = RelationshipType
        exclude = ("node_from", "graph", "relation")

    def __init__(self, *args, **kwargs):
        graph = kwargs['initial']['graph']
        super(ValidRelationForm, self).__init__(*args, **kwargs)
        self.fields['node_to'].queryset = \
            graph.nodetype_set.all()

    def clean(self):
        cleaned_data = self.cleaned_data
        edge_type_slug = defaultfilters.slugify(self.data["relation"])
        try:
            self.instance.relation.name = edge_type_slug
            self.instance.relation.save()
            cleaned_data["relation"] = self.instance.relation
        except ObjectDoesNotExist:
            edges = RelationshipType.objects.filter(name__iexact=edge_type_slug)
            if edges:
                cleaned_data["relation"] = edges[0]
            else:
                edge = RelationshipType.objects.create(name=edge_type_slug,
                                               graph=self.initial["graph"])
                cleaned_data["relation"] = edge
        self.initial["relation"] = cleaned_data["relation"]
        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.node_from = self.initial["node_from"]
        self.instance.relation = self.initial["relation"]
        self.instance.graph = self.initial["graph"]
        super(ValidRelationForm, self).save(*args, **kwargs)
