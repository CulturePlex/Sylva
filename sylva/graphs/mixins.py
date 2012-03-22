# -*- coding: utf-8 -*-
from engines.gdb.backends import NodeDoesNotExist, RelationshipDoesNotExist
from schemas.models import NodeType, RelationshipType


class LimitReachedException(Exception):
    pass


class NodesLimitReachedException(LimitReachedException):
    pass


class RelationshipsLimitReachedException(LimitReachedException):
    pass


class GraphMixin(object):

    def _nodes(self):
        return NodesManager(self)
    nodes = property(_nodes)

    def _relationships(self):
        return RelationshipsManager(self)
    relationships = property(_relationships)


class BaseManager(object):

    def __init__(self, graph):
        self.graph = graph
        self.gdb = graph.data.get_gdb()
        self.schema = (not graph.relaxed) and graph.schema
        self.data = graph.data

    def _filter_dict(self, properties, itemtype):
        if properties:
            if self.schema:
                property_keys = [p.key for p in itemtype.properties.all()]
                popped = [properties.pop(k) for k in properties.keys() \
                                            if (k not in property_keys \
                                                or unicode(k).startswith("_"))]
                del popped
                return properties
            else:
                return dict(filter(lambda (k, v): \
                                    not unicode(k).startswith("_"),
                                   properties.iteritems()))
        else:
            return {}

    def get(self, node_id, *args, **kwargs):
        try:
            return self._get(node_id)
        except KeyError:
            if args:
                return args[0]
            elif "default" in kwargs:
                return kwargs["default"]
            else:
                raise KeyError(node_id)


class NodesManager(BaseManager):
    NodeDoesNotExist = NodeDoesNotExist

    def create(self, label, properties=None):
        if self.data.can_add_nodes():
            if self.schema:
                nodetype = self.schema.nodetype_set.get(pk=label)
                properties = self._filter_dict(properties, nodetype)
                nodetype.total += 1
                nodetype.save()
            node_id = self.gdb.create_node(label=label, properties=properties)
            node = Node(node_id, self.graph, properties=properties)
            self.data.total_nodes += 1
            self.data.save()
            return node
        else:
            raise NodesLimitReachedException

    def _create_node_list(self, eltos):
        nodes = []
        for node_id, node_properties in eltos:
            node = Node(node_id, self.graph, properties=node_properties)
            nodes.append(node)
        return nodes

    def all(self):
        eltos = self.gdb.get_all_nodes(include_properties=True)
        return self._create_node_list(eltos)

    def filter(self, **options):
        if "label" in options:
            label = options.get("label")
            eltos = self.gdb.get_nodes_by_label(label,
                                                include_properties=True)
            return self._create_node_list(eltos)
        else:
            return []

    def iterator(self):
        eltos = self.gdb.get_all_nodes(include_properties=True)
        for node_id, node_properties in eltos:
            node = Node(node_id, self.graph, properties=node_properties)
            yield node

    def in_bulk(self, id_list):
        nodes = []
        eltos = self.gdb.get_nodes_properties(id_list)
        for node_id, node_properties in eltos:
            node = Node(node_id, self.graph, properties=node_properties)
            nodes.append(node)
        return nodes

    def delete(self, **options):
        if "label" in options:
            label = options.get("label")
            eltos = self.gdb.get_nodes_by_label(label,
                                                include_properties=False)
            self.gdb.delete_nodes(eltos)
        elif "id" in options:
            node_id = options.get("id")
            self.gdb.delete_nodes([node_id])
        else:
            eltos = self.gdb.get_all_nodes(include_properties=False)
            self.gdb.delete_nodes([node_id for node_id, props in eltos])

    def _get(self, node_id):
        return Node(node_id, self.graph)


