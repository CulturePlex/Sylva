# -*- coding: utf-8 -*-
from pyblueprints.neo4j import Neo4jIndexableGraph as Neo4jGraphDatabase

from engines.gdb.backends import BlueprintsGraphDatabase


class GraphDatabase(BlueprintsGraphDatabase):

    def __init__(self, *args, **kwargs):
        self.url = url
        self.params = params or {}
        self.graph = graph
        self.gdb = Neo4jGraphDatabase(self.url)

    def _validate_property(self, key):
        if key.startswith('_'):
            raise ValueError("%s: Keys starting with _ \
                            are not allowed" % key)

    def _check_property(self, key):
        if key not in vertex.getPropertyKeys():
            raise KeyError("%s key does not exist" % key)

    def _get_public_properties(self, element):
        properties = {}
        for key in element.getPropertyKeys():
            if not key.startswith('_'):
                properties[key] = element.getProperty(key)
        return properties
 
    def _get_public_keys(self, element):
        return self._get_public_properties(element).keys()

    def create_node(self, label, properties=None):
        #Label must be a string
        if not label or not type(label) == basestring:
            raise TypeError("label must be a string")
        vertex = self.gdb.addVertex()
        if type(properties) == dict:
            #Properties starting with _ are not allowed
            for key in properties.keys():
                self._validate_property(key)
            for key, value in properties.iteritems():
                vertex.setProperty(key, value)
        #_id and _label are mandatory internal properties
        vertex.setProperty("_id", vertex.getId())
        vertex.setProperty("_label", label)
        return vertex.getId()

    def delete_node(self, id):
        vertex = self.gdb.getVertex(id)
        self.gdb.removeVertex(vertex)

    def get_node_label(self, id):
        vertex = self.gdb.getVertex(id)
        return vertex.getProperty("_label")

    def set_node_label(self, id, label):
        vertex = self.gdb.getVertex(id)
        return vertex.getProperty("_label")

    def get_node_property(self, id, key):
        self._validate_property(key)
        vertex = self.gdb.getVertex(id)
        self._check_property(key)
        return vertex.getProperty(key)

    def set_node_property(self, id, key, value):
        self._validate_property(key)
        vertex = self.gdb.getVertex(id)
        vertex.setProperty(key, value)

    def delete_node_property(self, id, key):
        self._validate_property(key)
        self._check_property(key)
        vertex = self.gdb.getVertex(id)
        vertex.removeProperty(key)

    def get_node_properties(self, id):
        vertex = self.gdb.getVertex(id)
        return self._public_properties(vertex)

    def set_node_properties(self, id, properties):
        for key in properties:
            self._validate_property(key)
        vertex = self.gdb.getVertex(id)
        for key in self._get_public_keys(vertex):
            vertex.removeProperty(key)
        for key, value in properties.iteritems():
            vertex.setProperty(key, value)

    def delete_node_properties(self, id):
        vertex = self.gdb.getVertex(id)
        for key in self._get_public_keys(vertex):
            vertex.removeProperty(key)

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False):
        vertex = self.gdb.getVertex(id)
        if not incoming and outgoing:
            edges = vertex.getOutEdges()
        elif incoming and notoutgoing:
            edges = vertex.getInEdges()
        else:
            edges = vertex.getBothEdges()
        edges_list = list(edges)
        if include_properties:
            return [{'id': e.getId(),
                    'properties': self.get_relationship_properties(e)} \
                            for e in edges_list]
        else:
            return [e.getId() for e in edges_list)

    def get_nodes(self, ids, include_properties=False):
        result = []
        for _id in ids:
            result.append({'id': _id,
                            'properties': self.get_node_properties(_id))
        return result

    def delete_nodes(self, ids):
        for _id in ids:
            vertex = self.gdb.getVertex(_id)
            self.gdb.removeVertex(vertex)

    def get_all_nodes(self, include_properties=False):
        """
        Get an iterator for all nodes.
        If "include_properties" is True, each element in the list will be a
        dictionary with two keys: "id", containing the id of the relationship,
        and "properties", containing a dictionary with the properties.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_filtered_nodes(self, **lookups):
        """
        Get an iterator for filtered nodes using the parameters expressed in
        the dictionary lookups.
        The most usual lookups from Django should be implemented.
        More info: https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
        """
        raise NotImplementedError("Method has to be implemented")

    # Relationships methdos

    def create_relationship(self, id1, id2, label, properties=None):
        """
        Create a relationship from node "id1" to node "id2".
        If "label" is a string, the relationship will be labeled with "label".
        If "properties" is a dictionary, they will be added to the node.
        Return the id of the relationship created and set it to it.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_label(self, id):
        """
        Get the label of the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_label(self, id, label):
        """
        Set the label of the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationship(self, id):
        """
        Delete the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_property(self, id, key):
        """
        Get the property identified by "key" of the relationship "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_property(self, id, key, value):
        """
        Set to "value" the property identified by "key" of the
        relationship "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationship_property(self, id, key):
        """
        Delete the property identified by "key" of the relationship "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_properties(self, id):
        edge = self.gdb.getEdge(id)
        return self._public_properties(edge)

    def set_relationship_properties(self, id, properties):
        """
        Set to "properties" the dictionary of properties of the
        relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationship_properties(self, id):
        """
        Delete all the properties of the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_source(self, id, include_properties=False):
        """
        Get the node id for the source node of the relationship "id".
        keys, "id" with the id of the source node, and "properties" containing
        a dictionary with the properties of the node.
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_source(self, relationship_id, node_id):
        """
        Set the source node of the relationship "relationship_id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_target(self, id, include_properties=False):
        """
        Get the node id for the target node of the relationship "id".
        If "include_properties" is True, a dictionart is returned with two
        keys, "id" with the id of the target node, and "properties" containing
        a dictionary with the properties of the node.
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_target(self, relationship_id, node_id):
        """
        Set the target node of the relationship "relationship_id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationships(self, ids):
        """
        Delete all the relationships which "id" is on the list "ids".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_all_relationship(self, include_properties=False):
        """
        Get an iterator for all relationship.
        If "include_properties" is True, a new key "properties" is added to the
        returned dictionaries, containing a dictionary with the properties of
        the relationship.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_filtered_relationship(self, **lookups):
        """
        Get an iterator for filtered relationship using the parameters
        expressed in the dictionary lookups.
        The most usual lookups from Django should be implemented.
        More info: https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
        """
        raise NotImplementedError("Method has to be implemented")

    # Quering

    def query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")

