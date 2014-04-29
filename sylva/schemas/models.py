# -*- coding: utf-8 -*-
try:
    import ujson as json
except ImportError:
    import json  # NOQA

from django.db import models, transaction
from django.db.models import F, Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

from base.fields import AutoSlugField
from schemas.mixins import SchemaMixin


class Schema(models.Model, SchemaMixin):
    # graph = models.OneToOneField(Graph, verbose_name=_('graph'))
    options = models.TextField(_('options'), null=True, blank=True)

    class Meta:
        permissions = (
            ('view_schema', _('View schema')),
        )

    def __unicode__(self):
        try:
            return _(u"Schema for \"%s\"") % (self.graph.name)
        except ObjectDoesNotExist:
            return _(u"Schema \"%s\"") % (self.id)

    def is_empty(self):
        return not self.nodetype_set.exists()

    def export(self):

        def get_property_fields(n):
            return {'required': n.required,
                    'slug': n.slug,
                    'default': n.default,
                    'value': n.value,
                    'datatype': n.datatype,
                    'display': n.display,
                    'description': n.description,
                    'validation': n.validation,
                    'auto': n.auto}

        schema = {}
        schema["node_types"] = []
        for node_type in self.nodetype_set.all():
            schema["node_types"].append(node_type)
        schema["relationship_types"] = []
        for r_type in self.relationshiptype_set.all():
            schema["relationship_types"].append(r_type)
        schema_json = {"nodeTypes": {}, "allowedEdges": []}
        for node_type in schema["node_types"]:
            attributes = {}
            for n in node_type.properties.all():
                attributes[n.key] = get_property_fields(n)
            schema_json["nodeTypes"][node_type.name] = attributes
        for edge_type in schema["relationship_types"]:
            edge_attributes = {}
            for n in edge_type.properties.all():
                edge_attributes[n.key] = get_property_fields(n)
            schema_json["allowedEdges"].append({
                "source": edge_type.source.name,
                "label": edge_type.name,
                "target": edge_type.target.name,
                "properties": edge_attributes})
        return schema_json

    def get_schema_diagram(self):
        schema = {}
        for node_type in self.nodetype_set.all():
            fields = []
            relations = []
            for node_property in node_type.properties.all().select_related():
                field = {
                    "label": node_property.key,
                    #"type": node_property.get_datatype(),
                    "type": node_property.datatype,
                    "name": node_property.slug,
                    "primary": False,
                    "blank": False,
                    "choices": node_property.get_choices(),
                }
                fields.append(field)
            for rel_type in node_type.get_all_relationships().select_related():
                rel_fields = []
                for rel_property in rel_type.properties.all().select_related():
                    field = {
                        "label": rel_property.key,
                        #"type": rel_property.get_datatype(),
                        "type": rel_property.datatype,
                        "name": rel_property.slug,
                    }
                    rel_fields.append(field)
                relation = {
                    "label": rel_type.name,
                    "name": rel_type.slug,
                    "source": rel_type.source.slug,
                    "target": rel_type.target.slug,
                    "fields": rel_fields,
                    "id": rel_type.id
                }
                relations.append(relation)
            schema[node_type.slug] = {
                "name": node_type.name,
                "collapse": False,
                "primary": None,
                "is_auto": False,
                "fields": fields,
                "relations": relations,
                "id": node_type.id
            }
        slug = self.graph.slug
        diagram = {slug: schema}
        if settings.DEBUG:
            return json.dumps(diagram, indent=4)
        else:
            return json.dumps(diagram)

    def _import(self, data):
        with transaction.atomic():
            for node_type, properties in data['nodeTypes'].iteritems():
                n = NodeType(name=node_type, schema=self)
                # Saving with color
                color = n.schema.get_color()
                n.set_option('color', color)
                n.schema.save()
                n.save()
                for prop, values in properties.iteritems():
                    np = NodeProperty(key=prop, node=n)
                    for key, value in values.iteritems():
                        setattr(np, key, value)
                    np.save()
            for edge_type in data['allowedEdges']:
                source = NodeType.objects.get(schema=self,
                                              name=edge_type['source'].strip())
                target = NodeType.objects.get(schema=self,
                                              name=edge_type['target'].strip())
                rt = RelationshipType(source=source, target=target,
                                schema=self, name=edge_type['label'])
                rt.save()
                for prop, values in edge_type['properties'].iteritems():
                    rp = RelationshipProperty(key=prop, relationship=rt)
                    for key, value in values.iteritems():
                        setattr(rp, key, value)
                    rp.save()

    def _create_colors(self):
        colors = ['#F70000', '#B9264F', '#990099', '#74138C', '#0000CE',
                  '#1F88A7', '#4A9586', '#FF2626', '#D73E68', '#B300B3',
                  '#8D18AB', '#5B5BFF', '#25A0C5', '#5EAE9E', '#FF5353',
                  '#DD597D', '#CA00CA', '#A41CC6', '#7373FF', '#29AFD6',
                  '#74BAAC', '#FF7373', '#E37795', '#D900D9', '#BA21E0',
                  '#8282FF', '#4FBDDD', '#8DC7BB', '#FF8E8E', '#E994AB',
                  '#FF2DFF', '#CB59E8', '#9191FF', '#67C7E2', '#A5D3CA',
                  '#FFA4A4', '#EDA9BC', '#F206FF', '#CB59E8', '#A8A8FF',
                  '#8ED6EA', '#C0E0DA', '#FFB5B5', '#F0B9C8', '#FF7DFF',
                  '#D881ED', '#B7B7FF', '#A6DEEE', '#CFE7E2', '#FFC8C8',
                  '#F4CAD6', '#FFA8FF', '#EFCDF8', '#C6C6FF', '#C0E7F3',
                  '#DCEDEA', '#FFEAEA', '#F8DAE2', '#FFC4FF', '#EFCDF8',
                  '#DBDBFF', '#D8F0F8', '#E7F3F1', '#FFEAEA', '#FAE7EC',
                  '#FFE3FF', '#F8E9FC', '#EEEEFF', '#EFF9FC', '#F2F9F8',
                  '#FFFDFD', '#FEFAFB', '#FFFDFF', '#FFFFFF', '#FDFDFF',
                  '#FAFDFE', '#F7FBFA']
        self.set_option("colors", colors)

    def get_color(self):
        if 'colors' not in self.get_options():
            self._create_colors()
        colors = self.get_option("colors")
        next = colors[0]
        del colors[0]
        if len(colors) <= 0:
            self._create_colors()
        else:
            self.set_option("colors", colors)
        return next

    def get_options(self):
        options = json.loads(self.options or "{}")
        return options

    def set_options(self, dic):
        if isinstance(dic, dict):
            self.options = json.dumps(dic)

    def update_options(self, dic):
        options = self.get_options()
        options.update(dic)
        self.options = json.dumps(options)

    def get_option(self, key=None):
        return self.get_options()[key]

    def set_option(self, key, value):
        if key and value:
            options = self.get_options()
            options[key] = value
            self.options = json.dumps(options)

    @models.permalink
    def get_absolute_url(self):
        return ('schema_edit', [self.graph.slug])


