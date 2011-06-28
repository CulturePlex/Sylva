# -*- coding: utf-8 -*-
import binascii
from Crypto.Cipher import Blowfish

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.utils.translation import gettext as _
from django.db import models

default_engine = settings.GRAPHDATABASES["default"]["ENGINE"]


class Instance(models.Model):
    name = models.CharField(_("name"), max_length=100)
    engine = models.CharField(_("engine"), max_length=50,
                              default=default_engine)
    schema = models.CharField(_("schema"), max_length=10, default="http")
    host = models.CharField(_("host"), max_length=250, default="localhost")
    port = models.PositiveIntegerField(_("port"), max_length=10,
                                       default="7474")
    path = models.CharField(_("path"), max_length=250, default="db/data")
    username = models.CharField(_("username"), max_length=250,
                                null=True, blank=True)
    encrypted_password = models.CharField(_("encrypted password"),
                                          max_length=32,
                                          null=True, blank=True)
    plain_password = models.CharField(_("password"),
                                      max_length=50,
                                      null=True, blank=True,
                                      help_text=_("Type again to change"))

    owner = models.ForeignKey(User, verbose_name=_('owner'))

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        if self.plain_password:
            self._set_password(self.plain_password)
            self.plain_password = ""
        super(Instance, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('engines.views.edit', [str(self.id)])

    def get_gdb(self):
        username = self.username or self.owner.username
        if username and self.password:
            connection_string = "%s://%s:%s@%s:%s/%s/" % (self.schema,
                                                          username,
                                                          self.password,
                                                          self.host,
                                                          self.port,
                                                          self.path)
        elif username:
            connection_string = "%s://%s@%s:%s/%s/" % (self.schema, username,
                                                       self.host, self.port,
                                                       self.path)
        else:
            connection_string = "%s://%s:%s/%s/" % (self.schema, self.host,
                                                    self.port, self.path)
        module = import_module(self.engine)
        gdb = module.GraphDatabase(connection_string)
        return gdb

    def _get_password(self):
        enc_obj = Blowfish.new(settings.SECRET_KEY)
        hex_password = binascii.a2b_hex(self.encrypted_password)
        return u"%s" % enc_obj.decrypt(hex_password).rstrip()

    def _set_password(self, value):
        enc_obj = Blowfish.new(settings.SECRET_KEY)
        repeat = 8 - (len(value) % 8)
        value = value + " " * repeat
        self.encrypted_password = binascii.b2a_hex(enc_obj.encrypt(value))

    password = property(_get_password, _set_password)
