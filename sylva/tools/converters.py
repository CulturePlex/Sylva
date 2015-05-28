import datetime
import csv
import os
import unicodecsv
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
    def export(self):
        schema = self.graph.schema
        today = datetime.datetime.now()
        date = u"%s-%s-%s" % (today.year, today.month, today.day)
        graph_name = self.graph.name
        graph_description = self.graph.description
        graph_owner = self.graph.owner.username

        # Header
        header = (
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<gexf xmlns="http://www.gexf.net/1.2draft" '
            u'xmlns:viz="http://www.gexf.net/1.2draft/viz" '
            u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            u'xsi:schemaLocation="http://www.gexf.net/1.2draft'
            u'http://www.gexf.net/1.2draft/gexf.xsd" '
            u'version="1.2">\n')

        # Meta
        name = u''
        if graph_name:
            name = u'\t\t<name>{0}</name>\n'.format(graph_name)
        description = u''
        if graph_description:
            description = (
                u'\t\t<description>{0}</description>\n'.format(
                    graph_description))
        owner = u''
        if graph_owner:
            owner = u'\t\t<creator>{0}</creator>\n'.format(graph_owner)
        meta = (
            u'\t<meta lastmodifieddate="{0}">\n'
            u'{1}{2}{3}'
            u'\t</meta>\n'.format(date, owner, name, description))

        # Graph header
        graph_header = u'\t<graph mode="static" defaultedgetype="directed">\n'

        # Node attributes
        node_attributes = (
            u'\t\t<attributes class="node">\n'
            u'\t\t\t<attribute id="NodeType" '
            u'title="[Schema] Type" type="string"/>\n'
            u'\t\t\t<attribute id="NodeTypeId" '
            u'title="[Schema] Type Id" type="string"/>\n')

        for node_type in self.graph.schema.nodetype_set.all():
            for property_name in node_type.properties.all():
                namespace_name = u"(%s) %s" % (
                    self.encode_html(node_type.name),
                    self.encode_html(property_name.key))
                node_attributes += (
                    u'\t\t\t<attribute '
                    u'id="n{0}" title="{1}" '
                    u'type="string"/>\n'.format(property_name.id,
                                                namespace_name))
        node_attributes += u'\t\t</attributes>\n'

        # Edge attributes
        edge_attributes = (
            u'\t\t<attributes class="edge">\n'
            u'\t\t\t<attribute id="RelationshipType" '
            u'title="[Schema] Allowed Relationship" type="string"/>\n'
            u'\t\t\t<attribute id="RelationshipTypeId" '
            u'title="[Schema] Allowed Relationship Id" type="string"/>\n')

        for relationship_type in self.graph.schema.relationshiptype_set.all():
            for property_name in relationship_type.properties.all():
                namespace_name = u"(%s) %s" % (
                    self.encode_html(relationship_type.name),
                    self.encode_html(property_name.key))
                edge_attributes += (
                    u'\t\t\t<attribute '
                    u'id="r{0}" title="{1}" '
                    u'type="string"/>\n'.format(property_name.id,
                                                namespace_name))
        edge_attributes += u'\t\t</attributes>\n'

        # Nodes
        nodes = u'\t\t<nodes>\n'

        for node in self.graph.nodes.iterator():
            # Node metadata
            node_meta = (
                u'\t\t\t<node id="{0}" label="{1}" type="{2}">\n'
                u'\t\t\t<attvalues>\n'.format(node.id,
                                              self.encode_html(node.display),
                                              self.encode_html(
                                                  node.label_display)))
            nodes += node_meta
            # Node properties
            node_properties = {
                'NodeType': self.encode_html(node.label_display),
                'NodeTypeId': node.label
            }
            for key, value in node_properties.iteritems():
                node_properties_text = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        self.encode_html(key),
                        self.encode_html(value)))
                nodes += node_properties_text
            # Node properties values
            try:
                nodetype = schema.nodetype_set.get(id=node.label)
                nodetype_dict = nodetype.properties.all().values("id", "key")
                nodetype_properties = dict([
                    (d["key"], d["id"]) for d in nodetype_dict])
            except:
                nodetype_properties = {}
            for key, value in node.properties.iteritems():
                if key in nodetype_properties:
                    att_for = (
                        u"n%s" % self.encode_html(nodetype_properties[key]))
                else:
                    att_for = self.encode_html(key)
                node_properties_values = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        att_for,
                        self.encode_html(value)))
                nodes += node_properties_values
            node_finish = (
                u'\t\t\t</attvalues>\n'
                u'\t\t\t</node>\n')
            nodes += node_finish
        nodes += u'\t\t</nodes>\n'

        # Edges
        edges = u'\t\t<edges>\n'

        for edge in self.graph.relationships.iterator():
            # Edge metadata
            edge_meta = (
                u'\t\t\t<edge id="{0}" source="{1}" '
                u'target="{2}" label="{3}">\n'
                u'\t\t\t<attvalues>\n'.format(edge.id,
                                              edge.source.id,
                                              edge.target.id,
                                              self.encode_html(
                                                  edge.label_display)))
            edges += edge_meta
            # Edge properties
            edge_properties = {
                'RelationshipType': self.encode_html(edge.label_display),
                'RelationshipTypeId': edge.label
            }
            for key, value in edge_properties.iteritems():
                edge_properties_text = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        self.encode_html(key),
                        self.encode_html(value)))
                edges += edge_properties_text
            # Edge properties values
            try:
                reltype = schema.relationshiptype_set.get(id=edge.label)
                reltype_dict = reltype.properties.all().values("id", "key")
                reltype_properties = dict([
                    (d["key"], d["id"]) for d in reltype_dict])
            except:
                reltype_properties = {}
            for key, value in edge.properties.iteritems():
                if key in reltype_properties:
                    att_for = (
                        u"r%s" % self.encode_html(reltype_properties[key]))
                else:
                    att_for = self.encode_html(key)
                edge_properties_values = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        att_for,
                        self.encode_html(value)))
                edges += edge_properties_values
            edge_finish = (
                u'\t\t\t</attvalues>\n'
                u'\t\t\t</edge>\n')
            edges += edge_finish
        edges += u'\t\t</edges>\n'

        # Finish gexf file
        finish_gexf = (
            u'\t</graph>\n'
            u'</gexf>')

        gephi_format = u"{0}{1}{2}{3}{4}{5}{6}{7}".format(header,
                                                          meta,
                                                          graph_header,
                                                          node_attributes,
                                                          edge_attributes,
                                                          nodes,
                                                          edges,
                                                          finish_gexf)
        return gephi_format

    def stream_export(self):
        schema = self.graph.schema
        today = datetime.datetime.now()
        date = u"%s-%s-%s" % (today.year, today.month, today.day)
        graph_name = self.graph.name
        graph_description = self.graph.description
        graph_owner = self.graph.owner.username

        # Header
        header = (
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<gexf xmlns="http://www.gexf.net/1.2draft" '
            u'xmlns:viz="http://www.gexf.net/1.2draft/viz" '
            u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            u'xsi:schemaLocation="http://www.gexf.net/1.2draft'
            u'http://www.gexf.net/1.2draft/gexf.xsd" '
            u'version="1.2">\n')
        yield header

        # Meta
        name = u''
        if graph_name:
            name = u'\t\t<name>{0}</name>\n'.format(graph_name)
        description = u''
        if graph_description:
            description = (
                u'\t\t<description>{0}</description>\n'.format(
                    graph_description))
        owner = u''
        if graph_owner:
            owner = u'\t\t<creator>{0}</creator>\n'.format(graph_owner)
        meta = (
            u'\t<meta lastmodifieddate="{0}">\n'
            u'{1}{2}{3}'
            u'\t</meta>\n'.format(date, owner, name, description))
        yield meta

        # Graph header
        graph_header = u'\t<graph mode="static" defaultedgetype="directed">\n'
        yield graph_header

        # Node attributes
        node_attributes = (
            u'\t\t<attributes class="node">\n'
            u'\t\t\t<attribute id="NodeType" '
            u'title="[Schema] Type" type="string"/>\n'
            u'\t\t\t<attribute id="NodeTypeId" '
            u'title="[Schema] Type Id" type="string"/>\n')
        yield node_attributes

        for node_type in self.graph.schema.nodetype_set.all():
            for property_name in node_type.properties.all():
                namespace_name = u"(%s) %s" % (
                    self.encode_html(node_type.name),
                    self.encode_html(property_name.key))
                node_attributes = (
                    u'\t\t\t<attribute '
                    u'id="n{0}" title="{1}" '
                    u'type="string"/>\n'.format(property_name.id,
                                                namespace_name))
                yield node_attributes
        yield u'\t\t</attributes>\n'

        # Edge attributes
        edge_attributes = (
            u'\t\t<attributes class="edge">\n'
            u'\t\t\t<attribute id="RelationshipType" '
            u'title="[Schema] Allowed Relationship" type="string"/>\n'
            u'\t\t\t<attribute id="RelationshipTypeId" '
            u'title="[Schema] Allowed Relationship Id" type="string"/>\n')
        yield edge_attributes

        for relationship_type in self.graph.schema.relationshiptype_set.all():
            for property_name in relationship_type.properties.all():
                namespace_name = u"(%s) %s" % (
                    self.encode_html(relationship_type.name),
                    self.encode_html(property_name.key))
                edge_attributes = (
                    u'\t\t\t<attribute '
                    u'id="r{0}" title="{1}" '
                    u'type="string"/>\n'.format(property_name.id,
                                                namespace_name))
                yield edge_attributes
        yield u'\t\t</attributes>\n'

        # Nodes
        yield u'\t\t<nodes>\n'

        for node in self.graph.nodes.iterator():
            # Node metadata
            node_meta = (
                u'\t\t\t<node id="{0}" label="{1}" type="{2}">\n'
                u'\t\t\t<attvalues>\n'.format(node.id,
                                              self.encode_html(node.display),
                                              self.encode_html(
                                                  node.label_display)))
            yield node_meta

            # Node properties
            node_properties = {
                'NodeType': self.encode_html(node.label_display),
                'NodeTypeId': node.label
            }
            for key, value in node_properties.iteritems():
                node_properties_text = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        self.encode_html(key),
                        self.encode_html(value)))
            yield node_properties_text

            # Node properties values
            try:
                nodetype = schema.nodetype_set.get(id=node.label)
                nodetype_dict = nodetype.properties.all().values("id", "key")
                nodetype_properties = dict([
                    (d["key"], d["id"]) for d in nodetype_dict])
            except:
                nodetype_properties = {}
            for key, value in node.properties.iteritems():
                if key in nodetype_properties:
                    att_for = (
                        u"n%s" % self.encode_html(nodetype_properties[key]))
                else:
                    att_for = self.encode_html(key)
                node_properties_values = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        att_for,
                        self.encode_html(value)))
                yield node_properties_values
            node_finish = (
                u'\t\t\t</attvalues>\n'
                u'\t\t\t</node>\n')
            yield node_finish
        yield u'\t\t</nodes>\n'

        # Edges
        yield u'\t\t<edges>\n'

        for edge in self.graph.relationships.iterator():
            # Edge metadata
            edge_meta = (
                u'\t\t\t<edge id="{0}" source="{1}" '
                u'target="{2}" label="{3}">\n'
                u'\t\t\t<attvalues>\n'.format(edge.id,
                                              edge.source.id,
                                              edge.target.id,
                                              self.encode_html(
                                                  edge.label_display)))
            yield edge_meta

            # Edge properties
            edge_properties = {
                'RelationshipType': self.encode_html(edge.label_display),
                'RelationshipTypeId': edge.label
            }
            for key, value in edge_properties.iteritems():
                edge_properties_text = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        self.encode_html(key),
                        self.encode_html(value)))
            yield edge_properties_text

            # Edge properties values
            try:
                reltype = schema.relationshiptype_set.get(id=edge.label)
                reltype_dict = reltype.properties.all().values("id", "key")
                reltype_properties = dict([
                    (d["key"], d["id"]) for d in reltype_dict])
            except:
                reltype_properties = {}
            for key, value in edge.properties.iteritems():
                if key in reltype_properties:
                    att_for = (
                        u"r%s" % self.encode_html(reltype_properties[key]))
                else:
                    att_for = self.encode_html(key)
                edge_properties_values = (
                    u'\t\t\t\t<attvalue for="{0}" value="{1}"/>\n'.format(
                        att_for,
                        self.encode_html(value)))
                yield edge_properties_values
            edge_finish = (
                u'\t\t\t</attvalues>\n'
                u'\t\t\t</edge>\n')
            yield edge_finish
        yield u'\t\t</edges>\n'

        # Finish gexf file
        yield (
            u'\t</graph>\n'
            u'</gexf>')


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
                csv_name = os.path.join(
                    'relationships', rel_type.slug + '.csv')
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
        csv_writer = unicodecsv.writer(csv_file, encoding='utf-8')

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
        csv_writer = unicodecsv.writer(csv_file, encoding='utf-8')

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
                results_encoded.append(individual_result)
            csv_writer.writerow(results_encoded)
            yield csv_file.getvalue()
            # We remove the last element to avoid overlap of values
            csv_file.seek(0)
            csv_file.truncate()
