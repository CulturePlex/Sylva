# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory

from schemas.models import (NodeType, NodeProperty,
                            RelationshipType, RelationshipProperty)


class NodeTypeForm(forms.ModelForm):

    class Meta:
        model = NodeType
        exclude = ("schema", "order")

NodePropertyFormSet = inlineformset_factory(NodeType, NodeProperty,
                                            extra=1, can_delete=True)


class RelationshipTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop("schema", None)
        super(RelationshipTypeForm, self).__init__(*args, **kwargs)
        if schema:
            nodetypes_qs = schema.nodetype_set.all()
            self.fields["source"].queryset = nodetypes_qs
            self.fields["target"].queryset = nodetypes_qs

    class Meta:
        model = RelationshipType
        fields = ("source", "name", "plural_name", "inverse", "plural_inverse",
                  "target", "description", "arity", "inheritance")


RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                RelationshipProperty,
                                                extra=1, can_delete=True)
