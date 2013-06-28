import datetime
import csv
import os
import zipfile
import tempfile
import settings

from django.template.defaultfilters import force_escape as escape


class BaseConverter(object):

    html_codes = (
        (u'&', u'&amp;'),
        (u'<', u'&lt;'),
        (u'>', u'&gt;'),
        (u'"', u'&quot;'),
        (u"'", u'&#39;'),
    )

    def __init__(self, graph):
        self.graph = graph

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

        csv_dir_path = tempfile.mkdtemp(dir=settings.TMP_ROOT)

        os.mkdir(os.path.join(csv_dir_path, 'nodes'))
        os.mkdir(os.path.join(csv_dir_path, 'edges'))

        csv_nodes_path = os.path.join(csv_dir_path, 'nodes')
        csv_edges_path = os.path.join(csv_dir_path, 'edges')

        node_types = graph.schema.nodetype_set.all()
        rel_types = graph.schema.relationshiptype_set.all()

        for node_type in node_types:
            csv_filename = node_type.slug + '.csv'
            with open(os.path.join(csv_dir_path, 'nodes', csv_filename),
                      'w+') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"',
                                       quoting=csv.QUOTE_ALL)
                csv_header = ['id', 'type']
                for node_type_prop in node_type.properties.all():
                    csv_header.append(node_type_prop.key.encode('utf-8'))
                csvwriter.writerow(csv_header)
                node_type_properties = [node_type_prop.key for node_type_prop
                                        in node_type.properties.all()]
                nodes = node_type.all()
                for node in nodes:
                    node_properties = [node.id, node_type.name.encode('utf-8')]
                    for node_type_prop in node_type_properties:
                        if node_type_prop in node.properties:
                            node_prop = unicode(node.properties[node_type_prop])
                            node_properties.append(node_prop.encode('utf-8'))
                        else:
                            node_properties.append('')
                    csvwriter.writerow(node_properties)

        for rel_type in rel_types:
            csv_filename = rel_type.slug + '.csv'
            with open(os.path.join(csv_dir_path, 'edges', csv_filename),
                      'w+') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"',
                                       quoting=csv.QUOTE_ALL)
                csv_header = ['sourceId', 'targetId', 'label']
                for rel_type_prop in rel_type.properties.all():
                    csv_header.append(rel_type_prop.key.encode('utf-8'))
                csvwriter.writerow(csv_header)
                rel_type_properties = [rel_type_prop.key for rel_type_prop in
                                       rel_type.properties.all()]
                rels = rel_type.all()
                for rel in rels:
                    rel_properties = [rel.source.id, rel.target.id,
                                      rel_type.name.encode('utf-8')]
                    for rel_type_prop in rel_type_properties:
                        if rel_type_prop in rel.properties:
                            rel_prop = unicode(rel.properties[rel_type_prop])
                            rel_properties.append(rel_prop.encode('utf-8'))
                        else:
                            rel_properties.append('')
                    csvwriter.writerow(rel_properties)

        zipfile_name = graph.slug + '.zip'
        zipfile_path = os.path.join(csv_dir_path, zipfile_name)

        with zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED) as _zip:
            for root, dirs, files in os.walk(csv_nodes_path):
                for _file in files:
                    _zip.write(os.path.join(root, _file),
                               os.path.join('nodes', _file))
            for root, dirs, files in os.walk(csv_edges_path):
                for _file in files:
                    _zip.write(os.path.join(root, _file),
                               os.path.join('edges', _file))

        return zipfile_name, zipfile_path