class BaseType(models.Model):
    name = models.CharField(_('name'), max_length=150)
    slug = AutoSlugField(populate_from=['name'], max_length=200,
                         editable=False, unique=True)
    plural_name = models.CharField(_('plural name'), max_length=175,
                                   null=True, blank=True)
    description = models.TextField(_('description'), null=True, blank=True)
    schema = models.ForeignKey(Schema)
    order = models.IntegerField(_('order'), null=True, blank=True)
    total = models.IntegerField(_("total objects"), default=0)
    validation = models.TextField(_('validation'), blank=True, null=True,
#                                  default="""
#// The properties list ordered by "Order"
#// and then by "Name" is provided and it
#// will be used. In case of error, set
#// error variable to string;
#properties;
#error = "";
#                                  """,
                                  help_text=_("Code in Javascript to "
                                              "validate all the properties"))
    options = models.TextField(_('options'), null=True, blank=True)

    def get_options(self):
        options = json.loads(self.options or "{}")
        return options

    def set_options(self, dic):
        if isinstance(dic, dict):
            self.options = json.dumps(dic)

    def update_options(self, dic):
        options = self.get_options()
        options.update(dic)
        self.options = json.dumps(options)

    def get_option(self, key=None):
        return self.get_options()[key]

    def set_option(self, key, value):
        if key and value:
            options = self.get_options()
            options[key] = value
            self.options = json.dumps(options)

    class Meta:
        abstract = True
        ordering = ("order", "name")

    @models.permalink
    def get_absolute_url(self):
        return ('nodes_list_full', [self.schema.graph.slug, self.id])

    def has_color(self):
        return 'color' in self.get_options()

    def get_color(self):
        if self.has_color():
            return self.get_option('color')
        else:
            return self.create_color()

    def set_color(self, color):
        with transaction.atomic():
            self.set_option('color', color)
            self.save()


