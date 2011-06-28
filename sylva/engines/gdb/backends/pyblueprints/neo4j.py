#!/usr/bin/env python
#-*- coding:utf-8 -*-

#####################################################################
# A set of classes implementing Blueprints API for Neo4j engine.    #
#                                                                   #
# The CulturePlex Laboratory                                        #
# The University of Western Ontario                                 #
#                                                                   #
# Diego Muñoz Escalante (escalant3 at gmail dot com)                #
# Javier de la Rosa (versae at gmail dot com)                       #
#                                                                   #
# File: pyblueprints/neo4j.py                                       #
#####################################################################

import neo4jrestclient
from base import Graph


class Neo4jGraph(Graph):

    def __init__(self, host):
        self.neograph = neo4jrestclient.GraphDatabase(host)

    def addVertex(self, _id=None):
        """Add param declared for compability with the API. Neo4j
        creates the id automatically
        @params _id: Node unique identifier

        @returns The created Vertex or None"""
        node = self.neograph.nodes.create(_id=_id)
        return Vertex(node)

    def getVertex(self, _id):
        """Retrieves an existing vertex from the graph
        @params _id: Node unique identifier

        @returns The requested Vertex or None"""
        node = self.neograph.nodes.get(_id)
        return Vertex(node)

    def getVertices(self):
        """Returns an iterator with all the vertices"""
        raise NotImplementedError("Method has to be implemented")

    def removeVertex(self, vertex):
        """Removes the given vertex
        @params vertex: Node to be removed"""
        vertex.neoelement.delete()

    def addEdge(self, _id, outVertex, inVertex, label):
        """Creates a new edge
        @params _id: Edge unique identifier
        @params outVertex: Edge origin Vertex
        @params inVertex: Edge target vertex
        @params label: Edge label

        @returns The created Edge object"""
        n1 = outVertex.neoelement
        n2 = inVertex.neoelement
        edge = n1.relationships.create(label, n2)
        return Edge(edge)

    def getEdges(self):
        """Returns an iterator with all the vertices"""
        raise NotImplementedError("Method has to be implemented")

    def removeEdge(self, edge):
        """Removes the given edge
        @params edge: The edge to be removed"""
        edge.neoelement.delete()

    def clear(self):
        """Removes all data in the graph database"""
        raise NotImplementedError("Method has to be implemented")

    def shutdown(self):
        """Shuts down the graph database server"""
        raise NotImplementedError("Method has to be implemented")


class Element():
    """An class defining an Element object composed
    by a collection of key/value properties for the
    Neo4j database"""

    def __init__(self, neoelement):
        """Constructor
        @params neolement: The Neo4j element to be transformed"""
        self.neoelement = neoelement

    def getProperty(self, key):
        """Gets the value of the property for the given key
        @params key: The key which value is being retrieved

        @returns The value of the property with the given key"""
        return self.neoelement.get(key)

    def getPropertyKeys(self):
        """Returns a set with the property keys of the element

        @returns Set of property keys"""
        return set(self.neoelement.properties.keys())

    def setProperty(self, key, value):
        """Sets the property of the element to the given value
        @params key: The property key to set
        @params value: The value to set"""
        self.neoelement.set(key, value)

    def getId(self):
        """Returns the unique identifier of the element

        @returns The unique identifier of the element"""
        return self.neoelement.id


class Vertex(Element):
    """An abstract class defining a Vertex object representing
    a node of the graph with a set of properties"""

    def getOutEdges(self, label=None):
        """Gets all the outgoing edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A generator function with the outgoing edges"""
        if label:
            for edge in self.neoelement.relationships.outgoing(types=[label]):
                yield Edge(edge)
        else:
            for edge in self.neoelement.relationships.outgoing():
                yield Edge(edge)

    def getInEdges(self, label=None):
        """Gets all the incoming edges of the node. If label
        parameter is provided, it only returns the edges of
        the given label
        @params label: Optional parameter to filter the edges

        @returns A generator function with the incoming edges"""
        if label:
            for edge in self.neoelement.relationships.incoming(types=[label]):
                yield Edge(edge)
        else:
            for edge in self.neoelement.relationships.incoming():
                yield Edge(edge)

    def __str__(self):
        return "Vertex %s: %s" % (self.neoelement.id,
                                self.neoelement.properties)


class Edge(Element):
    """An abstract class defining a Edge object representing
    a relationship of the graph with a set of properties"""

    def getOutVertex(self):
        """Returns the origin Vertex of the relationship

        @returns The origin Vertex"""
        return Vertex(self.neoelement.start)

    def getInVertex(self):
        """Returns the target Vertex of the relationship

        @returns The target Vertex"""
        return Vertex(self.neoelement.end)

    def getLabel(self):
        """Returns the label of the relationship

        @returns The edge label"""
        return self.neoelement.type

    def __str__(self):
        return "Edge %s: %s" % (self.neoelement.id,
                                self.neoelement.properties)


