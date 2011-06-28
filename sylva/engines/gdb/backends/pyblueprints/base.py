#!/usr/bin/env python
#-*- coding:utf-8 -*-

#####################################################################
# A set of abstract classes to export the Blueprints API from       #
# TinkerPop to Python                                               #
#                                                                   #
# https://github.com/tinkerpop/blueprints/wiki/Property-Graph-Model #
#                                                                   #
# The CulturePlex Laboratory                                        #
# The University of Western Ontario                                 #
#                                                                   #
# Diego Muñoz Escalante (escalant3 at gmail dot com)                #
# Javier de la Rosa (versae at gmail dot com)                       #
#                                                                   #
# File: pyblueprints/base.py                                        #
#####################################################################


class Graph():
    """This is an abstract class that specifies all the
    methods that should be reimplemented in order to
    follow a Blueprints-like API in python"""

    def addVertex(self, _id):
        """Adds a new vertex to the graph
        @params _id: Node unique identifier

        @returns The created Vertex or None"""
        raise NotImplementedError("Method has to be implemented")

    def getVertex(self, _id):
        """Retrieves an existing vertex from the graph
        @params _id: Node unique identifier

        @returns The requested Vertex or None"""
        raise NotImplementedError("Method has to be implemented")

    def getVertices(self):
        """Returns an iterator with all the vertices"""
        raise NotImplementedError("Method has to be implemented")

    def removeVertex(self, vertex):
        """Removes the given vertex
        @params vertex: Node to be removed"""
        raise NotImplementedError("Method has to be implemented")

    def addEdge(self, _id, outVertex, inVertex, label):
        """Creates a new edge
        @params _id: Edge unique identifier
        @params outVertex: Edge origin Vertex
        @params inVertex: Edge target vertex
        @params label: Edge label

        @returns The created Edge object"""
        raise NotImplementedError("Method has to be implemented")

    def getEdges(self):
        """Returns an iterator with all the vertices"""
        raise NotImplementedError("Method has to be implemented")

    def removeEdge(self, edge):
        """Removes the given edge
        @params edge: The edge to be removed"""
        raise NotImplementedError("Method has to be implemented")

    def clear(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def shutdown(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")


class TransactionalGraph(Graph):
    """An abstract class containing the specific methods
    for transacional graphs"""

    def startTransaction(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def stopTransaction(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def setTransactionMode(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def getTransactionMode(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")


class IndexableGraph(Graph):
    """An abstract class containing the specific methods
    for indexable graphs"""

    def createManualIndex(self, indexName, indexClass):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def createAutomaticIndex(self, name, indexClass):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def getIndex(self, indexName, indexClass):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def getIndices(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def dropIndex(self, indexName):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")


class Element():
    """An abstract class defining an Element object composed
    by a collection of key/value properties"""

    def getProperty(self, key):
        """Gets the value of the property for the given key
        @params key: The key which value is being retrieved

        @returns The value of the property with the given key"""
        raise NotImplementedError("Method has to be implemented")

    def getPropertyKeys(self):
        """Returns a set with the property keys of the element

        @returns Set of property keys"""
        raise NotImplementedError("Method has to be implemented")

    def setProperty(self, key, value):
        """Sets the property of the element to the given value
        @params key: The property key to set
        @params value: The value to set"""
        raise NotImplementedError("Method has to be implemented")

    def getId(self):
        """Returns the unique identifier of the element

        @returns The unique identifier of the element"""
        raise NotImplementedError("Method has to be implemented")


class Vertex(Element):
    """An abstract class defining a Vertex object representing
    a node of the graph with a set of properties"""

    def getOutEdges(self, label=None):
        """Gets all the outgoing edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A list of edges"""
        raise NotImplementedError("Method has to be implemented")

    def getInEdges(self, label=None):
        """Gets all the incoming edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A list of edges"""
        raise NotImplementedError("Method has to be implemented")


class Edge(Element):
    """An abstract class defining a Edge object representing
    a relationship of the graph with a set of properties"""

    def getOutVertex(self):
        """Returns the origin Vertex of the relationship

        @returns The origin Vertex"""
        raise NotImplementedError("Method has to be implemented")

    def getInVertex(self):
        """Returns the target Vertex of the relationship

        @returns The target Vertex"""
        raise NotImplementedError("Method has to be implemented")

    def getLabel(self):
        """Returns the label of the relationship

        @returns The edge label"""
        raise NotImplementedError("Method has to be implemented")


class Index():
    """An abstract class containing all the methods needed to
    implement an Index object"""

    def count(self, key, value):
        raise NotImplementedError("Method has to be implemented")

    def getIndexName(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def getIndexClass(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def getIndexType(self):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def put(self, key, value, element):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def get(self, key, value):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def remove(self, key, value, element):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")


class AutomaticIndex(Index):
    """An abstract class containing the specific methods for an
    automatic index"""

    def getAutoIndexKeys(self):
        raise NotImplementedError("Method has to be implemented")
