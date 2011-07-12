# -*- coding: utf-8 -*-
from data.models import Data
from schemas.models import Schema


class GraphMixin(object):

    def get_gdb(self):
        return self.data.get_gdb()

    def add_node(self):
        gdb = self.get_gdb()
        gdb.create_node()


class BaseElement(object):
    """
    Base element class for building Node and Relationship classes.
    """

    def __init__(self, id, gdb, properties=None):
        self.id = id
        self.gdb = gdb
        self._properties = properties

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


class Node(BaseElement):
    """
    Node class.
    """

    def delete(self, key=None):
        if key:
            self.__delitem__(key)
        else:
            self.gdb.delete_node(self.id)
            del self

    def __getitem__(self, key):
        self._properties[key] = self.gdb.get_node_property(self.id)
        return self._properties[key]

    def __setitem__(self, key, value):
        self.gdb.set_node_property(self.id, key, value)
        self._properties[key] = value

    def __delitem__(self, key):
        self.gdb.delete_node_property(key)
        del self._properties[key]

    def _get_properties(self):
        self._properties = self.gdb.get_node_properties(self.id)
        return self._properties

    def _set_properties(self, properties={}):
        if not props:
            return None
        self.gdb.set_node_properties(self.gdb.id, properties=properties)
        self._properties = properties
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
            self.gdb.delete_relationship(self.id)
            del self

    def __getitem__(self, key):
        self._properties[key] = self.gdb.get_relationship_property(self.id)
        return self._properties[key]

    def __setitem__(self, key, value):
        self.gdb.set_relationship_property(self.id, key, value)
        self._properties[key] = value

    def __delitem__(self, key):
        self.gdb.delete_relationship_property(key)
        del self._properties[key]

    def _get_properties(self):
        self._properties = self.gdb.get_relationship_properties(self.id)
        return self._properties

    def _set_properties(self, properties={}):
        if not props:
            return None
        self.gdb.set_relationship_properties(self.gdb.id, properties=properties)
        self._properties = properties
        return self._properties

    def _del_properties(self):
        self.gdb.delete_relationship_properties()
        self._properties = {}

    properties = property(_get_properties, _set_properties, _del_properties)
