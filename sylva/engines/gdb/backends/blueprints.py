# -*- coding: utf-8 -*-

from engines.gdb.backends import (BaseGraphDatabase,
                                NodeDoesNotExist,
                                RelationshipDoesNotExist)


class BlueprintsGraphDatabase(BaseGraphDatabase):

    PRIVATE_PREFIX = '_'

    def setup_indexes(self):
        vertex_index_name = "%s_nodes" % self.graph_id
        edge_index_name = "%s_relationships" % self.graph_id
        vertex_index = self.gdb.getIndex(vertex_index_name, "vertex")
        if not vertex_index:
            vertex_index = self.gdb.createManualIndex(vertex_index_name,
                                                    "vertex")
        edge_index = self.gdb.getIndex(edge_index_name, "edge")
        if not edge_index:
            edge_index = self.gdb.createManualIndex(edge_index_name,
                                                    "edge")
        self.node_index = vertex_index
        self.relationship_index = edge_index

    def __get_vertex(self, id):
        vertex = self.gdb.getVertex(id)
        if not vertex:
            raise NodeDoesNotExist(id)
        return vertex

    def __get_edge(self, id):
        edge = self.gdb.getEdge(id)
        if not edge:
            raise RelationshipDoesNotExist(id)
        return edge

    def __validate_property(self, key):
        if key.startswith(self.PRIVATE_PREFIX):
            raise ValueError("%s: Keys starting with %s \
                            are not allowed" % (key, self.PRIVATE_PREFIX))

    def __check_property(self, element, key):
        if key not in element.getPropertyKeys():
            raise KeyError("%s key does not exist" % key)

    def __get_public_properties(self, element):
        properties = {}
        for key in element.getPropertyKeys():
            if not key.startswith('_') and not key.startswith(self.PRIVATE_PREFIX):
                properties[key] = element.getProperty(key)
        return properties
 
    def __get_public_keys(self, element):
        return self.__get_public_properties(element).keys()

    def __get_element_label(self, element):
        return element.getProperty("%slabel" % self.PRIVATE_PREFIX)

    def __set_element_label(self, element, label):
        return element.setProperty("%slabel" % self.PRIVATE_PREFIX, label)

    def __get_element_property(self, element, key):
        self.__validate_property(key)
        self.__check_property(element, key)
        return element.getProperty(key)

    def __set_element_property(self, element, key, value):
        self.__validate_property(key)
        element.setProperty(key, value)

    def __delete_element_property(self, element, key):
        self.__validate_property(key)
        self.__check_property(element, key)
        element.removeProperty(key)

    def __get_element_properties(self, element):
        return self.__get_public_properties(element)

    def __set_element_properties(self, element, properties):
        for key in properties:
            self.__validate_property(key)
        for key in self.__get_public_keys(element):
            element.removeProperty(key)
        for key, value in properties.iteritems():
            element.setProperty(key, value)

    def __update_element_properties(self, element, properties):
        for key in properties:
            self.__validate_property(key)
        for key, value in properties.iteritems():
            element.setProperty(key, value)

    def __delete_element_properties(self, element):
        for key in self.__get_public_keys(element):
            element.removeProperty(key)

    def create_node(self, label, properties=None):
        #Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        vertex = self.gdb.addVertex()
        if type(properties) == dict:
            #Properties starting with _ are not allowed
            for key in properties.keys():
                self.__validate_property(key)
            for key, value in properties.iteritems():
                vertex.setProperty(key, value)
        #_id and _label is a mandatory internal properties
        if not "_id" in vertex.getPropertyKeys():
            vertex.setProperty("_id", vertex.getId())
        vertex.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        self.node_index.put("id", str(vertex.getId()), vertex)
        self.node_index.put("label", label, vertex)
        self.node_index.put("graph", self.graph_id, vertex)
        return vertex.getId()

    def delete_node(self, id):
        vertex = self.__get_vertex(id)
        self.gdb.removeVertex(vertex)

    def get_node_label(self, id):
        vertex = self.__get_vertex(id)
        return self.__get_element_label(vertex)

    def set_node_label(self, id, label):
        vertex = self.__get_vertex(id)
        return self.__set_element_label(vertex, label)

    def get_node_property(self, id, key):
        vertex = self.__get_vertex(id)
        return self.__get_element_property(vertex, key)

    def set_node_property(self, id, key, value):
        vertex = self.__get_vertex(id)
        self.__set_element_property(vertex, key, value)

    def delete_node_property(self, id, key):
        vertex = self.__get_vertex(id)
        self.__delete_element_property(vertex, key)

    def get_node_properties(self, id):
        vertex = self.__get_vertex(id)
        return self.__get_public_properties(vertex)

    def set_node_properties(self, id, properties):
        vertex = self.__get_vertex(id)
        self.__set_element_properties(vertex, properties)

    def update_node_properties(self, id, properties):
        vertex = self.__get_vertex(id)
        self.__update_element_properties(vertex, properties)

    def delete_node_properties(self, id):
        vertex = self.__get_vertex(id)
        self.__delete_element_properties(vertex)

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False):
        vertex = self.__get_vertex(id)
        if not incoming and outgoing:
            edges = vertex.getOutEdges()
        elif incoming and not outgoing:
            edges = vertex.getInEdges()
        else:
            edges = vertex.getBothEdges()
        edges_list = [e.getId() for e in list(edges)]
        result = {}
        if include_properties:
            for e in edges_list:
                result[e] = self.get_relationship_properties(e)
            return result
        else:
            return result.fromkeys(edges_list)

    def get_nodes_properties(self, ids):
        result = {}
        for _id in ids:
            result[_id] = self.get_node_properties(_id)
        return result

    def delete_nodes(self, ids):
        for _id in ids:
            vertex = self.gdb.getVertex(_id)
            self.gdb.removeVertex(vertex)

    def get_all_nodes(self, include_properties=False):
        for node in self.node_index.get("graph", self.graph_id):
            if include_properties:
                yield {node.getId(): self.get_node_properties(node.getId())}
            else:
                yield node.getId()

    def get_filtered_nodes(self, **lookups):
        """
        Get an iterator for filtered nodes using the parameters expressed in
        the dictionary lookups.
        The most usual lookups from Django should be implemented.
        More info: https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
        """
        raise NotImplementedError("Method has to be implemented")

    def create_relationship(self, id1, id2, label, properties=None):
        #Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        v1 = self.__get_vertex(id1)
        v2 = self.__get_vertex(id2)
        edge = self.gdb.addEdge(v1, v2, label)
        if type(properties) == dict:
            #Properties starting with _ are not allowed
            for key in properties.keys():
                self.__validate_property(key)
            for key, value in properties.iteritems():
                edge.setProperty(key, value)
        #_id and _label is a mandatory internal property
        if not "_id" in edge.getPropertyKeys():
            edge.setProperty("_id", edge.getId())
        edge.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        self.relationship_index.put("id", str(edge.getId()), edge)
        self.relationship_index.put("label", label, edge)
        self.relationship_index.put("graph", self.graph_id, edge)
        return edge.getId()

    def get_relationship_label(self, id):
        edge = self.__get_edge(id)
        return self.__get_element_label(edge)

    def set_relationship_label(self, id, label):
        edge = self.__get_edge(id)
        self.__set_element_label(edge, label)

    def delete_relationship(self, id):
        edge = self.__get_edge(id)
        self.gdb.removeEdge(edge)

    def get_relationship_property(self, id, key):
        edge = self.__get_edge(id)
        return self.__get_element_property(edge, key)

    def set_relationship_property(self, id, key, value):
        edge = self.__get_edge(id)
        self.__set_element_property(edge, key, value)

    def delete_relationship_property(self, id, key):
        edge = self.__get_edge(id)
        self.__delete_element_property(edge, key)

    def get_relationship_properties(self, id):
        edge = self.__get_edge(id)
        return self.__get_element_properties(edge)

    def set_relationship_properties(self, id, properties):
        edge = self.__get_edge(id)
        self.__set_element_properties(edge, properties)

    def update_relationship_properties(self, id, properties):
        edge = self.__get_edge(id)
        self.__update_element_properties(edge, properties)

    def delete_relationship_properties(self, id):
        edge = self.__get_edge(id)
        self.__delete_element_properties(edge)

    def get_relationship_source(self, id, include_properties=False):
        edge = self.__get_edge(id)
        vertex = edge.getOutVertex()
        if include_properties:
            return {vertex.getId(): self.__get_element_properties(vertex)}
        else:
            return {vertex.getId(): None}

    def set_relationship_source(self, relationship_id, node_id):
        v1 = self.__get_vertex(node_id)
        edge = self.__get_edge(relationship_id)
        v2 = edge.getInVertex()
        label = edge.getLabel()
        self.create_relationship(v1.getId(), v2.getId(), label,
                                self.__get_element_properties(edge))
        self.gdb.removeEdge(edge)

    def get_relationship_target(self, id, include_properties=False):
        edge = self.__get_edge(id)
        vertex = edge.getInVertex()
        if include_properties:
            return {vertex.getId(): self.__get_element_properties(vertex)}
        else:
            return {vertex.getId(): None}

    def set_relationship_target(self, relationship_id, node_id):
        v2 = self.__get_vertex(node_id)
        edge = self.__get_edge(relationship_id)
        v1 = edge.getOutVertex()
        label = edge.getLabel()
        self.create_relationship(v1.getId(), v2.getId(), label,
                                self.__get_element_properties(edge))
        self.gdb.removeEdge(edge)

    def delete_relationships(self, ids):
        for _id in ids:
            edge = self.gdb.getEdge(_id)
            self.gdb.removeEdge(edge)

    def get_all_relationships(self, include_properties=False):
        for rel in self.relationship_index.get("graph", self.graph_id):
            if include_properties:
                yield {rel.getId(): \
                        self.get_relationship_properties(rel.getId())}
            else:
                yield rel.getId()

    def get_filtered_relationships(self, **lookups):
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

