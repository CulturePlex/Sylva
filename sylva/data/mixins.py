# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Account
from engines.gdb.utils import get_gdb


class DataMixin(object):

    def __init__(self, *args, **kwargs):
        super(DataMixin, self).__init__(*args, **kwargs)
        self._gdb = None

    def get_gdb(self):
        if not self._gdb:
            try:
                if self.instance:
                    self._gdb = self.instance.get_gdb(graph=self.graph)
                else:
                    self._gdb = get_gdb(graph=self.graph)
            except ObjectDoesNotExist:
                if self.instance:
                    self._gdb = self.instance.get_gdb()
                else:
                    self._gdb = get_gdb()
        return self._gdb

    def can_add_nodes(self):
        user = self.graph.owner
        if user.is_superuser or user.is_staff:
            return True
        else:
            try:
                profile = user.profile
                # HACK: Avoid the QuerySet cache
                account = Account.objects.get(pk=profile.account.id)
                return (self.total_nodes < account.nodes)
            except:
                return False

    def can_add_relationships(self):
        user = self.graph.owner
        if user.is_superuser or user.is_staff:
            return True
        else:
            try:
                profile = user.profile
                # HACK: Avoid the QuerySet cache
                account = Account.objects.get(pk=profile.account.id)
                return (self.total_relationships < account.relationships)
            except:
                return False
