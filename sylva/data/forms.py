# -*- coding: utf-8 -*-
import datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
# from django.core.urlresolvers import reverse
# from django.forms.extras import widgets
from django.forms.formsets import BaseFormSet, DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from leaflet.forms.widgets import LeafletWidget
import geojson

from data.models import MediaNode, MediaFile, MediaLink
from schemas.models import NodeType
from schemas.models import RelationshipType

ITEM_FIELD_NAME = "_ITEM_ID"
NULL_OPTION = u"---------"
SOURCE = u"source"
TARGET = u"target"


class ItemDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete "
                                        "this? All related relationships "
                                        "will be removed"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class ItemForm(forms.Form):

    # Here isn't jQueryUI because it is needed to be added manually depending
    # of the template.
    class Media:
        js = (
            "js/jqueryui.timepicker.js",
            "js/datatypes.js",
            "js/jquery.formsets.1.2.min.js",
            "js/jquery.tokeninput.js",
            "js/chosen.jquery.min.js",
        )
        css = {
            "all": ("css/jqueryui.1.8.18.css", "css/chosen.css")
        }

    def __init__(self, graph, itemtype, instance=None, *args, **kwargs):
        self.username = kwargs.pop('user')
        self.graph = graph
        # Only for relationships
        self.related_node = kwargs.pop("related_node", None)
        self.direction = kwargs.pop("direction", SOURCE)
        super(ItemForm, self).__init__(label_suffix="", *args, **kwargs)
        self.populate_fields(graph, itemtype, instance=instance,
                             initial=kwargs.get("initial", None))
        self.item_id = None
        self.delete = None
        self.instance = instance
        self.itemtype = itemtype
        self.itemtype_properties = [prop["key"] for prop
                                    in itemtype.properties.all().values("key")
                                    if itemtype.id != prop["key"]]

    def populate_fields(self, graph, itemtype, instance=None, initial=None):
        self.populate_node_properties(graph, itemtype, initial=initial)

    def populate_node_properties(self, graph, itemtype, initial=None):
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
            auto_increment_update = datatype_dict["auto_increment_update"]
            field = None
            if item_property.datatype == datatype_dict["date"]:
                widget = forms.TextInput(attrs={"class": "date"})
                field_attrs["widget"] = widget
                field = forms.DateField(**field_attrs)
            elif item_property.datatype == datatype_dict["time"]:
                widget = forms.TextInput(attrs={"class": "time"})
                field_attrs["widget"] = widget
                field = forms.TimeField(**field_attrs)
            elif item_property.datatype == datatype_dict["boolean"]:
                field = forms.BooleanField(**field_attrs)
            elif item_property.datatype == datatype_dict["number"]:
                field = forms.IntegerField(**field_attrs)
            elif item_property.datatype == datatype_dict["float"]:
                field = forms.FloatField(**field_attrs)
            elif item_property.datatype == datatype_dict["choices"]:
                field_attrs["choices"] = item_property.get_choices()
                field_attrs["initial"] = slugify(field_attrs["initial"] or "")
                if initial and item_property.key in initial:
                    slug_value = slugify(initial[item_property.key])
                    initial[item_property.key] = slug_value
                field = forms.ChoiceField(**field_attrs)
            elif item_property.datatype == datatype_dict["text"]:
                field_attrs["widget"] = widget = forms.Textarea
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == datatype_dict["auto_user"]:
                field_attrs["initial"] = self.username
                widget = forms.TextInput(attrs={"readonly": "readonly"})
                field_attrs["widget"] = widget
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == datatype_dict["auto_now"]:
                if not initial:
                    field_attrs["initial"] = datetime.datetime.today()
                else:
                    field_attrs["initial"] = item_property.value
                widget = forms.TextInput(attrs={"readonly": "readonly"})
                field_attrs["widget"] = widget
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == datatype_dict["auto_now_add"]:
                if not initial:
                    field_attrs["initial"] = datetime.datetime.today()
                else:
                    field_attrs["initial"] = item_property.value
                widget = forms.TextInput(attrs={"readonly": "readonly"})
                field_attrs["widget"] = widget
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == datatype_dict["auto_increment"]:
                if not item_property.auto:
                    field_attrs["initial"] = 0
                else:
                    field_attrs["initial"] = item_property.auto
                widget = forms.TextInput(attrs={"readonly": "readonly"})
                field_attrs["widget"] = widget
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == auto_increment_update:
                if not item_property.default:
                    field_attrs["initial"] = '0'
                widget = forms.TextInput(attrs={"readonly": "readonly"})
                field_attrs["widget"] = widget
                field = forms.CharField(**field_attrs)
            elif item_property.datatype == datatype_dict["collaborator"]:
                if settings.ENABLE_AUTOCOMPLETE_COLLABORATORS:
                    if initial and item_property.key in initial:
                        slug_value = slugify(initial[item_property.key])
                        initial[item_property.key] = slug_value
                        username = slug_value
                        widget_class = u"user_autocomplete %s" % username
                    else:
                        widget_class = u"user_autocomplete"
                    widget = forms.TextInput(
                        attrs={
                            "class": widget_class,
                        })
                    field_attrs["widget"] = widget
                    field_attrs["initial"] = ""
                    field = forms.CharField(**field_attrs)
                else:
                    collaborators = [(u'', NULL_OPTION)]
                    owner = graph.owner.username
                    collaborators.append((owner, owner))
                    collaborators.extend(
                        [(collaborator.username, collaborator.username)
                            for collaborator
                            in graph.get_collaborators()])
                    collaborators.sort()
                    field_attrs["choices"] = collaborators
                    field_attrs["initial"] = slugify(field_attrs["initial"]
                                                     or "")
                    if initial and item_property.key in initial:
                        slug_value = slugify(initial[item_property.key])
                        initial[item_property.key] = slug_value
                    field = forms.ChoiceField(**field_attrs)
            elif settings.ENABLE_SPATIAL and isinstance(itemtype, NodeType):
                if item_property.datatype == datatype_dict["point"]:
                    widget = LeafletPointWidget()
                    field_attrs["widget"] = widget
                    field = forms.CharField(**field_attrs)
                elif item_property.datatype == datatype_dict["path"]:
                    widget = LeafletPathWidget()
                    field_attrs["widget"] = widget
                    field = forms.CharField(**field_attrs)
                elif item_property.datatype == datatype_dict["area"]:
                    widget = LeafletAreaWidget()
                    field_attrs["widget"] = widget
                    field = forms.CharField(**field_attrs)
            if not field:
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
                # Here it is the difference: we need to slugify the field name
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
        # Extra check for choices fields
        choices_properties = self.itemtype.properties.filter(datatype="c")
        for choice_property in choices_properties:
            choice_dict = dict(choice_property.get_choices())
            key = choice_property.key
            if key in cleaned_data:
                value = choice_dict[cleaned_data[key]].strip()
                if value == NULL_OPTION:
                    # cleaned_data[key] = None
                    cleaned_data.pop(key)
                else:
                    cleaned_data[key] = value
            elif choice_property.required:
                msg = _("This field is required and "
                        "must have some value selected.")
                self._errors[key] = self.error_class([msg])
            else:
                cleaned_data[key] = u""
        # Extra check for spatial fields
        spatial_properties = self.itemtype.properties.filter(
            datatype__in=["p", "l", "m"])
        for spatial_property in spatial_properties:
            key = spatial_property.key
            if key in cleaned_data and cleaned_data[key]:
                try:
                    field = geojson.loads(cleaned_data[key])
                except ValueError:
                    msg = _("This field is required to "
                            "be in a valid JSON format.")
                    self._errors[key] = self.error_class([msg])
                else:
                    validity = geojson.is_valid(field)
                    is_not_valid = validity['valid'] == 'no'
                    if is_not_valid and spatial_property.datatype == u'p':
                        msg = _("This field is required to "
                                "be a valid GeoJSON point.")
                    elif is_not_valid and spatial_property.datatype == u'l':
                        msg = _("This field is required to "
                                "be a valid GeoJSON path.")
                    elif is_not_valid and spatial_property.datatype == u'm':
                        msg = _("This field is required to "
                                "be a valid GeoJSON area.")
                    elif is_not_valid:
                        msg = _("This field is required to "
                                "be a valid GeoJSON.")
                    if is_not_valid:
                        self._errors[key] = self.error_class([msg])
            else:
                cleaned_data[key] = u""
        return cleaned_data

    def save(self, commit=True, as_new=False, *args, **kwargs):
        properties = self.cleaned_data
        if (properties and any([bool(unicode(v).strip())
                                for v in properties.values()])):
            if self.graph.relaxed:
                properties_items = properties.items()
                for field_key, field_value in properties_items:
                    if field_key not in self.itemtype_properties:
                        properties.pop(field_key)
            # Assign to label the value of the identifier of the NodeType
            label = unicode(self.itemtype.id)
            properties = self._set_now_attributes(properties)
            properties = self._auto_increment_update(properties)
            if commit:
                if self.item_id and not as_new:
                    if self.delete:
                        '''
                        It will never pass by here because the nodes are not
                        deleted with the save method
                        '''
                        return self.graph.nodes.delete(id=self.item_id)
                    else:
                        node = self.graph.nodes.get(self.item_id)
                        node.properties = properties
                    return node
                else:
                    properties = self._auto_increment(properties)
                    return self.graph.nodes.create(label=label,
                                                   properties=properties)
            else:
                return (label, properties)

    def _set_now_attributes(self, properties):
        if self.item_id is None:
            for prop in self.itemtype.properties.filter(datatype="a"):
                properties[prop.key] = datetime.datetime.today()
        for prop in self.itemtype.properties.filter(datatype="w"):
            properties[prop.key] = datetime.datetime.today()
        return properties

    def _auto_increment_update(self, properties):
        for prop in self.itemtype.properties.filter(datatype="o"):
            number = int(properties[prop.key]) + 1
            properties[prop.key] = '{}'.format(number)
        return properties

    def _auto_increment(self, properties):
        for prop in self.itemtype.properties.filter(datatype="i"):
            if not prop.auto:
                prop.auto = 0
                number = prop.auto + 1
                prop.auto = number
                prop.save()
                properties[prop.key] = number
            else:
                number = prop.auto + 1
                prop.auto = number
                prop.save()
                properties[prop.key] = number
        return properties


