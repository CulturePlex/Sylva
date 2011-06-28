# -*- coding: utf-8 -*-
import datetime


class BaseGraphDatabase(object):

    def __init__(self, url):
        self.url = url


class BlueprintsGraphDatabase(BaseGraphDatabase):

    def create_node(self, properties):
        node_properties = {}
        #TODO Default properties
        for key, value in properties.items():
            node_properties[key] = value
        # index = self.gdb.getIndex('all_nodes', 'VERTICES')
        # Create node and set properties
        node = self.gdb.addVertex()
        for key, value in node_properties.iteritems():
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
