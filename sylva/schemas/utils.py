# -*- coding: utf-8 -*-
import json


def json_export(schema):
    schema_types = schema.export()
    schema_json = {"nodeTypes": {}, "allowedEdges":[]}
    for node_type in schema_types["node_types"]:
        attributes = {}
        for n in node_type.properties.all():
            attributes[n.key] = n.required
        schema_json["nodeTypes"][node_type.name] = attributes
    for edge_type in schema_types["relationship_types"]:
        edge_attributes = {}
        for n in edge_type.properties.all():
            edge_attributes[n.key] = n.required
        schema_json["allowedEdges"].append({
                "source": edge_type.source.name,
                "label": edge_type.name,
                "target": edge_type.target.name,
                "properties": edge_attributes})
    return json.dumps(schema_json)