class NodeForm(ItemForm):
    pass


class RelationshipForm(ItemForm):

    def populate_fields(self, graph, itemtype, instance=None, initial=None):
        self.populate_relationship_properties(
            graph, itemtype, instance=instance, initial=initial)
        self.populate_node_properties(graph, itemtype, initial=initial)

    def populate_relationship_properties(self, graph, itemtype, instance=None,
                                         initial=None):
        # Relationship properties
        if isinstance(itemtype, RelationshipType):
            direction = self.direction
            if direction == TARGET:
                label = u"→ %s (%s)" % (itemtype.name,
                        getattr(itemtype, direction).name)
                if not settings.ENABLE_AUTOCOMPLETE_NODES:
                    choices = [(n.id, n.display)
                               for n in itemtype.target.all()]
                # url_create = reverse("nodes_create",
                #                      args=[itemtype.schema.graph.slug,
                #                            itemtype.target.id])
            else:
                label = u"← (%s) %s" % (getattr(itemtype, direction).name,
                        itemtype.inverse or itemtype.name)
                if not settings.ENABLE_AUTOCOMPLETE_NODES:
                    choices = [(n.id, n.display)
                               for n in itemtype.source.all()]
                # url_create = reverse("nodes_create",
                #                      args=[itemtype.schema.graph.slug,
                #                            itemtype.source.id])
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
            if settings.ENABLE_AUTOCOMPLETE_NODES:
                data_name = "-".join([self.prefix, str(itemtype.id)])
                node = None
                if initial and itemtype.id in initial:  # Saved data
                    node = graph.nodes.get(initial.get(
                        itemtype.id))
                elif data_name in self.data:  # New data from the form
                    '''
                    This is a special case. It is used when you introduce a new
                    relationship and the form have validation errors. So, we
                    don't have a `initial` object with "original" data, but we
                    DO have new data to show in the form with errors.
                    '''
                    node_id = self.data[data_name]
                    if node_id.isdecimal():
                        node_id = int(node_id)
                        node = graph.nodes.get(node_id)
                if node is not None:
                    widget_class = u"node_autocomplete %s" % node.display
                else:
                    widget_class = u"node_autocomplete"
                input_attrs = {
                    "class": widget_class,
                    "data-type": getattr(itemtype, direction).id,
                }
                if self.related_node and itemtype.source == itemtype.target:
                    # If it's reflexive
                    input_attrs.update({
                        "data-exclude-id": self.related_node.id
                    })
                field_attrs = {
                    "required": True,
                    "initial": "",
                    "label": label,
                    "help_text": help_text,
                    "widget": forms.TextInput(attrs=input_attrs)
                }
                field = forms.CharField(**field_attrs)
            else:
                field_attrs = {
                    "required": True,
                    "initial": "",
                    "label": label,
                    "help_text": help_text,
                    "choices": [(u"", NULL_OPTION)] + choices,
                }
                if settings.ENABLE_AUTOCOMPLETE_NODES_COMBO:
                    input_attrs = {
                        "class": "combobox",
                        "data-placeholder": NULL_OPTION,
                    }
                    field_attrs.update({
                        "widget": forms.Select(attrs=input_attrs)
                    })
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
                msg = _("The {0} must be {1}").format(direction,
                                                      itemtype_attr.name)
                self._errors[self.itemtype.id] = self.error_class([msg])
                del cleaned_data[self.itemtype.id]
        else:
            itemtype_attr = getattr(self.itemtype, direction)
            msg = _("The {0} must be {1}").format(direction,
                                                  itemtype_attr.name)
            self._errors[self.itemtype.id] = self.error_class([msg])
        # If there is no data, there is no relationship to add
        if (self.itemtype.id in self._errors
                and not (self.initial or cleaned_data)):
            self._errors.pop(self.itemtype.id)
        return cleaned_data

    def save(self, related_node=None, as_new=False, commit=True, *args,
             **kwargs):
        related_node = related_node or self.related_node
        properties = None
        if hasattr(self, "cleaned_data"):
            properties = self.cleaned_data
        if (properties and
                any([bool(unicode(v).strip()) for v in properties.values()])):
            node_id = properties.pop(self.itemtype.id)
            if not self.graph.relaxed:
                properties_items = properties.items()
                for field_key, field_value in properties_items:
                    if (field_key not in self.itemtype_properties):
                        properties.pop(field_key)
            label = unicode(self.itemtype.id)
            properties = self._set_now_attributes(properties)
            properties = self._auto_increment_update(properties)
            if commit and (self.item_id or related_node):
                if self.item_id and not as_new:
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
                    if self.direction == TARGET:
                        # Direction →
                        properties = self._auto_increment(properties)
                        return self.graph.relationships.create(
                            related_node.id,
                            node_id,
                            label=label,
                            properties=properties
                        )
                    else:
                        # Direction ←
                        properties = self._auto_increment(properties)
                        return self.graph.relationships.create(
                            node_id,
                            related_node.id,
                            label=label,
                            properties=properties
                        )
            else:
                return (related_node.id, node_id, label, properties)


