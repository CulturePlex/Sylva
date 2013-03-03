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
    option = forms.ChoiceField(label=_("We found some elements of this type."
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
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete "
                                        "this?"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class NodeTypeForm(forms.ModelForm):

    def clean_name(self):
        name = self.cleaned_data["name"]
        if name.strip() == "":
            raise forms.ValidationError(_("You need to provide a name."))
        return name

    class Meta:
        model = NodeType
        if settings.OPTIONS["ENABLE_INHERITANCE"]:
            exclude = ("schema", "order", "total")
        else:
            exclude = ("schema", "order", "total", "inheritance")
        if not settings.OPTIONS.get("ENABLE_TYPE_VALIDATION_FORMS", False):
            exclude += ("validation", )

if settings.OPTIONS.get("ENABLE_TYPE_VALIDATION_FORMS", False):
    NodePropertyFormSet = inlineformset_factory(NodeType, NodeProperty,
                                                extra=1, can_delete=True)
else:
    NodePropertyFormSet = inlineformset_factory(NodeType, NodeProperty,
                                                extra=1, can_delete=True,
                                                exclude=["validation"])


class ElementTypeChangedForm(forms.Form):

    option = forms.ChoiceField(label=_("You have renamed this property in the "
                                       "schema, but we have not modified the "
                                       "related elements yet. What do you want "
                                       "to do with them?"),
                               required=True,
                               widget=forms.RadioSelect())
    key = forms.CharField(widget=forms.HiddenInput())
    new_key = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ElementTypeChangedForm, self).__init__(*args, **kwargs)
        self.fields['option'].choices = (
            ("rename", _("Rename this property in all related elements using "
                         "the new property name: \"%s\"")
                       % self.initial.get('new_key')),
            ("keep", _("Keep this property name in all related elements, but "
                       "don't show it, and start using the new property name "
                       "for the new elements")),
        )
        self.fields['option'].initial = "keep"


class ElementTypeDeletedForm(forms.Form):

    CHOICES = (
        ("delete", _("Delete this property in all related elements")),
        ("keep", _("Keep this property in all related elements, but don't show "
                   "it")),
    )

    option = forms.ChoiceField(label=_("You have deleted this property in the "
                                       "schema, but we have not modified the "
                                       "related elements yet. What do you want "
                                       "to do with them?"),
                               choices=CHOICES,
                               required=True,
                               widget=forms.RadioSelect())
    key = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ElementTypeDeletedForm, self).__init__(*args, **kwargs)
        self.fields['option'].initial = "keep"


class RelationshipTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop("schema", None)
        super(RelationshipTypeForm, self).__init__(*args, **kwargs)
        if schema:
            nodetypes_qs = schema.nodetype_set.all()
            self.fields["source"].queryset = nodetypes_qs
            self.fields["target"].queryset = nodetypes_qs

    def clean_name(self):
        name = self.cleaned_data["name"]
        if name.strip() == "":
            raise forms.ValidationError(_("You need to provide a name."))
        return name

    class Meta:
        model = RelationshipType
        if settings.OPTIONS["ENABLE_INHERITANCE"]:
            fields = ("source", "name", "plural_name", "inverse",
                      "plural_inverse", "target", "description",
                      "arity_source", "arity_target",
                      "inheritance")
        else:
            fields = ("source", "name", "plural_name", "inverse",
                      "plural_inverse", "target", "description",
                      "arity_source", "arity_target")
        if settings.OPTIONS.get("ENABLE_TYPE_VALIDATION_FORMS", False):
            fields += ("validation", )

if settings.OPTIONS.get("ENABLE_TYPE_VALIDATION_FORMS", False):
    RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                    RelationshipProperty,
                                                    extra=1, can_delete=True)
else:
    RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                    RelationshipProperty,
                                                    extra=1, can_delete=True,
                                                    exclude=["validation"])


class SchemaImportForm(forms.Form):
    file = forms.FileField(help_text=_("Choose a JSON file previously exported"))
