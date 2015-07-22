# -*- coding: utf-8 -*-
from requests.exceptions import ConnectionError
from gremlinrestclient import TitanGraph, Vertex, GremlinServerError
from engines.gdb.backends import (BaseGraphDatabase, NodeDoesNotExist,
                                  RelationshipDoesNotExist,
                                  GraphDatabaseInitializationError,
                                  GraphDatabaseConnectionError)
from engines.gdb.lookups.titan import Q as q_lookup_builder


class GraphDatabase(BaseGraphDatabase):

    PRIVATE_PREFIX = '_'

    def __init__(self, url, params=None, graph=None):
        self.url = url
        self.params = params or {}
        self.graph = graph
        if not self.graph:
            raise GraphDatabaseInitializationError("graph parameter required")
        self.graph_id = str(self.graph.id)
        self.gdb = TitanGraph(self.url)
        try:
            self.build_schema_indices()
        except ConnectionError:
            raise GraphDatabaseConnectionError(self.url)
        except GremlinServerError:
            # Titan throws error on schema/index redef.
            pass

    def analysis(self):
        return None

    def build_schema_indices(self):
        script = """mgmt = graph.openManagement()
                    rels = mgmt.makeEdgeLabel('RELS').multiplicity(MULTI).make()
                    _id = mgmt.makePropertyKey('_id').dataType(Object.class).cardinality(Cardinality.SINGLE).make()
                    _label = mgmt.makePropertyKey('_label').dataType(String.class).cardinality(Cardinality.SINGLE).make()
                    _graph = mgmt.makePropertyKey('_graph').dataType(String.class).cardinality(Cardinality.SINGLE).make()
                    mgmt.buildIndex('_vid', Vertex.class).addKey(_id).buildCompositeIndex()
                    mgmt.buildIndex('_eid', Edge.class).addKey(_id).buildCompositeIndex()
                    mgmt.buildIndex('_vlabel', Vertex.class).addKey(_label).buildCompositeIndex()
                    mgmt.buildIndex('_elabel', Edge.class).addKey(_label).buildCompositeIndex()
                    mgmt.buildIndex('_vgraph', Vertex.class).addKey(_graph).buildCompositeIndex()
                    mgmt.buildIndex('_egraph', Edge.class).addKey(_graph).buildCompositeIndex()
                    mgmt.commit()"""
        self.gdb.execute(script)
        print("SUCCESSFULLY CREATED TITAN SCHEMA/INDICES")

    def get_all_nodes(self, include_properties=False):
        return self.get_filtered_nodes({"graph": unicode(self.graph_id)},
                                       include_properties=include_properties)

    def get_nodes_by_label(self, label, include_properties=False, **kwargs):
        return self.get_filtered_nodes({}, label=label,
                                       include_properties=include_properties)

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

    def create_node(self, label, properties=None):
        # Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        if properties is None:
            properties = {}
        # Properties starting with _ are not allowed
        for key in properties.keys():
            self._validate_property(key)
        # _id and _label is a mandatory internal properties
        coll = self.gdb.create(properties)
        vertex, = coll.vertices
        vid = vertex.id
        props = {}
        if "_id" not in vertex.properties.keys():
            props["_id"] = vid
        props["%slabel" % self.PRIVATE_PREFIX] = label
        props["%sgraph" % self.PRIVATE_PREFIX] = self.graph_id
        self._set_elem_properties(vid, props, "V", NodeDoesNotExist)
        return vid

    def create_relationship(self, id1, id2, label, properties=None):
        # Label must be a string
        if not label or not isinstance(label, basestring):
            raise TypeError("label must be a string")
        if properties is None:
            properties = {}
        v1 = Vertex(id1, None, {})
        v2 = Vertex(id2, None, {})
        for key in properties.keys():
                self._validate_property(key)
        # _id and _label is a mandatory internal property
        coll = self.gdb.create((v1, "RELS", v2, properties))
        edge, = coll.edges
        eid = edge.id
        props = {}
        if "_id" not in edge.properties.keys():
            props["_id"] = eid
        props["%slabel" % self.PRIVATE_PREFIX] = label
        props["%sgraph" % self.PRIVATE_PREFIX] = self.graph_id
        self._set_elem_properties(eid, props, "E", RelationshipDoesNotExist)
        return eid

    def _validate_property(self, key):
        if key.startswith(self.PRIVATE_PREFIX):
            raise ValueError("%s: Keys starting with %s \
                              are not allowed" % (key, self.PRIVATE_PREFIX))

    def _set_elem_properties(self, eid, properties, traversal_source, error):
        param_id = 0
        bindings = {}
        script = "e = g.%s(eid).next();" % traversal_source
        for k, v in properties.items():
            param = "p%s" % str(param_id)
            script += "e.property('%s', %s);" % (k, param)
            bindings[param] = v
            param_id += 1
        bindings.update({"eid": eid})
        script += "graph.tx().commit();"
        try:
            self.gdb.execute(script, bindings=bindings)
        except GremlinServerError:
            raise error(eid)

    def get_relationships_count(self, label=None):
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
        script = "g.V().each{it.remove()};graph.tx().commit();"
        self.gdb.execute(script)

    def delete_node(self, vid):
        self._delete_elem(vid, "V", NodeDoesNotExist)

    def delete_relationship(self, eid):
        self._delete_elem(eid, "E", RelationshipDoesNotExist)

    def _delete_elem(self, eid, traversal_source, error):
        script = """e = g.%s(eid).next();e.remove();
                    graph.tx().commit();""" % traversal_source
        try:
            self.gdb.execute(script, bindings={"eid": eid})
        except GremlinServerError:
            raise error(eid)

    def get_node_label(self, vid):
        return self.get_node_property(vid, "%slabel" % self.PRIVATE_PREFIX)

    def get_relationship_label(self, eid):
        return self.get_relationship_property(
            eid, "%slabel" % self.PRIVATE_PREFIX)

    def get_node_property(self, vid, key):
        return self._get_property(vid, key, "V", NodeDoesNotExist)

    def get_relationship_property(self, eid, key):
        return self._get_property(eid, key, "E", RelationshipDoesNotExist)

    def _get_property(self, eid, key, traversal_source, error):
        script = """e = g.%s(eid).next();
                    e.property('%s');""" % (traversal_source, key)
        try:
            resp = self.gdb.execute(script, bindings={"eid": eid})
        except GremlinServerError:
            # This error may also mean that the key doesn't exist...
            raise error(eid)
        prop = resp.data[0]["value"]
        return prop

    def set_node_property(self, vid, key, value):
        self._set_elem_properties(vid, {key: value}, "V", NodeDoesNotExist)

    def set_relationship_property(self, eid, key, value):
        self._set_elem_properties(
            eid, {key: value}, "E", RelationshipDoesNotExist)

    def set_node_label(self, vid, label):
        self._set_elem_properties(
            vid, {"_label": label}, "V", NodeDoesNotExist)

    def set_relationship_label(self, eid, label):
        self._set_elem_properties(
            eid, {"_label": label}, "E", RelationshipDoesNotExist)

    def delete_node_property(self, vid, key):
        self._delete_property(vid, key, "V", NodeDoesNotExist)

    def delete_relationship_property(self, eid, key):
        self._delete_property(eid, key, "E", RelationshipDoesNotExist)

    def _delete_property(self, eid, key, traversal_source, error):
        script = """e = g.%s(eid).next();
                    e.property('%s').remove();
                    graph.tx().commit();""" % (traversal_source, key)
        try:
            self.gdb.execute(script, bindings={"eid": eid})
        except GremlinServerError:
            raise error(eid)

    def get_node_properties(self, vid):
        script = "g.V(vid)"
        resp = self.gdb.execute(script, bindings={"vid": vid})
        try:
            properties = resp.data[0]["properties"]
        except IndexError:
            raise NodeDoesNotExist(vid)
        properties = {k: v[0]["value"] for k, v in properties.items()}
        return properties

    def get_relationship_properties(self, eid):
        script = "e = g.E(eid);"
        resp = self.gdb.execute(script, bindings={"eid": eid})
        try:
            props = resp.data[0]["properties"]
        except IndexError:
            raise RelationshipDoesNotExist(eid)
        return props

    def set_node_properties(self, vid, properties):
        self._set_elem_properties(vid, properties, "V", NodeDoesNotExist)

    def set_relationship_properties(self, eid, properties):
        self._set_elem_properties(
            eid, properties, "E", RelationshipDoesNotExist)

    def update_node_properties(self, vid, properties):
        self._set_elem_properties(vid, properties, "V", NodeDoesNotExist)

    def update_relationship_properties(self, eid, properties):
        self._set_elem_properties(
            eid, properties, "E", RelationshipDoesNotExist)

    def delete_node_properties(self, vid):
        script = """v = g.V(vid).next();
                    v.properties().each{
                        it -> v.property(it['label']).remove()};
                    graph.tx().commit();"""
        try:
            self.gdb.execute(script, bindings={"vid": vid})
        except GremlinServerError:
            raise NodeDoesNotExist(vid)

    def delete_relationship_properties(self, eid):
        script = """e = g.E(eid).next();
                    e.properties().each{
                        it -> e.property(it['label']).remove()};
                    graph.tx().commit();"""
        try:
            self.gdb.execute(script, bindings={"eid": eid})
        except GremlinServerError:
            raise NodeDoesNotExist(eid)

    def get_node_relationships(self, vid, incoming=False, outgoing=False,
                               include_properties=False, label=None):
        """
        Kind of a weird function
        """
        script = "g.V(vid)"
        if not incoming and outgoing:
            script += ".outE()"
        elif incoming and not outgoing:
            script += ".inE()"
        else:
            script += ".bothE()"
        try:
            resp = self.gdb.execute(script, bindings={"vid": vid})
        except GremlinServerError:
            raise NodeDoesNotExist(vid)
        edges = resp.data
        if include_properties:
            if isinstance(label, (list, tuple)):
                if label:
                    return [(e["id"], e["properties"]) for e in edges
                            if str(e["properties"]["_label"]) in [str(label_id)
                            for label_id in label]]
                else:
                    # Idk about this behaviour
                    return ()
            else:
                if label:
                    return [(e["id"], e["properties"]) for e in edges
                            if str(label) == str(e["properties"]["_label"])]
                else:
                    return [(e["id"], e["properties"]) for e in edges]
        else:
            if isinstance(label, (list, tuple)):
                if label:
                    return [(e["id"], None) for e in edges
                            if str(e["properties"]["_label"]) in [str(label_id)
                            for label_id in label]]
                else:
                    return ()
            else:
                if label:
                    return [(e["id"], None) for e in edges
                            if str(label) == str(e["properties"]["_label"])]
                else:
                    return [(e["id"], None) for e in edges]

    def delete_node_relationships(self, vid):
        script = "rels = g.V(vid).bothE();rels.each{it -> it.remove()}"
        try:
            self.gdb.execute(script, bindings={"vid": vid})
        except GremlinServerError:
            raise NodeDoesNotExist(vid)

    def get_nodes_properties(self, vids):
        script = "g.V(vids)"
        try:
            resp = self.gdb.execute(script, bindings={"vids": ','.join(vids)})
        except GremlinServerError:
            raise NodeDoesNotExist(','.join(vids))
        output = []
        for vertex in resp.data:
            props = {k: v[0]["value"] for k, v in vertex["properties"].items()}
            output.append((vertex["id"], props))
        return output

    def delete_nodes(self, vids):
        self._delete_elems(vids, "V", NodeDoesNotExist)
        return len(vids)

    def delete_relationships(self, eids):
        self._delete_elems(eids, "E", RelationshipDoesNotExist)

    def _delete_elems(self, eids, traversal_source, error):
        script = """nodes = g.%s(eids);
                    nodes.each{it -> it.remove()};
                    graph.tx().commit();""" % traversal_source
        try:
            self.gdb.execute(
                script,
                bindings={"eids": ','.join(str(e) for e in eids)})
        except GremlinServerError:
            raise error(','.join(eids))

    def get_relationship_source(self, eid, include_properties=False):
        return self._get_source_target(eid, "outV", include_properties)

    def get_relationship_target(self, eid, include_properties=False):
        return self._get_source_target(eid, "inV", include_properties)

    def _get_source_target(self, eid, func, include_properties=False):
        script = """e = g.E(eid);e.%s();""" % func
        try:
            resp = self.gdb.execute(script, bindings={"eid": eid})
        except GremlinServerError:
            raise RelationshipDoesNotExist(eid)
        if include_properties:
            props = {k: v[0]["value"] for k, v
                     in resp.data[0]["properties"].items()}
        else:
            props = None
        return resp.data[0]["id"], props

    def set_relationship_source(self, eid, vid):
        self._set_source_target(eid, vid, self.get_relationship_target)

    def set_relationship_target(self, eid, vid):
        self._set_source_target(eid, vid, self.get_relationship_source)

    def _set_source_target(self, eid, vid, func):
        # TODO: refactor to gremlin
        source, props = func(eid, include_properties=True)
        label = props.pop("_label")
        props = {k: v for k, v in props.items()
                 if not k.startswith(self.PRIVATE_PREFIX)}
        self.delete_relationship(eid)
        self.create_relationship(vid, source, label, properties=props)