class RelationshipsManager(BaseManager):
    RelationshipDoesNotExist = RelationshipDoesNotExist

    def create(self, source, target, label, properties=None):
        if isinstance(source, Node):
            source_id = source.id
        else:
            source_id = source
        if isinstance(target, Node):
            target_id = target.id
        else:
            target_id = target
        if self.data.can_add_relationships():
            if self.schema:
                reltype = self.schema.relationshiptype_set.get(pk=label)
                properties = self._filter_dict(properties, reltype)
                reltype.total += 1
                reltype.save()
            relationship_id = self.gdb.create_relationship(source_id, target_id,
                                                           label, properties)
            relationship = Relationship(relationship_id, self.graph,
                                        properties=properties)
            self.data.total_relationships += 1
            self.data.save()
            return relationship
        else:
            raise RelationshipsLimitReachedException

    def _create_relationship_list(self, eltos):
        relationships = []
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def all(self):
        eltos = self.gdb.get_all_relationships(include_properties=True)
        return self._create_relationship_list(eltos)

    def filter(self, **options):
        if "label" in options:
            label = options.get("label")
            eltos = self.gdb.get_relationships_by_label(label,
                                                include_properties=True)
            return self._create_relationship_list(eltos)
        else:
            return []

    def iterator(self):
        eltos = self.gdb.get_all_relationships(include_properties=True)
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            yield relationship

    def in_bulk(self, id_list):
        relationships = []
        eltos = self.gdb.get_relationships(id_list, include_properties=True)
        for relationship_id, relationship_properties in eltos.items():
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def delete(self, **options):
        if "label" in options:
            label = options.get("label")
            eltos = self.gdb.get_relationships_by_label(label,
                                                    include_properties=False)
            self.gdb.delete_relationships([relationship_id
                                           for relationship_id, props in eltos])
        elif "id" in options:
            relationship_id = options.get("id")
            self.gdb.delete_relationships([relationship_id])
        else:
            eltos = self.gdb.get_all_relationships(include_properties=False)
            self.gdb.delete_relationships(eltos)

    def _get(self, node_id):
        return Relationship(node_id, self.graph)


class NodeRelationshipsManager(BaseManager):

    def __init__(self, graph, node_id=None):
        super(NodeRelationshipsManager, self).__init__(graph)
        self.node_id = node_id

    def create(self, target, label, properties=None, outgoing=False):
        if outgoing:
            source_id = self.node_id
            target_id = target.id
        else:
            source_id = target.id
            target_id = self.node_id
        if self.data.can_add_relationships():
            if self.schema:
                relationshiptype = self.schema.relationshiptype_set.get(pk=label)
                properties = self._filter_dict(properties, relationshiptype)
                relationshiptype.total += 1
                relationshiptype.save()
            relationship_id = self.gdb.create_relationship(source_id,
                                                           target_id,
                                                           label,
                                                           properties)
            relationship = Relationship(relationship_id, self.graph,
                                        properties=properties)
            self.data.total_relationships += 1
            self.data.save()
            return relationship
        else:
            raise RelationshipsLimitReachedException

    def all(self):
        relationships = []
        eltos = self.gdb.get_node_relationships(self.node_id,
                                                include_properties=True)
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def filter(self, **options):
        label= None
        if "label" in options:
            label = options.get("label")
        relationships = []
        eltos = self.gdb.get_node_relationships(self.node_id,
                                                include_properties=True,
                                                label=label)
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def _create_relationship_list(self, eltos):
        relationships = []
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def incoming(self):
        relationships = []
        eltos = self.gdb.get_node_relationships(self.node_id, incoming=True,
                                                include_properties=True)
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def outgoing(self):
        relationships = []
        eltos = self.gdb.get_node_relationships(self.node_id, outgoing=True,
                                                include_properties=True)
        for relationship_id, relationship_properties in eltos:
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def iterator(self):
        iterator = self.gdb.get_node_relationships(include_properties=True)
        for relationship_id, relationship_properties in iterator.iteritems():
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            yield relationship

    def in_bulk(self, id_list):
        relationships = []
        eltos = self.gdb.get_node_relationships(self.node_id, incoming=True,
                                                include_properties=True)
        for relationship_id, relationship_properties in eltos.items():
            relationship = Relationship(relationship_id, self.graph,
                                        properties=relationship_properties)
            relationships.append(relationship)
        return relationships

    def _get(self):
        return Relationship(self.node_id, self.graph)


