import datetime
import simplejson


class BaseConverter(object):

    html_codes = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    )
    
    def __init__(self, graph):
        self.graph = graph


    def encode_html(self, value):
        if isinstance(value, basestring):
            for replacement in self.html_codes:
                value = value.replace(replacement[0], replacement[1])
        return value

class GEXFConverter(BaseConverter):
    " Converts a Sylva neo4j graph to GEXF 1.2"

    header = """<?xml version="1.0" encoding="UTF-8"?> 
<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2"> 
    <meta lastmodifieddate="%s"> 
        <creator>Sylva</creator> 
        <description>A Sylva exported file</description> 
    </meta> 
    <graph mode="static" defaultedgetype="directed">"""

    def export(self):
        today = datetime.datetime.now()
        date = "%s-%s-%s" % (today.year, today.month, today.day)
        attribute_counter = 0
        node_attributes = {}
        edge_attributes = {}
        nodes = ''
        for node in self.graph.nodes.all():
            nodes += """
                <node id="%s" label="%s" type="%s">
                <attvalues>""" % (node.id, node.display, node.label_display)
            for key, value in node.properties.iteritems():
                if key not in node_attributes:
                    node_attributes[key] = attribute_counter
                    attribute_counter += 1
                nodes += """
                    <attvalue for="%s" value="%s"/>""" % (node_attributes[key],
                            self.encode_html(value))
            nodes += """
                </attvalues>
                </node>"""
        attribute_counter = 0
        edges = ''
        for edge in self.graph.relationships.all():
            edges += """
                <edge id="%s" source="%s" target="%s" type="%s">
                <attvalues>""" % (edge.id, 
                        edge.source.id,
                        edge.target.id,
                        edge.label_display)
            for key, value in edge.properties.iteritems():
                if key not in edge_attributes:
                    edge_attributes[key] = attribute_counter
                    attribute_counter += 1
                edges += """
                    <attvalue for="%s" value="%s"/>""" % (edge_attributes[key],
                            self.encode_html(value))
            edges += """
                </attvalues>
                </edge>"""
        node_attributes_xml = ''
        for key, value in node_attributes.iteritems():
            node_attributes_xml += """
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        edge_attributes_xml = ''
        for key, value in edge_attributes.iteritems():
            edge_attributes_xml += """
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        gephi_format = """%s
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

        # Nodes
        yield '<nodes>'
        attribute_counter = 0
        node_attributes = {}
        edge_attributes = {}
        for node in self.graph.nodes.iterator():
            node_text = """
                <node id="%s" label="%s" type="%s">
                <attvalues>""" % (node.id,
                                self.encode_html(node.display),
                                self.encode_html(node.label_display))
            for key, value in node.properties.iteritems():
                if key not in node_attributes:
                    node_attributes[key] = attribute_counter
                    attribute_counter += 1
                node_text += """
                    <attvalue for="%s" value="%s"/>""" % (node_attributes[key],
                            self.encode_html(value))
            node_text += """
                </attvalues>
                </node>"""
            yield node_text
        yield '</nodes><edges>'

        # Edges
        attribute_counter = 0
        edges = ''
        for edge in self.graph.relationships.iterator():
            edge_text = """
                <edge id="%s" source="%s" target="%s" label="%s">
                <attvalues>""" % (edge.id, 
                        edge.source.id,
                        edge.target.id,
                        edge.label_display)
            for key, value in edge.properties.iteritems():
                if key not in edge_attributes:
                    edge_attributes[key] = attribute_counter
                    attribute_counter += 1
                edge_text += """
                    <attvalue for="%s" value="%s"/>""" % (edge_attributes[key],
                            self.encode_html(value))
            edge_text += """
                </attvalues>
                </edge>"""
            yield edge_text
        yield """
        </edges>
        """

        # Node attributes
        node_attributes_xml = ''
        for key, value in node_attributes.iteritems():
            node_attributes_xml += """
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        yield """
        <attributes class="node">
            %s
        </attributes>
        """ % (node_attributes_xml)

        # Edge attributes
        edge_attributes_xml = ''
        for key, value in edge_attributes.iteritems():
            edge_attributes_xml += """
                <attribute id="%s" title="%s" type="string"/>""" % (value,
                        key)
        yield """
        <attributes class="edge">
            %s
        </attributes>
        """ % (edge_attributes_xml)


        yield """
    </graph> 
</gexf>""" 
