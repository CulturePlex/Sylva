"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import date, time

from schemas.models import Schema, NodeType, RelationshipType, NodeProperty, RelationshipProperty


class SchemaTest(TestCase):
    """
    A set of tests for testing Schemas.
    """

    def test_schema_creation(self):
        """
        Tets Schema creation.
        """
        schema = Schema()

        self.assertIsNotNone(schema)
        self.assertIsNone(schema.id)
        schema.save()

        self.assertIsNotNone(schema.id)

        schema.set_option('boolean', True)
        schema.save()

        self.assertEquals(schema.get_option('boolean'), True)


def property_pre_setUp(property_test):
    """
    Sets up a few attributes for the new objects, nodes and relationships
    types, we'll create.
    """
    property_test.properties = {
        'default': (u'u', u''),
        'string': (u's', u"Bob's property"),
        'boolean': (u'b', True),
        'number': (u'n', 19),
        'text': (u'x', u"Bob has a node with his own name"),
        'date': (u'd', date(1988, 12, 14)),
        'time': (u't', time(19, 30, 55)),
        'choices': (u'c', ((1, 'one'), (2, 'two'))),
        'float': (u'f', 1.9)}
    property_test.new_value = u"Bob's fake property value"
    property_test.schema = Schema.objects.create()


class NodePropertyTest(TestCase):
    """
    A set of tests for testing NodeProperty.
    """
    def setUp(self):
        property_pre_setUp(self)
        self.node_type = NodeType.objects.create(
            name='bob_node', schema=self.schema)

        for k, v in self.properties.iteritems():
            NodeProperty.objects.create(
                node=self.node_type, key=k, datatype=v[0], value=v[1])

    def test_node_property_creation(self):
        """
        Tests NodeProperty creation from the setUp() method.
        """
        self.assertEqual(
            self.node_type.properties.count(), len(self.properties))

        for node_property in self.node_type.properties.all():
            k = node_property.key
            properties = self.properties[k]

            self.assertEqual(node_property.datatype, properties[0])
            self.assertEqual(node_property.value, str(properties[1]))
            self.assertEqual(node_property.node, self.node_type)

    def test_node_property_edition(self):
        """
        Tests NodeProperty edition from created ones.
        """
        for node_property in self.node_type.properties.all():
            node_property.value = self.new_value
            node_property.save()

        for node_property in self.node_type.properties.all():
            self.assertEqual(node_property.value, self.new_value)

    def test_node_property_deletion(self):
        """
        Tets NodeProperty deletion from created ones.
        """
        self.assertEqual(
            self.node_type.properties.count(), len(self.properties))
        self.node_type.properties.all().delete()
        self.assertEqual(self.node_type.properties.count(), 0)


class RelationshipPropertyTest(TestCase):
    """
    A set of tests for testing RelationshipProperties.
    """
    def setUp(self):
        property_pre_setUp(self)
        self.relationship_type = RelationshipType.objects.create(
            name='bob_relationship', schema=self.schema)

        for k, v in self.properties.iteritems():
            RelationshipProperty.objects.create(
                relationship=self.relationship_type, key=k, datatype=v[0],
                value=v[1])

    def test_relationship_property_creation(self):
        """
        Tests RelationshipProperty creation from the setUp() method.
        """
        self.assertEqual(
            self.relationship_type.properties.count(), len(self.properties))

        for relationship_property in self.relationship_type.properties.all():
            k = relationship_property.key
            properties = self.properties[k]

            self.assertEqual(relationship_property.datatype, properties[0])
            self.assertEqual(relationship_property.value, str(properties[1]))
            self.assertEqual(
                relationship_property.relationship, self.relationship_type)

    def test_relationship_property_edition(self):
        """
        Tests RelationshipProperty edition from created ones.
        """
        for relationship_property in self.relationship_type.properties.all():
            relationship_property.value = self.new_value
            relationship_property.save()

        for relationship_property in self.relationship_type.properties.all():
            self.assertEqual(relationship_property.value, self.new_value)

    def test_relationship_property_deletion(self):
        """
        Tets RelationshipProperty deletion from created ones.
        """
        self.assertEqual(
            self.relationship_type.properties.count(), len(self.properties))
        self.relationship_type.properties.all().delete()
        self.assertEqual(self.relationship_type.properties.count(), 0)