class PropertyDict(dict):

    def __init__(self, element=None, *args, **kwargs):
        self.element = element
        super(PropertyDict, self).__init__(*args, **kwargs)

    def update(self, properties, **kwargs):
        super(PropertyDict, self).update(properties, **kwargs)
        if self.element:
            if isinstance(self.element, Node):
                self.element.gdb.update_node_properties(self.element.id,
                                                        properties=properties)
            elif isinstance(self.element, Relationship):
                self.element.gdb.update_relationship_properties(self.element.id,
                                                        properties=properties)


class BaseElement(object):
    """
    Base element class for building Node and Relationship classes.
    """

    def __init__(self, id, graph, properties=None):
        self._id = id
        self.graph = graph
        self.gdb = graph.data.get_gdb()
        self.schema = (not graph.relaxed) and graph.schema
        self.data = graph.data
        if not properties:
            self._get_properties()
        else:
            self._properties = self._set_properties(properties)

    def get(self, key, *args, **kwargs):
        try:
            return self.__getitem__(key)
        except KeyError:
            if args:
                return args[0]
            elif "default" in kwargs:
                return kwargs["default"]
            else:
                raise KeyError(key)

    def __contains__(self, obj):
        return obj in self._properties

    def set(self, key, value):
        self.__setitem__(key, value)

    def __len__(self):
        return len(self._properties)

    def __iter__(self):
        return self._properties.__iter__()

    def __eq__(self, obj):
        return (hasattr(obj, "id")
                and self.id == obj.id
                and hasattr(obj, "__class__")
                and self.__class__ == obj.__class__)

    def __ne__(self, obj):
        return not self.__cmp__(obj)

    def __nonzero__(self):
        return bool(self.id and self.gdb and self._properties)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__, self.id)

    def _get_id(self):
        return self._id
    id = property(_get_id)

    def _filter_dict(self, properties):
        if properties:
            if self.schema:
                property_keys = self._get_property_keys()
                popped = [properties.pop(k) for k in properties.keys() \
                                            if (k not in property_keys \
                                                or unicode(k).startswith("_"))]
                del popped
                return properties
            else:
                return dict(filter(lambda (k, v): \
                                    not unicode(k).startswith("_"),
                                   properties.iteritems()))
        else:
            return {}

    def _get_display(self, separator=u", "):
        if not self._properties:
            return u"%s" % self._id
        else:
            properties_to_display = self._get_properties_display()
            if not properties_to_display:
                properties_to_display = []
                properties_values = self._properties.values()[:5]
                for i in range(len(properties_values)):
                    if properties_values[i]:
                        try:
                            unicode_value = unicode(properties_values[i])
                            properties_to_display.append(unicode_value)
                        except UnicodeDecodeError:
                            pass
            if properties_to_display:
                return separator.join(properties_to_display)
            else:
                return u"%s" % self._id
    display = property(_get_display)


