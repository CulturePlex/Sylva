# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from neo4jrestclient.exceptions import StatusException

from engines.gdb.backends.blueprints import VERTEX
from engines.gdb.backends.neo4j import GraphDatabase as Neo4jGraphDatabase
if settings.ENABLE_SPATIAL:
    import geojson
    from shapely.geometry import shape
    # Any symbol would work
    SPATIAL_INDEX_KEY = "$"
    SPATIAL_INDEX_VALUE = "$"
    SPATIAL_PROPERTY_NAMES = ("bbox", "gtype")
else:
    raise ImproperlyConfigured(
        "Neo4j Spatial can only work if ENABLE_SPATIAL is set to 'True'")


class GraphDatabase(Neo4jGraphDatabase):

    def __init__(self, url, params=None, graph=None):
        super(GraphDatabase, self).__init__(url, params, graph)
        self.sidx = {}  # shortcut for spatial indices
        self.setup_spatial()

    def _get_filtered_nodes_properties(self, element):
        properties = element[1]["data"]
        elto_id = properties.pop("_id")
        elto_label = properties.pop("_label")
        properties.pop("_graph", None)
        for to_remove in SPATIAL_PROPERTY_NAMES:
            properties.pop(to_remove, None)
        return (elto_id, properties, elto_label)

    def _get_filtered_relationships_properties(element):
        properties = element[1]["data"]
        properties.pop("_id")
        properties.pop("_graph", None)
        elto_label = properties.pop("_label")
        source_props = element[2]["data"]
        source_id = source_props.pop("_id")
        source_label = source_props.pop("_label")
        source_props.pop("_graph", None)
        target_props = element[3]["data"]
        target_id = target_props.pop("_id")
        target_label = target_props.pop("_label")
        target_props.pop("_graph", None)
        for to_remove in SPATIAL_PROPERTY_NAMES:
            source_props.pop(to_remove, None)
            target_props.pop(to_remove, None)
        source = {
            "id": source_id,
            "properties": source_props,
            "label": source_label
        }
        target = {
            "id": target_id,
            "properties": target_props,
            "label": target_label
        }
        return (element[0], properties, elto_label, source, target)

    def destroy(self):
        """Delete nodes, relationships, and even indices"""
        for sidx_key, sidx_dict in self.sidx.items():
            index = sidx_dict["index"]
            if index in self.gdb.neograph.nodes.indexes.values():
                index.delete()
        self.sidx = {}
        super(GraphDatabase, self).destroy()

    # Spatial
    def setup_spatial(self):
        # Setup spatial indices if they don't exist already
        # The proccess goes as follows
        # - post /db/sylva/index/node/
        # {"name": "spatial3", "config": {"provider": "spatial", "wkt": "wkt"}}
        # - post /db/sylva/index/node/spatial3
        # {"value": "0", "key": "0",
        #  "uri": "http://host:port/db/sylva/node/17600"}
        # - post /db/sylva/ext/SpatialPlugin/graphdb/addNodeToLayer
        # {"layer": "spatial3", "node": "http://host:port/db/sylva/node/17600"}
        spatial_datatypes = [u'p', u'l', u'm']
        spatial_properties = self.graph.schema.nodetype_set.filter(
            properties__datatype__in=spatial_datatypes
        ).values("id", "schema__graph__id", "properties__key",
                 "properties__id")
        indices = self.gdb.neograph.nodes.indexes
        for spatial_property in spatial_properties:
            # Spatial index name is in
            # the form: <graph_id>_<nodetype_id>_<property_id>_spatial
            spatial_index_name = u"{}_{}_{}_spatial".format(
                spatial_property["schema__graph__id"],
                spatial_property["id"],
                spatial_property["properties__id"])
            spatial_index = None
            try:
                spatial_index = indices.get(spatial_index_name)
            except StatusException:
                spatial_index = None
            finally:
                # The spatial index property to index by is
                # in the form: _spatial_<property_id>
                spatial_index_by = u"_spatial_{}".format(
                    spatial_property["properties__id"])
                if spatial_index is None:
                    spatial_index = indices.create(
                        name=spatial_index_name,
                        provider="spatial",
                        wkt=spatial_index_by
                    )
                # Keep track of properties indexed in spatial indices
                sidx_key = u"{}_{}".format(
                    spatial_property["id"],
                    spatial_property["properties__key"])
                self.sidx[sidx_key] = {
                    "index": spatial_index,
                    "key": spatial_index_by,
                }

    def _get_spatial(self):
        if not self._spatial:
            self._spatial = self.gdb.neograph.extensions.SpatialPlugin
        return self._spatial
    spatial = property(_get_spatial)

    def _index_spatial_property(self, node, key, value, label):
        sidx_key = u"{}_{}".format(label, key)
        if sidx_key in self.sidx:
            geo_value = geojson.loads(value)
            is_valid_geojson = geojson.is_valid(geo_value)['valid'] != 'no'
            if is_valid_geojson:
                # Add node to index
                index = self.sidx[sidx_key]["index"]
                index_key = self.sidx[sidx_key]["key"]
                wkt_value = shape(geo_value).wkt
                node[index_key] = wkt_value
                index.add(SPATIAL_INDEX_KEY, SPATIAL_INDEX_VALUE, node)
                # Add node to layer
                self.spatial.addNodeToLayer(layer=index.name, node=node.url)

    def _deindex_spatial_property(self, node, key, label):
        sidx_key = u"{}_{}".format(label, key)
        if sidx_key in self.sidx:
            index = self.sidx[sidx_key]["index"]
            index.delete(SPATIAL_INDEX_KEY, SPATIAL_INDEX_VALUE, node)

    def _reindex_spatial_property(self, node, key, value, label):
        self._deindex_spatial_property(node, key, label)
        self._index_spatial_property(node, key, value, label)

    def _set_element_property(self, element, key, value, element_type=None):
        super(GraphDatabase, self)._set_element_property(
            element, key, value, element_type)
        if element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            self._reindex_spatial_property(node, key, value, label)

    def _delete_element_property(self, element, key, element_type=None):
        super(GraphDatabase, self)._delete_element_property(
            element, key, element_type)
        if element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            self._deindex_spatial_property(node, key, label)

    def _set_element_properties(self, element, properties, element_type=None):
        if element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key in self._get_public_keys(element):
                self._deindex_spatial_property(node, key, label)
        super(GraphDatabase, self)._set_element_properties(
            element, properties, element_type)

    def _update_element_properties(self, element, properties,
                                   element_type=None):
        super(GraphDatabase, self)._update_element_properties(
            element, properties, element_type)
        if element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key, value in properties.items():
                self._reindex_spatial_property(node, key, value, label)

    def _delete_element_properties(self, element, element_type=None):
        if element_type == VERTEX:
            label = element.getProperty("%slabel" % self.PRIVATE_PREFIX)
            node = self.gdb.neograph.nodes.get(element.getId())
            for key in self._get_public_keys(element):
                self._deindex_spatial_property(node, key, label)
        super(GraphDatabase, self)._delete_element_properties(
            element, element_type)

    def create_node(self, label, properties=None):
        node_id = super(GraphDatabase, self).create_node(
            label=label, properties=properties)
        # We introspect all property values to see if any would have a
        # spatial value and an index in which to be indexed
        if self.sidx and properties:
            node = self.gdb.neograph.nodes.get(node_id)
            for key, value in properties.items():
                self._index_spatial_property(node, key, value, label)
        return node_id

    def get_node_relationships(self, id, incoming=False, outgoing=False,
                               include_properties=False, label=None):
        rels = super(GraphDatabase, self).get_node_relationships(
            id, incoming, outgoing, include_properties, label
        )
        # Avoid returning spatial pecific relationships by checking their label
        spatial_rel_labels = set([
            "RTREE_METADATA", "RTREE_ROOT", "RTREE_CHILD",
            "RTREE_REFERENCE", "FIRST_NODE", "LAST_NODE", "OTHER", "NEXT",
            "OSM", "WAYS", "RELATIONS", "MEMBERS", "MEMBER", "TAGS", "GEOM",
            "BBOX", "NODE", "CHANGESET", "USER", "USERS", "OSM_USER",
        ])
        clean_rels = []
        for (rel_id, rel_props) in rels:
            label = self._get_edge(rel_id).neoelement.type
            if not label in spatial_rel_labels:
                clean_rels.append((rel_id, rel_props))
        return clean_rels

    def get_node_properties(self, id):
        properties = super(GraphDatabase, self).get_node_properties(id)
        for to_remove in SPATIAL_PROPERTY_NAMES:
            if to_remove in properties:
                del properties[to_remove]
        return properties
