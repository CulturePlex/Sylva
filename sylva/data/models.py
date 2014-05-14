# -*- coding: utf-8 -*-
from os import path

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from engines.models import Instance
from data.mixins import DataMixin


class Data(models.Model, DataMixin):
    # graph = models.OneToOneField(Graph, verbose_name=_('graph'))
    instance = models.ForeignKey(Instance,
                                 verbose_name=_("Graph database instance"),
                                 blank=True, null=True)
    total_nodes = models.IntegerField(_("total nodes"), default=0)
    total_relationships = models.IntegerField(_("total relationships"),
                                              default=0)
    total_queries = models.IntegerField(_("total queries"), default=0)
    total_storage = models.IntegerField(_("total storage"), default=0)
    options = models.TextField(_('options'), null=True, blank=True)
    total_analytics = models.IntegerField(_("total analytics"),
                                          default=0)

    class Meta:
        verbose_name_plural = _("data")
        permissions = (
            ('view_data', _('View nodes and relationships')),
        )

    def __unicode__(self):
        try:
            if self.instance:
                return _(u"Data for {0} on instance {1}").format(self.graph.name, self.instance.name)
            else:
                return _(u"Data for {0} on default instance").format(self.graph.name)
        except ObjectDoesNotExist:
            if self.instance:
                return _(u"Data on instance {0}").format(self.instance.name)
            else:
                return _(u"Data on default instance")

    @models.permalink
    def get_absolute_url(self):
        return ('nodes_list', [self.graph.slug])


class MediaNode(models.Model):
    node_id = models.CharField(_("node identifier"), max_length=100)
    data = models.ForeignKey(Data, verbose_name=_("data"), related_name="data")

    def __unicode__(self):
        return u'%s' % (self.node_id)


def node_files(instance, filename):
    # Getting the node ID
    node_id = str(instance.media_node.node_id)
    # Getting the filename
    if u"." in filename:
        filename_split = filename.rsplit(u".", 1)
        slug_filename = u"%s.%s" % (slugify(filename_split[0]),
                                    filename_split[1])
        file_path = path.join(u"nodes", node_id, slug_filename)
    else:
        file_path = path.join("nodes", node_id, filename)
    # Getting the graph name
    graph_slug = instance.media_node.data.graph.slug
    # TODO: Add users' storage linked to instances
    return path.join(graph_slug, file_path)


class MediaFile(models.Model):
    media_node = models.ForeignKey(MediaNode, verbose_name=_("media node"),
                                   related_name="files")
    media_label = models.CharField(_("label"), max_length=150)
    media_file = models.FileField(_("file"), upload_to=node_files)

    def __unicode__(self):
        return _(u'{0} ({1} for {2})').format(self.media_label, self.media_file.name, self.media_node.node_id)

    class Meta:
        verbose_name_plural = _("Media files")


class MediaLink(models.Model):
    media_node = models.ForeignKey(MediaNode, verbose_name=_("media node"),
                                   related_name="links")
    media_label = models.CharField(_("label"), max_length=150)
    media_link = models.URLField(_('URL'))

    def __unicode__(self):
        return _(u'{0} ({1} for {2})').format(self.media_label, self.media_link, self.media_node.node_id)

    class Meta:
        verbose_name_plural = _("Media links")


@receiver(post_save, sender=MediaFile)
def create_schema_graph(*args, **kwargs):
    instance = kwargs.get("instance", None)
    size = instance.media_file.size
    data = instance.media_node.data
    data.total_storage += size
    data.save()


@receiver(pre_delete, sender=MediaFile)
def delete_schema_graph(*args, **kwargs):
    instance = kwargs.get("instance", None)
    size = instance.media_file.size
    data = instance.media_node.data
    data.total_storage -= size
    data.save()