class Node(BaseElement):
    """
    Node class.
    """

    def delete(self, key=None):
        if key:
            self.__delitem__(key)
        else:
            label = self.label
            self.gdb.delete_node(self.id)
            self.data.total_nodes -= 1
            self.data.save()
            if self.schema:
                nodetype = self.schema.nodetype_set.get(pk=label)
                nodetype.total -= 1
                nodetype.save()
            del self

    def to_json(self):
        node_dict = self.properties.copy()
        node_dict.update({
            'id': self.id,
            'type': NodeType.objects.get(id=self.label).name
        })
        return node_dict
            
    def __getitem__(self, key):
        self._properties[key] = self.gdb.get_node_property(self.id, key)
        return self._properties[key]

    def __setitem__(self, key, value):
        self.gdb.set_node_property(self.id, key, value)
        self._properties[key] = value

    def __delitem__(self, key):
        self.gdb.delete_node_property(self.id, key)
        del self._properties[key]

    def _get_label(self):
        return self.gdb.get_node_label(self.id)
    label = property(_get_label)

    def _relationships(self):
        return NodeRelationshipsManager(self.graph, self.id)
    relationships = property(_relationships)

    def _get_properties_display(self):
        displays = []
        if self.schema:
            nodetype = self.schema.nodetype_set.get(pk=self.label)
            displays = nodetype.properties.filter(display=True)
            if not displays:
                displays = nodetype.properties.all()[:2]
        properties_to_display = []
        properties = self._properties
        for display in displays:
            if display.key in properties:
                if display.datatype == u"b":  # Boolean
                    if properties[display.key]:
                        properties_to_display.append(display.key)
                    else:
                        properties_to_display.append(u"¬%s" % display.key)
                else:
                    try:
                        unicode_value = unicode(properties[display.key])
                        properties_to_display.append(unicode_value)
                    except UnicodeDecodeError:
                        pass
        return properties_to_display

    def _get_property_keys(self):
        itemtypes = self.schema.nodetype_set.filter(pk=self.label)
        if itemtypes:
            property_keys = [p.key for p in itemtypes[0].properties.all()]
        else:
            property_keys = []
        return property_keys

    def _get_properties(self):
        self._properties = self.gdb.get_node_properties(self.id)
        return self._properties

    def _set_properties(self, properties=None):
        if not properties:
            return None
        properties = self._filter_dict(properties)
        self.gdb.set_node_properties(self.id, properties=properties)
        self._properties = PropertyDict(self, properties)
        return self._properties

    def _del_properties(self):
        self.gdb.delete_node_properties()
        self._properties = {}

    properties = property(_get_properties, _set_properties, _del_properties)


class Relationship(BaseElement):
    """
    Relationship class.
    """

    def delete(self, key=None):
        if key:
            self.__delitem__(key)
        else:
            if self.schema:
                reltype = self.schema.relationshiptype_set.get(pk=self.label)
            self.gdb.delete_relationship(self.id)
            self.data.total_relationships -= 1
            self.data.save()
            if self.schema:
                reltype.total -= 1
                reltype.save()
            del self

    def to_json(self):
        return {
            'id': self.id,
            'source': self.source.display,
            'type': RelationshipType.objects.get(id=self.label).name,
            'target': self.target.display,
            'properties': self.properties.copy()
        }

    def __getitem__(self, key):
        value = self.gdb.get_relationship_property(self.id, key)
        self._properties[key] = value
        return self._properties[key]

    def __setitem__(self, key, value):
        self.gdb.set_relationship_property(self.id, key, value)
        self._properties[key] = value

    def __delitem__(self, key):
        self.gdb.delete_relationship_property(key)
        del self._properties[key]

    def _get_source(self):
        node_id, properties = self.gdb.get_relationship_source(self.id)
        return Node(node_id, self.graph, properties)

    def _set_source(self, node):
        self.gdb.set_relationship_source(self.id, node.id)

    source = property(_get_source, _set_source)

    def _get_target(self):
        node_id, properties = self.gdb.get_relationship_target(self.id)
        return Node(node_id, self.graph, properties)

    def _set_target(self, node):
        self.gdb.set_relationship_target(self.id, node.id)

    target = property(_get_target, _set_target)

    def _get_label(self):
        return self.gdb.get_relationship_label(self.id)
    label = property(_get_label)

    def _get_property_keys(self):
        itemtypes = self.schema.relationshiptype_set.filter(pk=self.label)
        if itemtypes:
            property_keys = [p.key for p in itemtypes[0].properties.all()]
        else:
            property_keys = []
        return property_keys

    def _get_properties(self):
        self._properties = self.gdb.get_relationship_properties(self.id)
        return self._properties

    def _set_properties(self, properties=None):
        if not properties:
            return None
        properties = self._filter_dict(properties)
        self.gdb.set_relationship_properties(self.id,
                                             properties=properties)
        self._properties = PropertyDict(self, properties)
        return self._properties

    def _del_properties(self):
        self.gdb.delete_relationship_properties()
        self._properties = {}

    properties = property(_get_properties, _set_properties, _del_properties)