class NodeType(BaseType):
    inheritance = models.ForeignKey('self', null=True, blank=True,
                                    verbose_name=_("inheritance"),
                                    help_text=_("Choose the type which "
                                                "properties will be "
                                                "inherited from"))

    def save(self, *args, **kwargs):
        for field in ("name", "plural_name", "description"):
            value = getattr(self, field, None)
            if value:
                setattr(self, field, value.strip())
        super(NodeType, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_incoming_relationships(self, reflexive=False):
        relationship_types = RelationshipType.objects.filter(target=self)
        if reflexive:
            return relationship_types
        else:
            return relationship_types.exclude(source=F("target"))

    def get_outgoing_relationships(self, reflexive=False):
        relationship_types = RelationshipType.objects.filter(source=self)
        if reflexive:
            return relationship_types
        else:
            return relationship_types.exclude(target=F("source"))

    def get_reflexive_relationships(self):
        return RelationshipType.objects.filter(source=self, target=self)

    def get_all_relationships(self):
        return RelationshipType.objects.filter(Q(source=self) | Q(target=self))

    def count(self):
        if self.total:
            return self.total
        elif self.id:
            return self.schema.graph.nodes.count(label=self.id)
        else:
            return 0

    def all(self):
        if self.id:
            return self.schema.graph.nodes.filter(label=self.id)
        else:
            return []

    def filter(self, *lookups):
        if self.id:
            return self.schema.graph.nodes.filter(*lookups, label=self.id)
        else:
            return []

    def create_color(self):
        with transaction.atomic():
            color = self.schema.get_color()
            self.schema.save()
        self.set_color(color)
        return color


class RelationshipType(BaseType):
    inverse = models.CharField(_('inverse name'), max_length=150,
                               null=True, blank=True,
                               help_text=_("For example, "
                                           "if name is \"writes\", inverse "
                                           "is \"written by\""))
    plural_inverse = models.CharField(_('plural inverse name'), max_length=175,
                                      null=True, blank=True)
    inheritance = models.ForeignKey('self', null=True, blank=True,
                                    verbose_name=_("inheritance"),
                                    help_text=_("Choose the type which "
                                                "properties will be "
                                                "inherited from"))
    source = models.ForeignKey(NodeType, related_name='outgoing_relationships',
                               null=True, blank=True,
                               verbose_name=_("source"),
                               help_text=_("Source type of the "
                                           "allowed relationship"))
    target = models.ForeignKey(NodeType, related_name='incoming_relationships',
                               null=True, blank=True,
                               verbose_name=_("target"),
                               help_text=_("Target type of the "
                                           "allowed relationship"))
    arity_source = models.IntegerField(_('Source arity'), default=0, blank=True,
                                help_text=_("Leave blank for infinite arity,"
                                            "or type with format min:max."))
    arity_target = models.IntegerField(_('Target arity'), default=0, blank=True,
                                help_text=_("Leave blank for infinite arity,"
                                            "or type with format min:max."))

    class Meta:
        ordering = ("order", "inverse", "name")

    def save(self, *args, **kwargs):
        for field in ("name", "plural_name", "inverse", "plural_inverse",
                      "description"):
            value = getattr(self, field, None)
            if value:
                setattr(self, field, value.strip())
        if not self.arity_source or self.arity_source < 1:
            self.arity_source = 0
        if not self.arity_target or self.arity_target < 1:
            self.arity_target = 0
        super(RelationshipType, self).save(*args, **kwargs)

    def count(self):
        if self.total:
            return self.total
        elif self.id:
            return self.schema.graph.relationships.count(label=self.id)
        else:
            return 0

    def all(self):
        if self.id:
            return self.schema.graph.relationships.filter(label=self.id)
        else:
            return []

    def filter(self, *lookups):
        if self.id:
            return self.schema.graph.relationships.filter(*lookups,
                                                          label=self.id)
        else:
            return []

    def __unicode__(self):
        return '%s %s %s' % (self.source.name, self.name, self.target.name)

    def create_color(self):
        color = self.target.get_color()
        self.set_color(color)
        self.set_color_mode('source')
        return color

    def get_color_mode(self):
        '''
        It will return 'target', 'source', 'avg' or 'custom'
        '''
        if 'color_mode' in self.get_options():
            return self.get_option('color_mode')
        else:
            color_mode = 'target'
            self.set_color_mode(color_mode)
            return color_mode

    def set_color_mode(self, color_mode):
        with transaction.atomic():
            self.set_option('color_mode', color_mode)
            self.save()


class BaseProperty(models.Model):
    key = models.CharField(_('key'), max_length=50)
    slug = AutoSlugField(populate_from=['key'], max_length=750,
                         editable=False, unique=True)
    default = models.CharField(_('default value'), max_length=255,
                               blank=True, null=True)
    value = models.CharField(_('value'), max_length=255, blank=True)
    DATATYPE_CHOICES = (
        (u'u', _(u'Default')),
        (_("Basic"), (
            (u's', _(u'String')),
            (u'b', _(u'Boolean')),
            (u'n', _(u'Number')),
        )),
        (_("Advanced"), (
            (u'x', _(u'Text')),
            (u'd', _(u'Date')),
            (u't', _(u'Time')),
            (u'c', _(u'Choices')),
            (u'f', _(u'Float')),
            (u'r', _(u'Collaborator')),
        )),
        (_("Auto"), (
            (u'w', _(u'Auto now')),
            (u'a', _(u'Auto now add')),
            (u'i', _(u'Auto increment')),
            (u'o', _(u'Auto increment update')),
            (u'e', _(u'Auto user')),
        )),
    )
    datatype = models.CharField(_('data type'),
                                max_length=1, choices=DATATYPE_CHOICES,
                                default=u"u")
    required = models.BooleanField(_('is required?'), default=False)
    display = models.BooleanField(_('use as label'), default=False)
    description = models.TextField(_('description'), blank=True, null=True)
    validation = models.TextField(_('validation'), blank=True, null=True,
#                                  default="""
#// The property value and name are provided
#// and modifications on the value will be used.
#// In case of error, set the error variable to
#// a string.
#name;
#value;
#error = "";
#                                  """,
                                  help_text=_("Code in Javascript to "
                                              "validate the property"))
    order = models.IntegerField(_('order'), blank=True, null=True)
    auto = models.IntegerField(_('auto'), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ("order", "key")

    def save(self, *args, **kwargs):
        if self.key:
            self.key = self.key.strip()
        super(BaseProperty, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s: %s" % (self.key, self.value)

    def get_datatype_dict(self):
        return {
            "default": u"u",
            "number": u"n",
            "string": u"s",
            "boolean": u"b",
            "date": u"d",
            "time": u"t",
            "choice": u"c",
            "text": u"x",
            "float": u"f",
            "collaborator": u"r",
            "auto_now": u"w",
            "auto_now_add": u"a",
            "auto_increment": u"i",
            "auto_increment_update": u"o",
            "auto_user": u"e",
        }

    def get_datatype(self):
        datatype_dict = dict(self.DATATYPE_CHOICES)
        return datatype_dict.get(self.datatype)

    def get_choices(self):
        choices = []
        if self.default:
            if not "," in self.default:
                self.default = u"%s," % self.default
            choices = [(u"", u"---------")]
            for choice in self.default.split(","):
                choice_strip = choice.strip()
                key = u"%s" % slugify(choice_strip)
                if key and choice_strip:
                    choices.append((key, choice_strip))
        return choices


class NodeProperty(BaseProperty):
    node = models.ForeignKey(NodeType, verbose_name=_('node'),
                             related_name="properties")

    class Meta:
        verbose_name_plural = _("Node properties")
        ordering = ("order", "key")


class RelationshipProperty(BaseProperty):
    relationship = models.ForeignKey(RelationshipType,
                                     verbose_name=_('relationship'),
                                     related_name="properties")

    class Meta:
        verbose_name_plural = _("Relationship properties")
        ordering = ("order", "key")


@receiver(pre_save, sender=Schema)
def create_schema_colors(*args, **kwargs):
    schema = kwargs.get("instance", None)
    if schema and not schema.pk:
        schema._create_colors()
