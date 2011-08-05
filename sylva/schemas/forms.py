# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.models import inlineformset_factory
from django.template import defaultfilters
from django.utils.translation import gettext as _

from schemas.models import (NodeType, NodeProperty,
                            RelationshipType, RelationshipProperty)


class NodeTypeForm(forms.ModelForm):

    class Meta:
        model = NodeType
        exclude = ("schema", "order")

NodePropertyFormSet = inlineformset_factory(NodeType, NodeProperty,
                                            extra=1, can_delete=True)


class RelationshipTypeForm(forms.ModelForm):

    class Meta:
        model = RelationshipType
        fields = ("source", "name", "inverse", "target", "description",
                  "arity", "inheritance")


RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                RelationshipProperty,
                                                extra=1, can_delete=True)