def relationship_formset_factory(relationship, *args, **kwargs):
    pass


class TypeBaseFormSet(BaseFormSet):

    def __init__(self, graph, itemtype, instance=None, related_node=None,
                 direction=SOURCE, *args, **kwargs):
        self.graph = graph
        self.itemtype = itemtype
        self.instance = instance
        self.username = kwargs.pop('user')
        self.related_node = related_node
        self.direction = direction
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
        defaults['user'] = self.username
        defaults.update(kwargs)
        # This is the only line distinct to original implementation from django
        form = self.form(
            self.graph,
            self.itemtype,
            instance=self.instance,
            related_node=self.related_node,
            direction=self.direction,
            **defaults)
        self.add_fields(form, i)
        return form


class MediaNodeForm(forms.ModelForm):

    class Meta:
        model = MediaNode

MediaFileFormSet = inlineformset_factory(MediaNode, MediaFile,
                                         extra=1, can_delete=True)

MediaLinkFormSet = inlineformset_factory(MediaNode, MediaLink,
                                         extra=1, can_delete=True)


class LeafletPointWidget(LeafletWidget):
    geometry_field_class = 'PointField'


class LeafletPathWidget(LeafletWidget):
    geometry_field_class = 'PathField'


class LeafletAreaWidget(LeafletWidget):
    geometry_field_class = 'AreaField'
