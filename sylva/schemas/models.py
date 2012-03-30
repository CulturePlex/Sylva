# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify

from base.fields import AutoSlugField


class Schema(models.Model):
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

    def export(self):

        def get_property_fields(n):
            return {'required': n.required,
                'slug': n.slug,
                'default': n.default,
                'value': n.value,
                'datatype': n.datatype,
                'display': n.display,
                'description': n.description,
                'validation': n.validation}

        schema = {}
        schema["node_types"] = []
        for node_type in self.nodetype_set.all():
            schema["node_types"].append(node_type)
        schema["relationship_types"] = []
        for r_type in self.relationshiptype_set.all():
            schema["relationship_types"].append(r_type)
        schema_json = {"nodeTypes": {}, "allowedEdges":[]}
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

    def _import(self, data):
        with transaction.commit_on_success():
            for node_type, properties in data['nodeTypes'].iteritems():
                n = NodeType(name=node_type, schema=self)
                n.save()
                for prop, values in properties.iteritems():
                    np = NodeProperty(key=prop, node=n)
                    for key, value in values.iteritems():
                        setattr(np, key, value)
                    np.save()
            for edge_type in data['allowedEdges']:
                source = NodeType.objects.get(schema=self, name=edge_type['source'])
                target = NodeType.objects.get(schema=self, name=edge_type['target'])
                rt = RelationshipType(source=source, target=target,
                                schema=self, name=edge_type['label'])
                rt.save()
                for prop, values in edge_type['properties'].iteritems():
                    rp = RelationshipProperty(key=prop, relationship=rt)
                    for key, value in values.iteritems():
                        setattr(rp, key, value)
                    rp.save()

    @models.permalink
    def get_absolute_url(self):
        return ('schemas.views.edit', [str(self.id)])


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

    class Meta:
        abstract = True
        ordering = ("order", "name")


class NodeType(BaseType):
    inheritance = models.ForeignKey('self', null=True, blank=True,
                                    verbose_name=_("inheritance"),
                                    help_text=_("Choose the type which "
                                                "properties will be "
                                                "inherited from"))

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

    def all(self):
        if self.id:
            return self.schema.graph.nodes.filter(label=self.id)
        else:
            return []


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
        if not self.arity_source or self.arity_source < 1:
            self.arity_source = 0
        if not self.arity_target or self.arity_target < 1:
            self.arity_target = 0
        super(RelationshipType, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s %s %s' % (self.source.name, self.name, self.target.name)


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

    class Meta:
        abstract = True
        ordering = ("order", "key")

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
            "float": u"f"
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
