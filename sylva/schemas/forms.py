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

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop("schema", None)
        super(RelationshipTypeForm, self).__init__(*args, **kwargs)
        if schema:
            nodetypes =  schema.nodetype_set.all()
            self.fields["source"].queryset = nodetypes
            self.fields["target"].queryset = nodetypes

    class Meta:
        model = RelationshipType
        fields = ("source", "name", "inverse", "target", "description",
                  "arity", "inheritance")


RelationshipTypeFormSet = inlineformset_factory(RelationshipType,
                                                RelationshipProperty,
                                                extra=1, can_delete=True)


class ItemTypeForm(forms.Form):

    def __init__(self, itemtype, *args, **kwargs):
        super(ItemTypeForm, self).__init__(*args, **kwargs)
        # Relationship properties
        # Node properties
        for node_property in itemtype.properties.all():
            datatype_dict = node_property.get_datatype_dict()
            label = node_property.key
            # TODO: Fix the required value rendering
            if node_property.required:
                label = "%s *" % label
            field_attrs = {
                "required": node_property.required,
                "initial": node_property.default,
                "label": label,
                "help_text": node_property.description,
            }
            if node_property.datatype == datatype_dict["date"]:
                field = forms.DateTimeField(**field_attrs)
            elif node_property.datatype == datatype_dict["boolean"]:
                field = forms.BooleanField(**field_attrs)
            elif node_property.datatype == datatype_dict["number"]:
                field = forms.FloatField(**field_attrs)
            else:
                field = forms.CharField(**field_attrs)
            self.fields[node_property.key] = field



#def get_form_for_nodetype(nodetype, gdb=False):
#    fields = {}
#    # Slug creation
#    field_attrs = {
#        "required": True,
#        "label": u"* %s:" % _(u"Slug"),
#        "help_text": _(u"The slug field allows to index que node for searching"),
#    }
#    fields["_slug"] = forms.CharField(**field_attrs)
#    # Node properties
#    for node_property in nodetype.nodeproperty_set.all():
#        datatype_dict = node_property.get_datatype_dict()
#        label = node_property.key.replace("-", " ").replace("_", " ")
#        label = "%s:" % label.capitalize()
#        # TODO: Fix the required value rendering
#        if node_property.required:
#            label = "* %s" % label
#        field_attrs = {
#            "required": node_property.required,
#            "initial": node_property.default,
#            "label": label,
#            "help_text": node_property.description,
#        }
#        if node_property.datatype == datatype_dict["date"]:
#            field = forms.DateTimeField(**field_attrs)
#        elif node_property.datatype == datatype_dict["boolean"]:
#            field = forms.BooleanField(**field_attrs)
#        elif node_property.datatype == datatype_dict["number"]:
#            field = forms.FloatField(**field_attrs)
#        else:
#            field = forms.CharField(**field_attrs)
#        fields[node_property.key] = field
#    # Relationships
#    # TODO: Use formsets to be able to add properties to the relationships
#    if gdb:
#        for relationship in nodetype.get_edges():
#            graph_id = nodetype.graph.id
#            idx = gdb.nodes.indexes.get('sylva_nodes')
#            results = idx.get("_type")[relationship.node_to.name]
#            # TODO: The indexable properties must be string or
#            #       unicode, why? :\
#            choices = [(n.id, n.properties.get("_slug")) for n in results
#                       if n.properties["_graph"] == unicode(graph_id)]
#            label = relationship.relation.name.replace("-", " ") \
#                    .replace("_", " ")
#            label = "%s:" % label.capitalize()
#            # TODO: Fix the required value rendering
#            # if relationship.required:
#            #    label = "* %s" % label
#            if relationship.arity > 0:
#                help_text = _(u"Check %s elements at most." \
#                              % relationship.arity)
#            else:
#                help_text = _(u"Check any number of elements.")
#            field = forms.MultipleChoiceField(choices=choices, required=False,
#                                              help_text=help_text, label=label)
#            fields[relationship.relation.name] = field

#    def clean_form(self):
#        cleaned_data = self.cleaned_data
#        for relationship in nodetype.get_edges():
#            rel_name = relationship.relation.name
#            if rel_name in self.data and relationship.arity > 0:
#                if len(self.data.getlist(rel_name)) > relationship.arity:
#                    msg = _("Only %s elements at most") % relationship.arity
#                    self._errors[rel_name] = msg
#                    del cleaned_data[rel_name]
#        return cleaned_data
#    fields["clean"] = clean_form

#    def save_form(self, *args, **kwargs):
#        properties = get_internal_attributes(self.data["_slug"], nodetype.name,
#                                             nodetype.graph.id, "", False)
#        node_properties = nodetype.nodeproperty_set.all().values("key")
#        keys = [p["key"] for p in node_properties]
#        for key in keys:
#            if key in self.data and len(self.data[key]) > 0:
#                properties[key] = self.data[key]
#        properties["_slug"] = self.data["_slug"]

