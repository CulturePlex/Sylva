# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext as _

from schemas.models import (NodeType, NodeProperty,
                            RelationshipType, RelationshipProperty)


ON_DELETE_NOTHING = "no"
ON_DELETE_CASCADE = "de"

class TypeDeleteForm(forms.Form):
    CHOICES = (
        (ON_DELETE_NOTHING, _("Nothing, let them as they are")),
        (ON_DELETE_CASCADE, _("Delete all related elements")),
    )
    option = forms.ChoiceField(label=_("We found some elements of this type." \
                                       " What do you want to do with them?"),
                               choices=CHOICES, required=True,
                               widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        count = kwargs.pop("count", None)
        super(TypeDeleteForm, self).__init__(*args, **kwargs)
        if count > 0:
            if count == 1:
                choice = (
                    ON_DELETE_CASCADE,
                    _("Delete %s related element" % count)
                )
            else:
                choice = (
                        ON_DELETE_CASCADE,
                        _("Delete %s related elements" % count)
                    )
            self.fields["option"].choices[1] = choice


class TypeDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete " \
                                        "this?"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class NodeTypeForm(forms.ModelForm):

    class Meta:
        model = NodeType
        if settings.OPTIONS["ALLOWS_INHERITANCE"]:
            exclude = ("schema", "order")
        else:
            exclude = ("schema", "order", "inheritance")

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
        if settings.OPTIONS["ALLOWS_INHERITANCE"]:
            fields = ("source", "name", "plural_name", "inverse",
                      "plural_inverse", "target", "description", "arity",
                      "inheritance")
        else:
            fields = ("source", "name", "plural_name", "inverse",
                      "plural_inverse", "target", "description", "arity")

RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                RelationshipProperty,
                                                extra=1, can_delete=True)
