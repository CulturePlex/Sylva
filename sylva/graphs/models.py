# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.db import models

from data.models import Data
from schemas.models import Schema

from graphs.mixins import GraphMixin


class Graph(models.Model, GraphMixin):
    name = models.CharField(_('name'), max_length=120)
    description = models.TextField(_('description'), null=True, blank=True)
    public = models.BooleanField(_('is public?'), default=True)
    order = models.IntegerField(_('order'), null=True, blank=True)

    owner = models.ForeignKey(User, verbose_name=_('owner'),
                              related_name='graphs')
    data = models.OneToOneField(Data, verbose_name=_('data'))
    schema = models.OneToOneField(Schema, verbose_name=_('schema'),
                               null=True, blank=True)
    relaxed = models.BooleanField(_('Is schema-relaxed?'), default=False)

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
