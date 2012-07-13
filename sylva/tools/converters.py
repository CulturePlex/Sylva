import datetime
import simplejson

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
#        if isinstance(value, basestring):
#            for replacement in self.html_codes:
#                value = value.replace(replacement[0], replacement[1])
        return escape(value)

class GEXFConverter(BaseConverter):
    " Converts a Sylva neo4j graph to GEXF 1.2"

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
                    <attribute id="%s" title="%s" type="string"/>""" % \
                                    (node_type.id, namespace_name)
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
                    <attribute id="%s" title="%s" type="string"/>""" % \
                                    (relationship_type.id, namespace_name)
        yield u"""
        <attributes class="edge">
            %s
        </attributes>
        """ % (edge_attributes_xml)


        # Nodes
        yield '<nodes>'
        node_attributes = {}
        edge_attributes = {}
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
            for key, value in node.properties.iteritems():
                node_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (self.encode_html(node.label),
                            self.encode_html(value))
            node_text += u"""
                </attvalues>
                </node>"""
            yield node_text
        yield '</nodes><edges>'

        # Edges
        edges = ''
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
            for key, value in edge.properties.iteritems():
                edge_text += u"""
                    <attvalue for="%s" value="%s"/>""" % \
                            (self.encode_html(edge.label),
                            self.encode_html(value))
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
