# -*- coding: utf-8 -*-
from requests.exceptions import ConnectionError
from gremlinrestclient import PyBlueprintsGraphDatabase
from engines.gdb.backends import (GraphDatabaseInitializationError,
                                  GraphDatabaseConnectionError)
from engines.gdb.backends.blueprints import BlueprintsGraphDatabase
from engines.gdb.lookups.tinkergraph import Q as q_lookup_builder


class GraphDatabase(BlueprintsGraphDatabase):

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        self.graph = graph
        if not self.graph:
            raise GraphDatabaseInitializationError("graph parameter required")
        self.graph_id = str(self.graph.id)
        try:
            self.gdb = PyBlueprintsGraphDatabase(self.url)
            self.setup_indexes()
        except ConnectionError:
            raise GraphDatabaseConnectionError(self.url)

    def analysis(self):
        # Maybe this should be added to base...
        return None

    def setup_indexes(self):
        script = """graph.createIndex('_label', Vertex.class);
                    graph.createIndex('_id', Vertex.class);
                    graph.createIndex('_label', Edge.class);
                    graph.createIndex('_id', Edge.class);"""
        self.gdb.execute(script)

    def _delete_element_property(self, element, key, element_type=None):
        self._validate_property(key)
        self._check_property(element, key)
        element.removeProperty(key)

    def _set_element_properties(self, element, properties, element_type=None):
        for key in properties:
            self._validate_property(key)
        for key in self._get_public_keys(element):
            element.removeProperty(key)
        for key, value in properties.iteritems():
            element.setProperty(key, value)

    def _delete_element_properties(self, element, element_type=None):
        for key in self._get_public_keys(element):
            element.removeProperty(key)

    def create_node(self, label, properties=None):
        # Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        vertex = self.gdb.addVertex()
        if type(properties) == dict:
            # Properties starting with _ are not allowed
            for key in properties.keys():
                self._validate_property(key)
            for key, value in properties.iteritems():
                vertex.setProperty(key, value)
        # _id and _label is a mandatory internal properties
        if "_id" not in vertex.getPropertyKeys():
            vertex.setProperty("_id", vertex.getId())
        vertex.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        vertex.setProperty("%sgraph" % self.PRIVATE_PREFIX, self.graph_id)
        return vertex.getId()

    def get_all_nodes(self, include_properties=False):
        return self.get_filtered_nodes({"graph": unicode(self.graph_id)},
                                       include_properties=include_properties)

    def get_nodes_by_label(self, label, include_properties=False, **kwargs):
        return self.get_filtered_nodes({}, label=label,
                                       include_properties=include_properties)

    def create_relationship(self, id1, id2, label, properties=None):
        # Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        v1 = self._get_vertex(id1)
        v2 = self._get_vertex(id2)
        edge = self.gdb.addEdge(v1, v2, label)
        if type(properties) == dict:
            # Properties starting with _ are not allowed
            for key in properties.keys():
                self._validate_property(key)
            for key, value in properties.iteritems():
                edge.setProperty(key, value)
        # _id and _label is a mandatory internal property
        if "_id" not in edge.getPropertyKeys():
            edge.setProperty("_id", edge.getId())
        edge.setProperty("%slabel" % self.PRIVATE_PREFIX, label)
        edge.setProperty("%sgraph" % self.PRIVATE_PREFIX, self.graph_id)
        return edge.getId()

    def get_all_relationships(self, include_properties=False):
        return self.get_filtered_relationships(
            {"_graph": unicode(self.graph_id)},
            include_properties=include_properties)

    def get_relationships_by_label(self, label, include_properties=False):
        return self.get_filtered_relationships(
            {}, label=label,
            include_properties=include_properties)

    def get_filtered_nodes(self, lookups, label=None, include_properties=None,
                           limit=None, offset=None, order_by=None):
        """
        Get an iterator for filtered nodes using the parameters expressed in
        the dictionary lookups.
        The most usual lookups from Django should be implemented.
        """
        if label is not None:
            labels = self._prep_labels(label)
            script = "g.V().or(%s)" % labels
        else:
            script = "g.V()"
        bindings = {}
        if lookups:
            where, bindings = self._prep_lookups(lookups)
            script = "%s.and(%s)" % (script, where)
        resp = self.gdb.execute(script, bindings=bindings)
        if include_properties:
            for v in resp.data:
                props = {k: v[0]["value"] for k, v in v["properties"].items()}
                yield (v["id"], props, v["properties"]["_label"][0]["value"])
        else:
            for v in resp.data:
                yield (v["id"], None, None)

    def get_filtered_relationships(self, lookups, label=None,
                                   include_properties=None, limit=None,
                                   offset=None, order_by=None):
        """
        Get an iterator for filtered relationship using the parameters
        expressed in the dictionary lookups.
        The most usual lookups from Django should be implemented.
        """
        if label is not None:
            labels = self._prep_labels(label)
            script = "g.E().or(%s)" % labels
        else:
            script = "g.E()"
        bindings = {}
        if lookups:
            where, bindings = self._prep_lookups(lookups)
            script = "%s.and(%s)" % (script, where)
        resp = self.gdb.execute(script, bindings=bindings)
        if include_properties:
            for e in resp.data:
                props = e["properties"]
                # Node class in graph/mixins will do this if not here.
                out_v = self.gdb.execute(
                    "g.V(vid)", bindings={"vid": e["outV"]})
                in_v = self.gdb.execute(
                    "g.V(vid)", bindings={"vid": e["inV"]})
                out_v = out_v.data[0]
                in_v = in_v.data[0]
                source = {
                    "id": out_v["id"],
                    "properties": out_v["properties"],
                    "label": out_v["properties"]["_label"]}
                target = {
                    "id": in_v["id"],
                    "properties": in_v["properties"],
                    "label": in_v["properties"]["_label"]}
                yield (
                    e["id"], props, e["properties"]["_label"], source, target)
        else:
            for e in resp.data:
                yield (e["id"], None, None)

    def _prep_labels(self, label):
        has = "has('%s', '%s')"
        labels = []
        if isinstance(label, (list, tuple)):
            label = [has % ('_label', unicode(l)) for l in label
                     if bool(l)]
            labels += label
        elif label:
            label = has % ('_label', unicode(label))
            labels.append(label)
        return ','.join(labels)

    def _prep_lookups(self, lookups):
        wheres = q_lookup_builder()
        for lookup in lookups:
            if isinstance(lookup, q_lookup_builder):
                wheres &= lookup
            elif isinstance(lookup, dict):
                wheres &= q_lookup_builder(**lookup)
        where, bindings = wheres.get_query_objects()
        return where, bindings

    def lookup_builder(self):
        # Should be added to base.
        return q_lookup_builder

    def get_nodes_count(self, label=None):
        """
        Get the number of total nodes.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if label is not None:
            labels = self._prep_labels(label)
            script = "g.V().or(%s).count()" % labels
        else:
            script = """g.V().count()"""
        resp = self.gdb.execute(script)
        count = resp.data[0]
        return count

    def get_node_relationships_count(self, id, incoming=False, outgoing=False,
                                     label=None):
        """
        Get the number of all relationships of a node.
        If "incoming" is True, it only counts the ids for incoming ones.
        If "outgoing" is True, it only counts the ids for outgoing ones.
        If "label" is provided, relationships will be filtered.
        """
        bindings = {"vid": id}
        if label is not None:
            labels = self._prep_labels(label)
            label_script = ".or(%s)" % labels
        else:
            label_script = ""
        if incoming and not outgoing:
            script = "g.V(vid).inE()%s.count()" % label_script
        elif outgoing and not incoming:
            script = "g.V(vid).outE()%s.count()" % label_script
        else:
            script = "g.V(vid).bothE()%s.count()" % label_script
        resp = self.gdb.execute(script, bindings=bindings)
        return resp.data[0]

    def get_relationship_count(self, label=None):
        """
        Get the number of total relationships.
        If "label" is provided, the number is calculated according the
        the label of the element.
        """
        if label is not None:
            labels = self._prep_labels(label)
            script = "g.E().or(%s).count()" % labels
        else:
            script = """g.E().count()"""
        resp = self.gdb.execute(script)
        count = resp.data[0]
        return count

    # Quering
    def query(self, *args, **kwargs):
        # TODO: Define the requirements of the queries.
        """
        XXX
        """
        raise NotImplementedError("Method has to be implemented")

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

    # Deleting the graph

    def destroy(self):
        """
        Delete the entire graph and all the information related: nodes,
        relationships, indices, etc.
        """
        raise NotImplementedError("Method has to be implemented")