class Index():
    """An class containing all the methods needed by an
    Index object"""

    def __init__(self, indexName, indexClass, indexType, indexObject):
        if indexClass != "VERTICES" and indexClass != "EDGES":
            raise NameError("%s is not a valid Index Class" % indexClass)
        self.indexClass = indexClass
        self.indexName = indexName
        if indexType != "AUTOMATIC" and indexType != "MANUAL":
            raise NameError("%s is not a valid Index Type" % indexType)
        self.indexType = indexType
        if not isinstance(indexObject, neo4jrestclient.client.Index):
            raise TypeError("""%s is not a valid
                            neo4jrestclient.client.Index
                            instance""" \
                            % type(indexObject))
        self.neoindex = indexObject

    def count(self, key, value):
        """Returns the number of elements indexed for a
        given key-value pair
        @params key: Index key string
        @params outVertex: Index value string

        @returns The number of elements indexed"""
        return len(self.neoindex[key][value])

    def getIndexName(self):
        """Returns the name of the index

        @returns The name of the index"""
        return self.indexName

    def getIndexClass(self):
        """Returns the index class (VERTICES or EDGES)

        @returns The index class"""
        return self.indexClass

    def getIndexType(self):
        """Returns the index type (AUTOMATIC or MANUAL)

        @returns The index type"""
        return self.indexType

    def put(self, key, value, element):
        """Puts an element in an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @params element: Vertex or Edge element to be indexed"""
        self.neoindex[key][value] = element.neoelement

    def get(self, key, value):
        """Gets an element from an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @returns A generator of Vertex or Edge objects"""
        for element in self.neoindex[key][value]:
            if self.indexClass == "VERTICES":
                yield Vertex(element)
            else:
                yield Edge(element)

    def remove(self, key, value, element):
        """Removes an element from an index under a given
        key-value pair
        @params key: Index key string
        @params value: Index value string
        @params element: Vertex or Edge element to be removed"""
        self.neoindex.delete(key, value, element.neoelement)

    def __str__(self):
        return "Index: %s (%s, %s)" % (self.indexName,
                                        self.indexClass,
                                        self.indexType)


class Neo4jIndexableGraph(Neo4jGraph):
    """An class containing the specific methods
    for indexable graphs"""

    def createManualIndex(self, indexName, indexClass):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")

    def createAutomaticIndex(self, name, indexClass):
        """Creates an index automatically managed my Neo4j
        @params name: The index name
        @params indexClass: VERTICES or EDGES

        @returns The created Index"""
        if indexClass == "VERTICES":
            index = self.neograph.nodes.indexes.create(name)
        elif indexClass == "EDGES":
            index = self.neograph.relationships.indexes.create(name)
        else:
            NameError("Unknown Index Class %s" % indexClass)
        return Index(name, indexClass, "AUTOMATIC", index)

    def getIndex(self, indexName, indexClass):
        """Retrieves an index with a given index name and class
        @params indexName: The index name
        @params indexClass: VERTICES or EDGES

        @return The Index object"""
        if indexClass == "VERTICES":
            try:
                return Index(indexName, indexClass, "AUTOMATIC",
                        self.neograph.nodes.indexes.get(indexName))
            except neo4jrestclient.request.NotFoundError:
                raise KeyError("VERTICES index %s not found" % indexName)
        elif indexClass == "EDGES":
            try:
                return Index(indexName, indexClass, "AUTOMATIC",
                        self.neograph.relationships.indexes.get(indexName))
            except neo4jrestclient.request.NotFoundError:
                raise KeyError("EDGES index %s not found" % indexName)
        else:
            raise KeyError("Unknown Index Class (%s). Use VERTICES or EDGES"\
                    % indexClass)

    def getIndices(self):
        """Returns a generator function over all the existing indexes

        @returns A generator function over all rhe Index objects"""
        for indexName in self.neograph.nodes.indexes.keys():
            indexObject = self.neograph.nodes.indexes.get(indexName)
            yield Index(indexName, "VERTICES", "AUTOMATIC", indexObject)
        for indexName in self.neograph.relationships.indexes.keys():
            indexObject = self.neograph.relationships.indexes.get(indexName)
            yield Index(indexName, "EDGES", "AUTOMATIC", indexObject)

    def dropIndex(self, indexName):
        """TODO Documentation"""
        raise NotImplementedError("Method has to be implemented")


if __name__ == "__main__":
    #Creates the object
    g = Neo4jIndexableGraph('http://localhost:7474/db/data')
    #Adds a vertex
    v1 = g.addVertex()
    #Sets, gets and prints Vertex
    v1.setProperty('myProp1', 'myValue1')
    print v1.getPropertyKeys()
    print v1.getProperty('myProp1')
    print v1
    vertexId = v1.getId()
    print vertexId
    #Create another vertex and add an Edge
    v2 = g.addVertex()
    v2.setProperty('myProp2', 'myValue2')
    e = g.addEdge(None, v1, v2, 'anEdgeLabel')
    #Sets, gets and prints Edge
    e.setProperty('myEdgeProp', 'myEdgeValue')
    print e.getPropertyKeys()
    print e.getProperty('myEdgeProp')
    print e.getInVertex()
    print e.getOutVertex()
    print "In edges:"
    for edge in v2.getInEdges():
        print edge
    print "Out edges:"
    for edge in v2.getOutEdges():
        print edge
    #Indexes
    i1 = g.createAutomaticIndex('testIndex', 'VERTICES')
    i2 = g.createAutomaticIndex('testIndex2', 'EDGES')
    for index in g.getIndices():
        print index
    i1 = g.getIndex('testIndex', "VERTICES")
    print i1.getIndexName()
    print i1.getIndexClass()
    print i1.getIndexType()
    i1.put('key1', 'value1', v1)
    i1.put('key1', 'value1', v2)
    print i1.count('key1', 'value1')
    for element in i1.get('key1', 'value1'):
        print element
    i1.remove('key1', 'value1', v1)
    print i1.count('key1', 'value1')
    g.removeEdge(e)
    v = g.getVertex(vertexId)
    g.removeVertex(v1)
