# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.db import models


class Schema(models.Model):
    # graph = models.OneToOneField(Graph, verbose_name=_('graph'))

    class Meta:
        permissions = (
            ('view_schema', _('View schema')),
        )

    def __unicode__(self):
        try:
            return _(u"Schema for \"%s\"") % (self.graph.name)
        except ObjectDoesNotExist:
            return _(u"Schema \"%s\"") % (self.id)

    @models.permalink
    def get_absolute_url(self):
        return ('schemas.views.edit', [str(self.id)])


class BaseType(models.Model):
    name = models.CharField(_('name'), max_length=30)
    description = models.TextField(_('description'), blank=True, null=True)
    schema = models.ForeignKey(Schema)

    class Meta:
        abstract = True


class NodeType(BaseType):
    inheritance = models.ForeignKey('self', null=True, blank=True,
                                    verbose_name=_("inheritance"),
                                    help_text=_("Choose the type which " \
                                                "inherits from."))

    def __unicode__(self):
        return "%s" % (self.name)

    def get_incoming_relationships(self):
        return RelationshipType.objects.filter(target=self)

    def get_outgoing_relationships(self):
        return RelationshipType.objects.filter(source=self)


class RelationshipType(models.Model):
    inheritance = models.ForeignKey('self', null=True, blank=True,
                                    verbose_name=_("inheritance"))
    source = models.ForeignKey(NodeType, related_name='node_source',
                               verbose_name=_("source node"),
                               help_text=_("Source node type"))
    target = models.ForeignKey(NodeType, related_name='node_target',
                               verbose_name=_("target node"),
                               help_text=_("Target node type"))
    arity = models.IntegerField(_('arity'), default=0,
                                help_text=_("Type 0 for infinite arity"))

    def save(self, *args, **kwargs):
        if not self.arity or self.arity < 1:
            self.arity = 0
        super(RelationshipType, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s %s %s' % (self.source.name, self.name, self.target.name)


class BaseProperty(models.Model):
    key = models.CharField(_('key'), max_length=50)
    default = models.CharField(_('default value'), max_length=255,
                               blank=True, null=True)
    value = models.CharField(_('value'), max_length=255, blank=True)
    DATATYPE_CHOICES = (
        (u'u', _(u'Undefined')),
        (u'n', _(u'Number')),
        (u's', _(u'String')),
        (u'b', _(u'Boolean')),
        (u'd', _(u'Date')),
    )
    datatype = models.CharField(_('data type'),
                                max_length=1, choices=DATATYPE_CHOICES,
                                default=u"u")
    required = models.BooleanField(_('is required?'), default=False)
    description = models.TextField(_('description'), blank=True, null=True)
    order = models.IntegerField(_('order'))

    class Meta:
        abstract = True
        ordering = ("order", )

    def __unicode__(self):
        return "%s: %s" % (self.key, self.value)

    def get_datatype_dict(self):
        return dict([(v.lower(), u) for (u, v) in self.DATATYPE_CHOICES])

    def get_datatype(self):
        datatype_dict = dict(self.DATATYPE_CHOICES)
        return datatype_dict.get(self.datatype)


class NodeProperty(BaseProperty):
    node = models.ForeignKey(NodeType, verbose_name=_('node'))

    class Meta:
        verbose_name_plural = _("Node properties")


class RelationshipProperty(BaseProperty):
    relationship = models.ForeignKey(RelationshipType,
                                     verbose_name=_('relationship'))

    class Meta:
        verbose_name_plural = _("Relationship properties")
