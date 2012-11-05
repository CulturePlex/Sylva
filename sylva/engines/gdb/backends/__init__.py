# -*- coding: utf-8 -*-


class BaseGraphDatabase(object):
    """
    Base class for GraphDatabase with the common API to implement.

    Note 1: Any other method distinct to these ones should be prefixed
            with character '_'.
    Note 2: The implementation of indices shouldn't be exposed to outside from
            this class. The indices must be used internally.
    Note 3: It doesn't allow properties keys startng with '_' defined by
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

    def create_node(self, label, properties=None, type=None):
        """
        Create a node.
        If "properties" is a dictionary, they will be added to the node.
        If "type" is not None, it will be added like a inner property.
        If "label" is a string, the node will be labeled with "label".
        Return the id of the node created and set it to it.
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

    def get_node_type(self, type):
        """
        Get the type of the node "type".
        """
        raise NotImplementedError("Method has to be implemented")

    def set_node_type(self, id, label):
        """
        Set the type of the node "id".
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

    def update_node_properties(self, id, properties):
        """
        Update to "properties" the dictionary of properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_node_properties(self, id):
        """
        Delete all the properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False, label=None):
        """
        Get a list of tuples with all relationships. The first element is "id"
        and the second is None.
        incoming and outgoing.
        If "incoming" is True, it only returns the ids for incoming ones.
        If "outgoing" is True, it only returns the ids for outgoing ones.
        If "include_properties" is True, the value of the second value of the
        tuple is a dictionary containing the properties.
        If "label" is provided, relationships will be filtered.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_node_relationships_count(self, id, incoming=False, outgoing=False,
                                     label=None):
        """
        Get the number of all relationships of a node.
        If "incoming" is True, it only counts the ids for incoming ones.
        If "outgoing" is True, it only counts the ids for outgoing ones.
        If "label" is provided, relationships will be filtered.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_node_relationships(self, id):
        """
        Delete all the relationships of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_nodes_properties(self, ids):
        """
        Get a list of tuples for the nodes with "id" in the list "ids",
        whose first element is the nodes "id" and the second one is a
        dictionary containing the properties.
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_nodes(self, ids):
        """
        Delete all the nodes whose "id" is on the list "ids".
        Return the number of elements removed. Useful when "ids" is an iterator
        """
        raise NotImplementedError("Method has to be implemented")

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_all_nodes(self, include_properties=False):
        """
        Get an iterator for the list of tuples of all nodes, the first element
        is the id of the node.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_filtered_nodes(self, lookups, label=None, include_properties=None):
        """
        Get an iterator for filtered nodes using the parameters expressed in
        the dictionary lookups.
        The most usual lookups from Django should be implemented.
        More info: https://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups
        """
        raise NotImplementedError("Method has to be implemented")

    # Relationships methdos

    def create_relationship(self, id1, id2, label, properties=None, type=None):
        """
        Create a relationship from node "id1" to node "id2".
        If "label" is a string, the relationship will be labeled with "label".
        If "type" is not None, it will be added like a inner property.
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

    def get_relationship_type(self, type):
        """
        Get the type of the relationship "type".
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_type(self, id, type):
        """
        Set the type of the relationship "type".
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

    def update_relationship_properties(self, id, properties):
        """
        Update to "properties" the dictionary of properties of the node "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def delete_relationship_properties(self, id):
        """
        Delete all the properties of the relationship "id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_source(self, id, include_properties=False):
        """
        Get the tuple of the relationship "id". The first element will be the
        source node "id" and the second one will be a dictionary containing
        the properties of the node.
        """
        raise NotImplementedError("Method has to be implemented")

    def set_relationship_source(self, relationship_id, node_id):
        """
        Set the source node of the relationship "relationship_id".
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_target(self, id, include_properties=False):
        """
        Get the tuple of the relationship "id". The first element will be the
        target node "id" and the second one will be a dictionary containing
        the properties of the node.
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
        Return the number of elements removed. Useful when "ids" is an iterator
        """
        raise NotImplementedError("Method has to be implemented")

    def get_relationship_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        raise NotImplementedError("Method has to be implemented")

    def get_all_relationship(self, include_properties=False):
        """
        Get an iterator for the list of tuples of all relationships, the
        first element is the id of the node.
        If "include_properties" is True, the second element in the tuple
        will be a dictionary containing the properties.
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

    def nodes_query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")

    def relationships_query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")

    def query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")

    def lookup_builder(self):
        """
        Get a constructor for Q objects in order to make lookups in filters
        """
        raise NotImplementedError("Method has to be implemented")

    # Deleting the graph

    def delete(self):
        """
        Delete the entire graph and all the information related: nodes,
        relationships, indices, etc.
        """
        raise NotImplementedError("Method has to be implemented")


class GraphDatabaseError(Exception):
    pass


class GraphDatabaseInitializationError(GraphDatabaseError):
    pass


class GraphDatabaseConnectionError(GraphDatabaseError):

    def __init__(self, url, *args, **kwargs):
        self.url = url

    def __str__(self):
        return "Unable to connect to \"%s\"" % repr(self.url)


class ObjectDoesNotExist(GraphDatabaseError):

    def __init__(self, object_id, *args, **kwargs):
        self.id = object_id

    def __str__(self):
        return "Object with identifier \"%s\" doesn't exist" % repr(self.id)


class NodeDoesNotExist(ObjectDoesNotExist):

    def __str__(self):
        return "Node \"%s\" doesn't exist" % repr(self.id)


class RelationshipDoesNotExist(ObjectDoesNotExist):

    def __str__(self):
        return "Relationship \"%s\" doesn't exist" % repr(self.id)
