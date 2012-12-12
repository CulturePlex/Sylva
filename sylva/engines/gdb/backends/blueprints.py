# -*- coding: utf-8 -*-

from engines.gdb.backends import (BaseGraphDatabase,
                                NodeDoesNotExist,
                                RelationshipDoesNotExist)

VERTEX = "vertex"
EDGE = "edge"


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

    def __set_element_property(self, element, key, value, element_type=None):
        self.__validate_property(key)
        # if value:
        #     if element_type == VERTEX:
        #         self.node_index.put(key, value, element)
        #     elif element_type == EDGE:
        #         self.relationship_index.put(key, value, element)
        element.setProperty(key, value)

    def __delete_element_property(self, element, key, element_type=None):
        self.__validate_property(key)
        self.__check_property(element, key)
        value = element.getProperty(key)
        element.removeProperty(key)
        if value:
            if element_type == VERTEX:
                self.node_index.remove(key, value, element)
            elif element_type == EDGE:
                self.relationship_index.remove(key, value, element)

    def __get_element_properties(self, element):
        return self.__get_public_properties(element)

    def __set_element_properties(self, element, properties, element_type=None):
        for key in properties:
            self.__validate_property(key)
        for key in self.__get_public_keys(element):
            value = element.getProperty(key)
            element.removeProperty(key)
            if value:
                if element_type == VERTEX:
                    self.node_index.remove(key, value, element)
                elif element_type == EDGE:
                    self.relationship_index.remove(key, value, element)
        for key, value in properties.iteritems():
            element.setProperty(key, value)
            # if value:
            #     if element_type == VERTEX:
            #         self.node_index.put(key, value, element)
            #     elif element_type == EDGE:
            #         self.relationship_index.put(key, value, element)

    def __update_element_properties(self, element, properties,
                                    element_type=None):
        for key in properties:
            self.__validate_property(key)
        for key, value in properties.iteritems():
            element.setProperty(key, value)
            # if value:
            #     if element_type == VERTEX:
            #         self.node_index.put(key, value, element)
            #     elif element_type == EDGE:
            #         self.relationship_index.put(key, value, element)

    def __delete_element_properties(self, element, element_type=None):
        for key in self.__get_public_keys(element):
            value = element.getProperty(key)
            element.removeProperty(key)
            if value:
                if element_type == VERTEX:
                    self.node_index.remove(key, value, element)
                elif element_type == EDGE:
                    self.relationship_index.remove(key, value, element)

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
                # -- Not needed indexing properties anymore
                # We don't index null values
                # if value:
                #    self.node_index.put(key, value, vertex)
        #_id and _label is a mandatory internal properties
        if not "_id" in vertex.getPropertyKeys():
            vertex.setProperty("_id", vertex.getId())
        vertex.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        vertex.setProperty("%sgraph" % self.PRIVATE_PREFIX, self.graph_id)
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
        self.__set_element_property(vertex, key, value, element_type=VERTEX)

    def delete_node_property(self, id, key):
        vertex = self.__get_vertex(id)
        self.__delete_element_property(vertex, key, element_type=VERTEX)

    def get_node_properties(self, id):
        vertex = self.__get_vertex(id)
        return self.__get_public_properties(vertex)

    def set_node_properties(self, id, properties):
        vertex = self.__get_vertex(id)
        self.__set_element_properties(vertex, properties, element_type=VERTEX)

    def update_node_properties(self, id, properties):
        vertex = self.__get_vertex(id)
        self.__update_element_properties(vertex, properties,
                                         element_type=VERTEX)

    def delete_node_properties(self, id):
        vertex = self.__get_vertex(id)
        self.__delete_element_properties(vertex, element_type=VERTEX)

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False, label=None):
        vertex = self.__get_vertex(id)
        if not incoming and outgoing:
            edges = vertex.getOutEdges()
        elif incoming and not outgoing:
            edges = vertex.getInEdges()
        else:
            edges = vertex.getBothEdges()
        if include_properties:
            if label:
                return [(e.getId(),
                          self.get_relationship_properties(e.getId()))
                        for e in list(edges)
                        if str(label) == str(e.getLabel())]
            else:
                return [(e.getId(),
                          self.get_relationship_properties(e.getId()))
                        for e in list(edges)]
        else:
            if label:
                return [(e.getId(), None) for e in list(edges)]
            else:
                return [(e.getId(), None)
                        for e in list(edges)
                        if str(label) == str(e.getLabel())]

    def delete_node_relationships(self, id):
        relationships = self.get_node_relationships(id)
        for relationship in relationships:
            self.delete_relationship(relationship)

    def get_nodes_properties(self, ids):
        result = {}
        for _id in ids:
            result[_id] = self.get_node_properties(_id)
        return result

    def delete_nodes(self, ids):
        count = 0
        for _id in ids:
            vertex = self.gdb.getVertex(_id)
            self.gdb.removeVertex(vertex)
            count += 1
        return count

    def __yield_nodes(self, nodes, include_properties):
        for node in nodes:
            if include_properties:
                yield (node.getId(), self.get_node_properties(node.getId()))
            else:
                yield (node.getId(), None)

    def get_all_nodes(self, include_properties=False):
        return self.__yield_nodes(self.node_index.get("graph",
                                                      unicode(self.graph_id)),
                                  include_properties)

    def get_nodes_by_label(self, label, include_properties=False):
        return self.__yield_nodes(self.node_index.get("label", unicode(label)),
                                  include_properties)

    def get_filtered_nodes(self, label=None, include_properties=None, *lookups):
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
            # -- Not needed to index all properties anymore
            #     # We don't index null values
            #     if value:
            #         self.relationship_index.put(key, value, edge)
        #_id and _label is a mandatory internal property
        if not "_id" in edge.getPropertyKeys():
            edge.setProperty("_id", edge.getId())
        edge.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        edge.setProperty("%sgraph" % self.PRIVATE_PREFIX, self.graph_id)
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
        self.__set_element_property(edge, key, value, element_type=EDGE)

    def delete_relationship_property(self, id, key):
        edge = self.__get_edge(id)
        self.__delete_element_property(edge, key, element_type=EDGE)

    def get_relationship_properties(self, id):
        edge = self.__get_edge(id)
        return self.__get_element_properties(edge)

    def set_relationship_properties(self, id, properties):
        edge = self.__get_edge(id)
        self.__set_element_properties(edge, properties, element_type=EDGE)

    def update_relationship_properties(self, id, properties):
        edge = self.__get_edge(id)
        self.__update_element_properties(edge, properties, element_type=EDGE)

    def delete_relationship_properties(self, id):
        edge = self.__get_edge(id)
        self.__delete_element_properties(edge, element_type=EDGE)

    def get_relationship_source(self, id, include_properties=False):
        edge = self.__get_edge(id)
        vertex = edge.getOutVertex()
        if include_properties:
            return (vertex.getId(), self.__get_element_properties(vertex))
        else:
            return (vertex.getId(), None)

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
            return (vertex.getId(), self.__get_element_properties(vertex))
        else:
            return (vertex.getId(), None)

    def set_relationship_target(self, relationship_id, node_id):
        v2 = self.__get_vertex(node_id)
        edge = self.__get_edge(relationship_id)
        v1 = edge.getOutVertex()
        label = edge.getLabel()
        self.create_relationship(v1.getId(), v2.getId(), label,
                                self.__get_element_properties(edge))
        self.gdb.removeEdge(edge)

    def delete_relationships(self, ids):
        count = 0
        for _id in ids:
            if isinstance(_id, (list, tuple)):
                edge = self.gdb.getEdge(_id[0])
            else:
                edge = self.gdb.getEdge(_id)
            self.gdb.removeEdge(edge)
            count += 1
        return count

    def __yield_relationships(self, relationships, include_properties=False):
        for rel in relationships:
            if include_properties:
                yield (rel.getId(), \
                        self.get_relationship_properties(rel.getId()))
            else:
                yield (rel.getId(), None)

    def get_all_relationships(self, include_properties=False):
        return self.__yield_relationships(
                self.relationship_index.get("graph", unicode(self.graph_id)))

    def get_relationships_by_label(self, label, include_properties=False):
        return self.__yield_relationships(
                self.relationship_index.get("label", unicode(label)),
                                            include_properties)

    # Quering

    def query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")
