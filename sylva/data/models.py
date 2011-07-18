# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext as _

from engines.gdb.utils import get_gdb
from engines.models import Instance


class Data(models.Model):
    # graph = models.OneToOneField(Graph, verbose_name=_('graph'))
    instance = models.ForeignKey(Instance,
                                 verbose_name=_("Graph database instance"),
                                 blank=True, null=True)
    total_nodes = models.IntegerField(_("total nodes"), default=0)
    total_relationships = models.IntegerField(_("total relationships"),
                                              default=0)

    class Meta:
        verbose_name_plural = _("data")

    def __unicode__(self):
        try:
            if self.instance:
                return _(u"Data for \"%s\" on instance \"%s\"") \
                       % (self.graph.name, self.instance.name)
            else:
                return _(u"Data for \"%s\" on default instance") \
                       % self.graph.name
        except ObjectDoesNotExist:
            if self.instance:
                return _(u"Data on instance \"%s\"") % self.instance.name
            else:
                return _(u"Data on default instance")

    def get_gdb(self):
        if self.instance:
            try:
                return self.instance.get_gdb(self.graph)
            except ObjectDoesNotExist:
                return self.instance.get_gdb()
        else:
            return get_gdb()

    @models.permalink
    def get_absolute_url(self):
        return ('data.views.edit', [str(self.id)])


class MediaNode(models.Model):
    node_id = models.CharField(_("node identifier"), max_length=100)
    data = models.ForeignKey(Data, verbose_name=_("data"))

    def __unicode__(self):
        return u'%s' % (self.node_id)


class MediaFile(models.Model):
    media_node = models.ForeignKey(MediaNode, verbose_name=_("media node"))
    media_label = models.CharField(_("media label"), max_length=150)
    MEDIA_TYPES = (('image', _('Image')),
                   ('audio', _('Audio')),
                   ('video', _('Video')),
                   ('docum', _('Document')))
    media_type = models.CharField(_("media type"), max_length=5,
                                  choices=MEDIA_TYPES)
    media_file = models.FileField(_("media file"), upload_to='nodes')

    def __unicode__(self):
        return _(u'%s (%s for %s)') % (self.media_label,
                                       self.get_media_type_display(),
                                       self.media_node.node_id)

    class Meta:
        verbose_name_plural = _("Media files")


class MediaLink(models.Model):
    media_node = models.ForeignKey(MediaNode, verbose_name=_("media node"))
    media_label = models.CharField(_("media label"), max_length=150)
    media_link = models.URLField(_('media URL'), verify_exists=False)

    def __unicode__(self):
        return _(u'%s (%s for %s)') % (self.media_label,
                                       self.media_link,
                                       self.media_node.node_id)

    class Meta:
        verbose_name_plural = _("Media links")
