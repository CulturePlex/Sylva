import re
import simplejson
from random import randint

from django.contrib.auth.models import ContentType, Permission, User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db import models


class Graph(models.Model):
    name = models.CharField(_('name'), max_length=120)
    description = models.TextField(_('description'))
    public = models.BooleanField(_('is public?'), default=True)
    order = models.IntegerField(_('order'))
    owner = models.ForeignKey(User, verbose_name=_('owner'))

    class Meta:
        unique_together = ["owner", "name"]  # TODO: Add constraint in forms
        ordering = ("order", )
        permissions = (
            ('view_graph', _('View graph')),
        )

    def __unicode__(self):
        return self.name
