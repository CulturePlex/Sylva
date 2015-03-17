import datetime
import csv
import os
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO  # NOQA

from django.shortcuts import get_object_or_404
from django.template.defaultfilters import force_escape as escape

from schemas.models import NodeType


class BaseConverter(object):

    html_codes = (
        (u'&', u'&amp;'),
        (u'<', u'&lt;'),
        (u'>', u'&gt;'),
        (u'"', u'&quot;'),
        (u"'", u'&#39;'),
    )

    def __init__(self, graph, csv_results=None, query_name=None,
                 node_type_id=None, headers_formatted=None,
                 headers_raw=None):
        self.graph = graph
        self.csv_results = csv_results
        self.query_name = query_name
        self.node_type_id = node_type_id
        self.headers_formatted = headers_formatted
        self.headers_raw = headers_raw

    def encode_html(self, value):
        return escape(value)


class GEXFConverter(BaseConverter):
    """
    Converts a Sylva neo4j graph to GEXF 1.2
    """

    header = u"""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
    <meta lastmodifieddate="%s">
        <creator>Sylva</creator>
        <description>A Sylva exported file</description>
    </meta>
    <graph mode="static" defaultedgetype="directed">"""

    def export(self):
        today = datetime.datetime.now()
        date = u"%s-%s-%s" % (today.year, today.month, today.day)
        attribute_counter = 0
        node_attributes = {}
        edge_attributes = {}
        nodes = ''
        for node in self.graph.nodes.all():
            nodes += u"""
                <node id="%s" label="%s" type="%s">
                <attvalues>""" % (node.id, node.display, node.label)
            for key, value in node.properties.iteritems():
                if key not in node_attributes:
                    node_attributes[key] = attribute_counter
                    attribute_counter += 1
                nodes += u"""
                    <attvalue for="%s" value="%s"/>""" % (node_attributes[key],
                            self.encode_html(value))
            nodes += u"""
                </attvalues>
                </node>"""
        attribute_counter = 0
        edges = ''
        for edge in self.graph.relationships.all():
            edges += u"""
                <edge id="%s" source="%s" target="%s" type="%s">
                <attvalues>""" % (edge.id,
                        edge.source.id,
                        edge.target.id,
                        edge.label)
            for key, value in edge.properties.iteritems():
                if key not in edge_attributes:
                    edge_attributes[key] = attribute_counter
                    attribute_counter += 1
                edges += u"""
                    <attvalue for="%s" value="%s"/>""" % (edge_attributes[key],
                            self.encode_html(value))
            edges += u"""
                </attvalues>
                </edge>"""
        node_attributes_xml = ''
        for key, value in node_attributes.iteritems():
            node_attributes_xml += u"""
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        edge_attributes_xml = ''
        for key, value in edge_attributes.iteritems():
            edge_attributes_xml += u"""
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        gephi_format = u"""%s
        <attributes class="node">
            %s
        </attributes>
        <attributes class="edge">
            %s
        </attributes>
        <nodes>%s
        </nodes>
        <edges>%s
        </edges>
    </graph>
</gexf>""" % (self.header, date, node_attributes_xml,
                edge_attributes_xml, nodes, edges)
        return gephi_format

    def stream_export(self):
        schema = self.graph.schema
        yield self.header
        # Node attributes
        node_attributes_xml = u"""
            <attribute id="NodeType" title="[Schema] Type" type="string"/>"
            <attribute id="NodeTypeId" title="[Schema] Type Id" type="string"/>"""
        for node_type in self.graph.schema.nodetype_set.all():
                for property_name in node_type.properties.all():
                    namespace_name = u"(%s) %s" % (self.encode_html(node_type.name),
                                            self.encode_html(property_name.key))

                    node_attributes_xml += u"""
                    <attribute id="n%s" title="%s" type="string"/>""" % \
                                    (property_name.id, namespace_name)
        yield u"""
        <attributes class="node">
            %s
        </attributes>
        """ % (node_attributes_xml)

        # Edge attributes
        edge_attributes_xml = u"""
            <attribute id="RelationshipType" title="[Schema] Allowed Relationship" type="string"/>"
            <attribute id="RelationshipTypeId" title="[Schema] Allowed Relationship Id" type="string"/>"""
        for relationship_type in self.graph.schema.relationshiptype_set.all():
                for property_name in relationship_type.properties.all():
                    namespace_name = u"(%s) %s" % (self.encode_html(relationship_type.name),
                                            self.encode_html(property_name.key))
                    edge_attributes_xml += u"""
                    <attribute id="r%s" title="%s" type="string"/>""" % \
                                    (property_name.id, namespace_name)
        yield u"""
        <attributes class="edge">
            %s
        </attributes>
        """ % (edge_attributes_xml)

        # Nodes
        yield '<nodes>'
        for node in self.graph.nodes.iterator():
            node_text = u"""
                <node id="%s" label="%s" type="%s">
                <attvalues>""" % (node.id,
                                self.encode_html(node.display),
                                self.encode_html(node.label_display))
            node_properties = {
                'NodeType': self.encode_html(node.label_display),
                'NodeTypeId': node.label
            }
            for key, value in node_properties.iteritems():
                node_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (self.encode_html(key),
                            self.encode_html(value))
            try:
                nodetype = schema.nodetype_set.get(id=node.label)
                nodetype_dict = nodetype.properties.all().values("id", "key")
                nodetype_properties = dict([(d["key"], d["id"])
                                            for d in nodetype_dict])
            except:
                nodetype_properties = {}
            for key, value in node.properties.iteritems():
                if key in nodetype_properties:
                    att_for = u"n%s" % self.encode_html(nodetype_properties[key])
                else:
                    att_for = self.encode_html(key)
                node_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (att_for,
                             self.encode_html(value))
            node_text += u"""
                </attvalues>
                </node>"""
            yield node_text
        yield '</nodes><edges>'

        # Edges
        for edge in self.graph.relationships.iterator():
            edge_text = u"""
                <edge id="%s" source="%s" target="%s" label="%s">
                <attvalues>""" % (edge.id,
                        edge.source.id,
                        edge.target.id,
                        self.encode_html(edge.label_display))
            edge_properties = {
                'RelationshipType': self.encode_html(edge.label_display),
                'RelationshipTypeId': edge.label
            }
            for key, value in edge_properties.iteritems():
                edge_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (self.encode_html(key),
                            self.encode_html(value))
            try:
                reltype = schema.relationshiptype_set.get(id=edge.label)
                reltype_dict = reltype.properties.all().values("id", "key")
                reltype_properties = dict([(d["key"], d["id"])
                                            for d in reltype_dict])
            except:
                reltype_properties = {}
            for key, value in edge.properties.iteritems():
                if key in reltype_properties:
                    att_for = u"r%s" % self.encode_html(reltype_properties[key])
                else:
                    att_for = self.encode_html(key)
                edge_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (att_for, self.encode_html(value))
            edge_text += u"""
                </attvalues>
                </edge>"""
            yield edge_text
        yield u"""
        </edges>
        """

        yield u"""
    </graph>
</gexf>"""


