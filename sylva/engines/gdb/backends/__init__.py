# -*- coding: utf-8 -*-
import datetime


class BaseGraphDatabase(object):
    """
    Base class for GraphDatabase with the common API to implement.

    Note 1: Any other method distinct to these ones should be prefixed
            with character '_'.
    Note 2: The implementation of indices shouldn't be exposed to outside from
            this class. The indices must be used internally.
    Note 3: It doesn't allow properties keys startng with "__" defined by
            users, because they are reserved to implementations details.
            So all dictionaries of properties must be cleaned after and before
            of being returned, updated and sent.
    """

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        self.graph = graph
        raise NotImplementedError("Indices must be set up")

    # Nodes methdos

    def create_node(self, label, properties=None):
        """
        Create a node.
        If "properties" is a dictionary, they will be added to the node.
        If "label" is a string, the node will be labeled with "label".
        Return the id of the node created.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_node(self, id):
        """
        Delete the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_label(self, id):
        """
        Get the label of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_property(self, id, key):
        """
        Get the property identified by "key" of the node "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def set_node_property(self, id, key, value):
        """
        Set to "value" the property identified by "key" of the node "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_node_property(self, id, key):
        """
        Delete the property identified by "key" of the node "id".
        Raise KeyError if "key" is not present.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_properties(self, id):
        """
        Get the dictionary of properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def set_node_properties(self, id, properties):
        """
        Set to "properties" the dictionary of properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_node_properties(self, id):
        """
        Delete all the properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False):
        """
        Get the list of all relationships ids related with the node "id",
        incoming and outgoing.
        If "incoming" is True, it only returns the ids for incoming ones.
        If "outgoing" is True, it only returns the ids for outgoing ones.
        If "include_properties" is True, each element in the list will be a
        dictionary with two keys: "id", containing the id of the relationship,
        and "properties", containing a dictionary with the properties.
        """

    def get_all_nodes(self):
        """
        Get an iterator for all nodes.
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
        It returns the id of the relationship created.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationship(self, id):
        """
        Delete the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_label(self, id):
        """
        Get the label of the relationship "id".
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
        """
        Get the dictionary of properties of the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

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

    def get_relationship_nodes(self, id, include_properties=False):
        """
        Get the list of all nodes ids implied in some relationship. Each
        element in the list is a dictionary with three keys: "source" with the id
        of the start node, "target" with the id of the end node, and "label"
        with the type of the relationship.
        If "include_properties" is True, a new key "properties" is added to the
        returned dictionaries, containing a dictionary with the properties of
        the relationship.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_all_relationship(self):
        """
        Get an iterator for all relationship.
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


class BlueprintsGraphDatabase(BaseGraphDatabase):

    def create_node(self, properties):
        # index = self.gdb.getIndex('all_nodes', 'VERTICES')
        # Create node and set properties
        node = self.gdb.addVertex()
        for key, value in properties.iteritems():
            node.setProperty(key, value)
        # Index node
        # TODO index.put('key1', properties['key1'], node)
        return node

    def element_exists(self, index, key, value):
        return index.count(key, value)

    def search_in_index(self, index, key, value):
        return index.get(key, value)

    def filter_by_property(self, nodes, prop, value):
        return [n for n in nodes if n.getProperty(prop) == value]

    def get_timestamp(self):
        timestamp = datetime.datetime.now()
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def update_timestamp(self, element, username):
        element.setProperty('_timestamp', self.get_timestamp())
        element.setProperty('_user', username)

    def create_relationship(self, node1, node2, label, properties):
        index = self.gdb.getIndex('all_relationships', 'EDGES')
        edge_str = "%s:%s:%s" % (node1.getId(),
                                label,
                                node2.getId())
        properties['edge_str'] = edge_str
        # Avoid creating duplicated edges
        if self.element_exists(index, properties):
            return None
        edge = self.gdb.addEdge(None, node1, node2, label)
        for key, value in properties.iteritems():
            edge.setProperty(key, value)
        #Index edge
        index.put('edge_str', edge_str, edge)
        return edge
