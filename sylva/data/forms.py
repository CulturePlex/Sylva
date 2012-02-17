# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import BaseFormSet, DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from data.models import MediaNode, MediaFile, MediaLink
from schemas.models import RelationshipType

ITEM_FIELD_NAME = "_ITEM_ID"


class ItemForm(forms.Form):

    def __init__(self, itemtype, *args, **kwargs):
        super(ItemForm, self).__init__(label_suffix="", *args, **kwargs)
        self.populate_fields(itemtype, initial=kwargs.get("initial", None))
        self.graph = itemtype.schema.graph
        self.item_id = None
        self.delete = None
        self.itemtype = itemtype
        self.itemtype_properties = [prop["key"] for prop
                                    in itemtype.properties.all().values("key")
                                    if itemtype.name != prop["key"]]

    def populate_fields(self, itemtype, initial=None):
        self.populate_node_properties(itemtype, initial=initial)

    def populate_node_properties(self, itemtype, initial=None):
        # Node properties
        for item_property in itemtype.properties.all().order_by("order"):
            datatype_dict = item_property.get_datatype_dict()
            label = item_property.key
            # TODO: Fix the required value rendering
            if item_property.required:
                label = "%s *" % label
            if initial:
                initial_value = initial.get(label, item_property.default)
            else:
                initial_value = item_property.default
            field_attrs = {
                "required": item_property.required,
                "initial": initial_value,
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
        if initial and ITEM_FIELD_NAME in initial:
            self.item_id = initial[ITEM_FIELD_NAME]
            field_attrs = {
                "required": True,
                "initial": self.item_id,
                "label": "",
                "widget": forms.HiddenInput(),
            }
            field = forms.CharField(**field_attrs)
            self.fields[ITEM_FIELD_NAME] = field


    def _clean_fields(self):
        # Taken from django/forms/forms.py
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = field.widget.value_from_datadict(self.data, self.files,
                                                     self.add_prefix(name))
            try:
                if isinstance(field, forms.fields.FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except UnicodeError, e:
                # Here it is the difference: we need to sluggify the field name
                slug_name = slugify(name)
                if hasattr(self, 'clean_%s' % slug_name):
                    value = getattr(self, 'clean_%s' % slug_name)()
                    self.cleaned_data[name] = value
            except ValidationError, e:
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]

    def clean(self):
        cleaned_data = super(ItemForm, self).clean()
        not_false_values = [bool(unicode(v).strip())
                            for v in cleaned_data.values()]
        if DELETION_FIELD_NAME in cleaned_data:
            self.delete = cleaned_data.pop(DELETION_FIELD_NAME)
        if ITEM_FIELD_NAME in cleaned_data:
            self.item_id = cleaned_data.pop(ITEM_FIELD_NAME)
        if (len(cleaned_data) <= 0 or
            not any(not_false_values)):
            msg = _("At least one field must be filled")
            for field_key, field_value in cleaned_data.items():
                if not field_value.strip():
                    self._errors[field_key] = self.error_class([msg])
                    del cleaned_data[field_key]
        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        properties = self.cleaned_data
        if (properties
            and any([bool(unicode(v).strip()) for v in properties.values()])):
            if self.graph.relaxed:
                properties_items = properties.items()
                for field_key, field_value in properties_items:
                    if field_key not in self.itemtype_properties:
                        properties.pop(field_key)
            # Assign to label the value of the identifier of the NodeType
            label = unicode(self.itemtype.id)
            if commit:
                if self.item_id:
                    if self.delete:
                        return self.graph.nodes.delete(id=self.item_id)
                    else:
                        node = self.graph.nodes.get(self.item_id)
                        node.properties = properties
                    return node
                else:
                    return self.graph.nodes.create(label=label,
                                                   properties=properties)
            else:
                return (label, properties)


class NodeForm(ItemForm):
    pass


class RelationshipForm(ItemForm):

    def populate_fields(self, itemtype, initial=None):
        self.populate_relationship_properties(itemtype, initial=initial)
        self.populate_node_properties(itemtype, initial=initial)

    def populate_relationship_properties(self, itemtype, initial=None):
        # Relationship properties
        if isinstance(itemtype, RelationshipType):
            choices = [(n.id, n.display) for n in itemtype.target.all()]
            field_attrs = {
                "required": True,
                "initial": "",
                "label": itemtype.name,
                "help_text": _("Choose the target of the relationship"),
                "choices": [(u"", u"---------")] + choices,
                "widget": forms.Select(attrs={
                    "class": "autocomplete"
                }),
            }
            field = forms.ChoiceField(**field_attrs)
            self.fields[itemtype.name] = field

    def clean(self):
        cleaned_data = super(RelationshipForm, self).clean()
        if self.itemtype.name in cleaned_data:
            target_node_id = cleaned_data[self.itemtype.name]
            self.target_node = self.graph.nodes.get(target_node_id)
            if self.target_node.label != unicode(self.itemtype.target.id):
                msg = _("The target must be %s" % self.itemtype.target.name)
                self._errors[self.itemtype.name] = self.error_class([msg])
                del cleaned_data[self.itemtype.name]
        else:
            msg = _("The target must be %s" % self.itemtype.target.name)
            self._errors[self.itemtype.name] = self.error_class([msg])
        return cleaned_data

    def save(self, source_node=None, commit=True, *args, **kwargs):
        properties = self.cleaned_data
        if (properties
            and any([bool(unicode(v).strip()) for v in properties.values()])):
            target_node_id = properties.pop(self.itemtype.name)
            if not self.graph.relaxed:
                properties_items = properties.items()
                for field_key, field_value in properties_items:
                    if (field_key not in self.itemtype_properties):
                        properties.pop(field_key)
            label = unicode(self.itemtype.id)
            if commit and (self.item_id or source_node):
                if self.item_id:
                    if self.delete:
                        return self.graph.relationships.delete(id=self.item_id)
                    else:
                        rel = self.graph.relationships.get(self.item_id)
                        rel.properties = properties
                        rel.target = self.target_node
                        return rel
                else:
                    return self.graph.relationships.create(source_node.id,
                                                           target_node_id,
                                                           label=label,
                                                       properties=properties)
            else:
                return (source_node.id, target_node_id, label, properties)


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