class CSVConverter(BaseConverter):
    """
    Converts a Sylva neo4j graph into CSV files.
    """

    def export(self):
        graph = self.graph
        node_types = graph.schema.nodetype_set.all()
        rel_types = graph.schema.relationshiptype_set.all()

        zip_buffer = StringIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for node_type in node_types:
                csv_name = os.path.join('nodes', node_type.slug + '.csv')
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer, delimiter=',',
                                        quotechar='"', quoting=csv.QUOTE_ALL)
                csv_header = ['id', 'type']
                node_type_properties = node_type.properties.all()
                node_properties_keys = [node_type_prop.key for node_type_prop
                                        in node_type_properties]
                for prop_key in node_properties_keys:
                    csv_header.append(prop_key.encode('utf-8'))
                csv_writer.writerow(csv_header)
                nodes = node_type.all()
                for node in nodes:
                    csv_properties = [node.id, node_type.name.encode('utf-8')]
                    node_properties = node.properties
                    for prop_key in node_properties_keys:
                        if prop_key in node_properties:
                            prop_value = unicode(node_properties[prop_key])
                            csv_properties.append(prop_value.encode('utf-8'))
                        else:
                            csv_properties.append('')
                    csv_writer.writerow(csv_properties)
                zip_file.writestr(csv_name, csv_buffer.getvalue())
                csv_buffer.close()

            for rel_type in rel_types:
                csv_name = os.path.join('relationships', rel_type.slug + '.csv')
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer, delimiter=',',
                                        quotechar='"', quoting=csv.QUOTE_ALL)
                csv_header = ['source id', 'target id', 'label']
                rel_type_properties = rel_type.properties.all()
                rel_properties_keys = [rel_type_prop.key for rel_type_prop in
                                       rel_type_properties]
                for prop_key in rel_properties_keys:
                    csv_header.append(prop_key.encode('utf-8'))
                csv_writer.writerow(csv_header)
                rels = rel_type.all()
                for rel in rels:
                    csv_properties = [rel.source.id, rel.target.id,
                                      rel_type.name.encode('utf-8')]
                    rel_properties = rel.properties
                    for prop_key in rel_properties_keys:
                        if prop_key in rel_properties:
                            prop_value = unicode(rel_properties[prop_key])
                            csv_properties.append(prop_value.encode('utf-8'))
                        else:
                            csv_properties.append('')
                    csv_writer.writerow(csv_properties)
                zip_file.writestr(csv_name, csv_buffer.getvalue())
                csv_buffer.close()

        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        zip_name = graph.slug + '.zip'

        return zip_data, zip_name


