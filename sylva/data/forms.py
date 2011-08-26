# -*- coding: utf-8 -*-
from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext as _

from data.models import MediaNode, MediaFile, MediaLink
from schemas.models import RelationshipType


class ItemForm(forms.Form):

    def __init__(self, itemtype, *args, **kwargs):
        super(ItemForm, self).__init__(label_suffix="", *args, **kwargs)
        self.populate_fields(itemtype, initial=kwargs.get("initial", None))

    def populate_fields(self, itemtype, initial=None):
        self.populate_node_properties(itemtype, initial=initial)

    def populate_node_properties(self, itemtype, initial=None):
        # Node properties
        for item_property in itemtype.properties.all():
            datatype_dict = item_property.get_datatype_dict()
            label = item_property.key
            # TODO: Fix the required value rendering
            if item_property.required:
                label = "%s *" % label
            field_attrs = {
                "required": item_property.required,
                "initial": item_property.default,
                "label": label,
                "help_text": item_property.description,
            }
            if item_property.datatype == datatype_dict["date"]:
                field = forms.DateTimeField(**field_attrs)
            elif item_property.datatype == datatype_dict["boolean"]:
                field = forms.BooleanField(**field_attrs)
            elif item_property.datatype == datatype_dict["number"]:
                field = forms.FloatField(**field_attrs)
            else:
                field = forms.CharField(**field_attrs)
            self.fields[item_property.key] = field


class NodeForm(ItemForm):
    pass


class RelationshipForm(ItemForm):

    def populate_fields(self, itemtype, initial=None):
        self.populate_relationship_properties(itemtype, initial=initial)
        self.populate_node_properties(itemtype, initial=initial)

    def populate_relationship_properties(self, itemtype, initial=None):
        # Relationship properties
        if isinstance(itemtype, RelationshipType):
            field_attrs = {
                "required": True,
                "initial": "",
                "label": itemtype.name,
                "help_text": _("Choose the target of the relationship"),
                "choices": [(n.id, n.display)
                            for n in itemtype.target.all()],
            }
            field = forms.ChoiceField(**field_attrs)
            # Is needed to sluggify this?
            # from django.template import defaultfilters
            # defaultfilters.sluggify
            self.fields[itemtype.name] = field


def relationship_formset_factory(relationship, *args, **kwargs):
    pass


class TypeBaseFormSet(BaseFormSet):

    def __init__(self, itemtype, *args, **kwargs):
        self.itemtype = itemtype
        super(TypeBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
        if self.is_bound:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        # This is the only line distinct to original implementation from django
        form = self.form(self.itemtype, **defaults)
        self.add_fields(form, i)
        return form


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


class MediaNodeForm(forms.ModelForm):

    class Meta:
        model = MediaNode

MediaFileFormSet = inlineformset_factory(MediaNode, MediaFile,
                                         extra=1, can_delete=True)

MediaLinkFormSet = inlineformset_factory(MediaNode, MediaLink,
                                         extra=1, can_delete=True)
