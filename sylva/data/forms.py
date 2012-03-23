# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.formsets import BaseFormSet, DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from data.models import MediaNode, MediaFile, MediaLink
from schemas.models import RelationshipType

ITEM_FIELD_NAME = "_ITEM_ID"


class ItemDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete " \
                                        "this? All related relationships " \
                                        "will be removed"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class ItemForm(forms.Form):

    def __init__(self, itemtype, instance=None, *args, **kwargs):
        super(ItemForm, self).__init__(label_suffix="", *args, **kwargs)
        self.populate_fields(itemtype, instance=instance,
                             initial=kwargs.get("initial", None))
        self.graph = itemtype.schema.graph
        self.item_id = None
        self.delete = None
        self.instance = instance
        self.itemtype = itemtype
        if hasattr(itemtype, "source"):
            if instance == itemtype.source:
                self.direction = "target"
            else:
                self.direction = "source"
        self.itemtype_properties = [prop["key"] for prop
                                    in itemtype.properties.all().values("key")
                                    if itemtype.id != prop["key"]]

    def populate_fields(self, itemtype, instance=None, initial=None):
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

    def populate_fields(self, itemtype, instance=None, initial=None):
        self.populate_relationship_properties(itemtype, instance=instance,
                                              initial=initial)
        self.populate_node_properties(itemtype, initial=initial)

    def populate_relationship_properties(self, itemtype, instance=None,
                                         initial=None):
        # Relationship properties
        if isinstance(itemtype, RelationshipType):
            if instance == itemtype.source:
                direction = u"target"
                label = u"→ %s (%s)" % (itemtype.name,
                                        getattr(itemtype, direction).name)
                if not settings.AUTOCOMPLETE_NODES:
                    choices = [(n.id, n.display)
                               for n in itemtype.target.all()]
                url_create = reverse("nodes_create",
                                     args=[itemtype.schema.graph.slug,
                                           itemtype.target.id])
            else:
                direction = u"source"
                label = u"← (%s) %s" % (getattr(itemtype, direction).name,
                                        itemtype.inverse or itemtype.name)
                if not settings.AUTOCOMPLETE_NODES:
                    choices = [(n.id, n.display)
                               for n in itemtype.source.all()]
                url_create = reverse("nodes_create",
                                     args=[itemtype.schema.graph.slug,
                                           itemtype.source.id])
            # We swap the help_text just to the properties
            #if itemtype.properties.count() == 0:
            #    help_text = _("%s of the relationship. "
            #                   "<a href=\"%s\">Add %s</a>. ") \
            #                 % (direction.capitalize(),
            #                    url_create,
            #                    getattr(itemtype, direction).name)
            #else:
            #    help_text = _("%s of the relationship. "
            #                   "<a href=\"%s\">Add %s</a>. "
            #                   "<a href=\"javascript:void(0);\""
            #                   "   class=\"toggleProperties\">"
            #                   "Toggle properties</a>.") \
            #                 % (direction.capitalize(),
            #                    url_create,
            #                    getattr(itemtype, direction).name)
            if itemtype.properties.count() == 0:
                help_text = None
            else:
                help_text = _("<a href=\"javascript:void(0);\""
                              " class=\"toggleProperties\">"
                              "Toggle properties</a>.")
            if settings.AUTOCOMPLETE_NODES:
                if initial and itemtype.id in initial:
                    node = itemtype.schema.graph.nodes.get(initial.get(itemtype.id))
                    widget_class = u"autocomplete %s" % node.display
                else:
                    node = None
                    widget_class = u"autocomplete"
                field_attrs = {
                    "required": True,
                    "initial": "",
                    "label": label,
                    "help_text": help_text,
                    "widget": forms.TextInput(attrs={
                        "class": widget_class,
                    }),
                }
                field = forms.CharField(**field_attrs)
            else:
                field_attrs = {
                    "required": True,
                    "initial": "",
                    "label": label,
                    "help_text": help_text,
                    "choices": [(u"", u"---------")] + choices,
                }
                field = forms.ChoiceField(**field_attrs)
            self.fields[itemtype.id] = field

    def clean(self):
        cleaned_data = super(RelationshipForm, self).clean()
        direction = self.direction
        if self.itemtype.id in cleaned_data:
            node_id = cleaned_data[self.itemtype.id]
            node = self.graph.nodes.get(node_id)
            node_attr = "%s_node" % direction
            setattr(self, node_attr, node)
            itemtype_id = unicode(getattr(self.itemtype, direction).id)
            if getattr(self, node_attr).label != itemtype_id:
                itemtype_attr = getattr(self.itemtype, direction)
                msg = _("The %s must be %s") \
                      % (direction, itemtype_attr.name)
                self._errors[self.itemtype.id] = self.error_class([msg])
                del cleaned_data[self.itemtype.id]
        else:
            itemtype_attr = getattr(self.itemtype, direction)
            msg = _("The %s must be %s") % (direction, itemtype_attr.name)
            self._errors[self.itemtype.id] = self.error_class([msg])
        return cleaned_data

    def save(self, related_node=None, commit=True, *args, **kwargs):
        properties = self.cleaned_data
        if (properties
            and any([bool(unicode(v).strip()) for v in properties.values()])):
            node_id = properties.pop(self.itemtype.id)
            if not self.graph.relaxed:
                properties_items = properties.items()
                for field_key, field_value in properties_items:
                    if (field_key not in self.itemtype_properties):
                        properties.pop(field_key)
            label = unicode(self.itemtype.id)
            if commit and (self.item_id or related_node):
                if self.item_id:
                    if self.delete:
                        return self.graph.relationships.delete(id=self.item_id)
                    else:
                        rel = self.graph.relationships.get(self.item_id)
                        rel.properties = properties
                        node_attr = "%s_node" % self.direction
                        self_node = getattr(self, node_attr)
                        setattr(rel, self.direction, self_node)
                        return rel
                else:
                    if self.instance == self.itemtype.source:
                        # Direction →
                        return self.graph.relationships.create(
                            related_node.id,
                            node_id,
                            label=label,
                            properties=properties
                        )
                    else:
                        # Direction ←
                        return self.graph.relationships.create(
                            node_id,
                            related_node.id,
                            label=label,
                            properties=properties
                        )
            else:
                return (source_node.id, node_id, label, properties)


def relationship_formset_factory(relationship, *args, **kwargs):
    pass


class TypeBaseFormSet(BaseFormSet):

    def __init__(self, itemtype, instance=None, *args, **kwargs):
        self.itemtype = itemtype
        self.instance = instance
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
        form = self.form(self.itemtype, instance=self.instance, **defaults)
        self.add_fields(form, i)
        return form


class MediaNodeForm(forms.ModelForm):

    class Meta:
        model = MediaNode

MediaFileFormSet = inlineformset_factory(MediaNode, MediaFile,
                                         extra=1, can_delete=True)

MediaLinkFormSet = inlineformset_factory(MediaNode, MediaLink,
                                         extra=1, can_delete=True)