class CSVTableConverter(BaseConverter):
    """
    Converts a Sylva neo4j data table into CSV files.
    """

    def stream_export(self):
        node_type_id = self.node_type_id
        node_type = get_object_or_404(NodeType, id=node_type_id)
        nodes = node_type.all()
        properties = node_type.properties.all()
        csv_header = []

        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)

        for prop in properties:
            header = prop.key
            csv_header.append(header)
        csv_writer.writerow(csv_header)
        yield csv_file.getvalue()
        # We remove the last element to avoid overlap of values
        csv_file.seek(0)
        csv_file.truncate()

        for node in nodes:
            csv_node_values = []
            node_properties = node.properties
            for header_prop in csv_header:
                prop_value = node_properties.get(header_prop, 0)
                if isinstance(prop_value, unicode):
                    prop_value = prop_value.encode('utf-8')
                csv_node_values.append(prop_value)
            csv_writer.writerow(csv_node_values)
            yield csv_file.getvalue()
            # We remove the last element to avoid overlap of values
            csv_file.seek(0)
            csv_file.truncate()


class CSVQueryConverter(BaseConverter):
    """
    Converts a Sylva neo4j graph query into CSV files.
    """

    def stream_export(self):
        headers_formatted = self.headers_formatted
        headers_raw = self.headers_raw
        csv_results = self.csv_results
        results = csv_results[1:]

        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)

        csv_header = []
        for header in headers_raw:
            header_formatted = headers_formatted[header]
            csv_header.append(header_formatted)
        csv_writer.writerow(csv_header)
        yield csv_file.getvalue()
        # We remove the last element to avoid overlap of values
        csv_file.seek(0)
        csv_file.truncate()

        for result in results:
            results_encoded = []
            for individual_result in result:
                if isinstance(individual_result, unicode):
                    individual_result = individual_result.encode('utf-8')
                results_encoded.append(individual_result)
            csv_writer.writerow(results_encoded)
            yield csv_file.getvalue()
            # We remove the last element to avoid overlap of values
            csv_file.seek(0)
            csv_file.truncate()
