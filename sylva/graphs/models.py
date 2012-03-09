# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from guardian import shortcuts as guardian

from base.fields import AutoSlugField
from data.models import Data
from schemas.models import Schema

from graphs.mixins import GraphMixin

PERMISSIONS = {
    'graph': {
        'change_graph': _("Change graph"),
        'view_graph': _("View graph"),
#        'change_collaborators': _("Change collaborators"),
    },
    'schema': {
        'change_schema': _("Change schema"),
        'view_schema': _("View schema"),
    },
    'data': {
        'add_data': _("Add data"),
        'view_data': _("View data"),
        'delete_data': _("Delete data"),
    },
}


class Graph(models.Model, GraphMixin):
    name = models.CharField(_('name'), max_length=120)
    slug = AutoSlugField(populate_from=['name'], max_length=200,
                         editable=False, unique=True)
    description = models.TextField(_('description'), null=True, blank=True)
    public = models.BooleanField(_('is public?'), default=True)
    order = models.IntegerField(_('order'), null=True, blank=True)

    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              related_name='graphs')
    data = models.OneToOneField(Data, verbose_name=_('data'))
    schema = models.OneToOneField(Schema, verbose_name=_('schema'),
                               null=True, blank=True)
    relaxed = models.BooleanField(_('Is schema-relaxed?'), default=False)
    options = models.TextField(_('options'), null=True, blank=True)

    class Meta:
        unique_together = ["owner", "name"]  # TODO: Add constraint in forms
        ordering = ("order", )
        permissions = (
            ('view_graph', _('View graph')),
        )

    def __unicode__(self):
        return self.name

    # TODO: Decide if a graph details view is required
    # @models.permalink
    # def get_absolute_url(self):
    #     return ('graphs.views.details', [str(self.id)])

    def get_collaborators(self):
        all_collaborators = guardian.get_users_with_perms(self)
        return list(all_collaborators.exclude(id=self.owner.id))


@receiver(pre_save, sender=Graph)
def create_data_graph(*args, **kwargs):
    graph = kwargs.get("instance", None)
    if graph:
        try:
            graph.data
        except Data.DoesNotExist:
            data = Data.objects.create()
            graph.data = data


@receiver(pre_save, sender=Graph)
def create_schema_graph(*args, **kwargs):
    graph = kwargs.get("instance", None)
    if graph and not graph.schema:
        schema = Schema.objects.create()
        graph.schema = schema


@receiver(post_save, sender=Graph)
def assign_permissions_to_owner(*args, **kwargs):
    graph = kwargs.get("instance", None)
    if graph:
        owner = graph.owner
        aux = {'graph': graph,
               'schema': graph.schema,
               'data': graph.data}
        for permission_type in aux:
            for permission in PERMISSIONS[permission_type].keys():
                guardian.assign(permission, owner, aux[permission_type])
