# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from guardian.shortcuts import assign, get_users_with_perms, remove_perm

from base.fields import AutoSlugField
from schemas.models import (Schema, NodeType, NodeProperty, RelationshipType,
                            RelationshipProperty)
from data.models import Data, MediaNode, MediaLink

from graphs.mixins import GraphMixin

PERMISSIONS = {
    'graph': {
        'change_graph': _("Change"),
        'view_graph': _("View"),
        'change_collaborators': _("Collaborators"),
    },
    'schema': {
        'change_schema': _("Change"),
        'view_schema': _("View"),
    },
    'data': {
        'add_data': _("Add"),
        'view_data': _("View"),
        'change_data': _("Change"),
        'delete_data': _("Delete"),
    },
}


class Graph(models.Model, GraphMixin):
    name = models.CharField(_('name'), max_length=120)
    slug = AutoSlugField(populate_from=['name'], max_length=200,
                         editable=False, unique=True)
    description = models.TextField(_('description'), null=True, blank=True)
    public = models.BooleanField(_('is public?'), default=True,
                                 help_text=_("It means publicly available "
                                             "to be browsed"))
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
            ('change_collaborators', _("Change collaborators")),
        )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('graph_view', [self.slug])

    def is_empty(self):
        return self.data.total_nodes == 0

    def clone(self, new_graph, clone_data=True):
        schema = self.schema
        new_schema = new_graph.schema
        nt_map, rt_map = self._clone_schema(schema, new_schema)
        if clone_data:
            self._clone_data(new_graph, nt_map, rt_map)

    def _clone_schema(self, schema, new_schema):
        nodetypes_map = {}      # map old/new nodetypes IDs
        relationtypes_map = {}  # map old/new relationtypes IDs
        nodetypes = schema.nodetype_set.all()
        for nt in nodetypes:
            new_nt = NodeType(schema=new_schema,
                              name=nt.name,
                              plural_name=nt.plural_name,
                              description=nt.description,
                              order=nt.order,
                              total=nt.total,
                              validation=nt.validation)
            new_nt.save()
            nodetypes_map[nt.id] = new_nt.id
            properties = nt.properties.all()
            for np in properties:
                new_np = NodeProperty(node=new_nt,
                                      key=np.key,
                                      value=np.value,
                                      default=np.default,
                                      datatype=np.datatype,
                                      required=np.required,
                                      display=np.display,
                                      description=np.description,
                                      validation=np.validation,
                                      order=np.order)
                new_np.save()
        relationtypes = schema.relationshiptype_set.all()
        for rt in relationtypes:
            source = NodeType.objects.get(schema=new_schema,
                                          name=rt.source.name)
            target = NodeType.objects.get(schema=new_schema,
                                          name=rt.target.name)
            new_rt = RelationshipType(schema=new_schema,
                                      source=source,
                                      target=target,
                                      name=rt.name,
                                      plural_name=rt.plural_name,
                                      description=rt.description,
                                      order=rt.order,
                                      total=rt.total,
                                      validation=rt.validation,
                                      inverse=rt.inverse,
                                      plural_inverse=rt.plural_inverse,
                                      arity_source=rt.arity_source,
                                      arity_target=rt.arity_target)
            new_rt.save()
            relationtypes_map[rt.id] = new_rt.id
            properties = rt.properties.all()
            for rp in properties:
                new_rp = RelationshipProperty(relationship=new_rt,
                                              key=rp.key,
                                              value=rp.value,
                                              default=rp.default,
                                              datatype=rp.datatype,
                                              required=rp.required,
                                              display=rp.display,
                                              description=rp.description,
                                              validation=rp.validation,
                                              order=rp.order)
                new_rp.save()
        return nodetypes_map, relationtypes_map

    def _clone_data(self, new_graph, nodetypes_map, relationtypes_map):
        nodes_map = {}  # map old/new nodes IDs
        data = self.data
        new_data = new_graph.data
        nodes = self.nodes.all()
        for n in nodes:
            node_label = int(n.label)
            if node_label in nodetypes_map:
                nt = NodeType.objects.get(pk=nodetypes_map[node_label])
                new_node = new_graph.nodes.create(label=unicode(nt.id),
                                                  properties=n.properties)
                nodes_map[n.id] = new_node
        relations = self.relationships.all()
        for r in relations:
            rel_label = int(r.label)
            if rel_label in relationtypes_map:
                rt = RelationshipType.objects.get(pk=relationtypes_map[rel_label])
                new_graph.relationships.create(nodes_map[r.source.id],
                                               nodes_map[r.target.id],
                                               label=unicode(rt.id),
                                               properties=r.properties)
        media_nodes = data.data.all()
        for mn in media_nodes:
            node_id = int(mn.node_id)
            if node_id in nodes_map:
                new_mn = MediaNode(node_id=nodes_map[node_id].id,
                                   data=new_data)
                new_mn.save()
                media_links = mn.links.all()
                for ml in media_links:
                    new_ml = MediaLink(media_node=new_mn,
                                       media_label=ml.media_label,
                                       media_link=ml.media_link)
                    new_ml.save()

    def get_collaborators(self, include_anonymous=False, as_queryset=False):
        all_collaborators = get_users_with_perms(self)
        if include_anonymous:
            if as_queryset:
                return all_collaborators.exclude(id=self.owner.id)
            else:
                return list(all_collaborators.exclude(id=self.owner.id))
        else:
            if as_queryset:
                return all_collaborators.exclude(id__in=[self.owner.id,
                                                 settings.ANONYMOUS_USER_ID])
            else:
                return list(all_collaborators.exclude(id__in=[self.owner.id,
                                                  settings.ANONYMOUS_USER_ID]))


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
                assign(permission, owner, aux[permission_type])
    anonymous = User.objects.get(id=settings.ANONYMOUS_USER_ID)
    if graph.public:
        for permission, obj in aux.items():
            assign("view_%s" % permission, anonymous, obj)
    else:
        for permission, obj in aux.items():
            perm = "view_%s" % permission
            if anonymous.has_perm(perm, obj):
                remove_perm(perm, anonymous, obj)
