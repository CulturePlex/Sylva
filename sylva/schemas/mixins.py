# -*- coding: utf-8 -*-


class SchemaMixin(object):

    def __init__(self, *args, **kwargs):
        super(SchemaMixin, self).__init__(*args, **kwargs)
        self._displays = {}
        self._relationship_names = {}
        self._node_names = {}

    def get_displays(self, label):
        from schemas.models import NodeType
        if label not in self._displays:
            try:
                nodetype = self.nodetype_set.get(pk=label)
                nodetype_properties = nodetype.properties.filter(display=True)
                self._displays[label] = nodetype_properties
                if not self._displays[label]:
                    self._displays[label] = nodetype.properties.all()[:2]
            except NodeType.DoesNotExist:
                self._displays[label] = []
        return self._displays[label]

    def get_relationship_name(self, label):
        from schemas.models import RelationshipType
        if label not in self._relationship_names:
            try:
                name = self.relationshiptype_set.get(id=label).name
                self._relationship_names[label] = name
            except RelationshipType.DoesNotExist:
                self._relationship_names[label] = u""
        return self._relationship_names[label]

    def get_node_name(self, label):
        from schemas.models import NodeType
        if label not in self._node_names:
            try:
                name = self.nodetype_set.get(id=label).name
                self._node_names[label] = name
            except NodeType.DoesNotExist:
                self._node_names[label] = u""
        return self._node_names[label]
