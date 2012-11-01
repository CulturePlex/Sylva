# -*- coding: utf-8 -*-


class SchemaMixin(object):

    def __init__(self, *args, **kwargs):
        super(SchemaMixin, self).__init__(*args, **kwargs)
        self._displays = {}
        self._relationship_names = {}
        self._node_names = {}

    def get_displays(self, label):
        if label not in self._displays:
            nodetype = self.nodetype_set.get(pk=label)
            self._displays[label] = nodetype.properties.filter(display=True)
            if not self._displays[label]:
                self._displays[label] = nodetype.properties.all()[:2]
        return self._displays[label]

    def get_relationship_name(self, label):
        if label not in self._relationship_names:
            try:
                name = self.relationshiptype_set.get(id=label).name
                self._relationship_names[label] = name
            except RelationshipType.DoesNotExist:
                self._relationship_names[label] = u""
        return self._relationship_names[label]

    def get_node_name(self, label):
        if label not in self._node_names:
            try:
                name = self.nodetype_set.get(id=label).name
                self._node_names[label] = name
            except nodeType.DoesNotExist:
                self._node_names[label] = u""
        return self._node_names[label]
