"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from schemas.models import Schema
from schemas.models import NodeType, RelationshipType


class NodeTypesTest(TestCase):
    def setUp(self):
        self.mySchema = Schema.objects.create()

    def test_nodeType_creation(self):
        """
        Tests that a node type is created.
        """
        nodeTypeName = "nodeType"
        nt = NodeType.objects.create(name=nodeTypeName, schema=self.mySchema)
        self.assertIsNotNone(nt)
        self.assertEqual(nt.name, nodeTypeName)

    def test_nodeType_edition(self):
        """
        Tests that a node type is edited.
        """
        nodeTypeName = "nodeTypeExample"
        nt = NodeType.objects.create(name=nodeTypeName,
            schema=self.mySchema)
        self.assertEqual(nt.name, nodeTypeName)
        nt.name = 'nodeType'
        self.assertEqual(nt.name, 'nodeType')

    def test_nodeType_deletion(self):
        """
        Tests that a node type is deleted.
        """
        nodeTypeName = "nodeTypeExample"
        nt = NodeType.objects.create(name=nodeTypeName,
            schema=self.mySchema)
        id_nt = nt.id
        self.assertIsNotNone(nt)
        elem = NodeType.objects.get(pk=id_nt).delete()
        self.assertIsNone(elem)


class RelationshipTypesTest(TestCase):
    def setUp(self):
        self.mySchema = Schema.objects.create()

    def test_relationshipType_creation(self):
        """
        Tests that a relationship type is created.
        """
        relationshipTypeName = "relationshipTypeExample"
        rt = RelationshipType.objects.create(name=relationshipTypeName,
            schema=self.mySchema)
        self.assertIsNotNone(rt)
        self.assertEqual(rt.name, relationshipTypeName)

    def test_relationshipType_edition(self):
        """
        Tests that a relationship type is edited.
        """
        relationshipTypeName = "relationshipTypeExample"
        rt = RelationshipType.objects.create(name=relationshipTypeName,
            schema=self.mySchema)
        self.assertEqual(rt.name, relationshipTypeName)
        rt.name = 'relationshipType'
        self.assertEqual(rt.name, 'relationshipType')

    def test_relationshipType_deletion(self):
        """
        Tests that a relationship type is deleted.
        """
        relationshipTypeName = "relationshipTypeExample"
        rt = RelationshipType.objects.create(name=relationshipTypeName,
            schema=self.mySchema)
        id_rt = rt.id
        self.assertIsNotNone(rt)
        elem = RelationshipType.objects.get(pk=id_rt).delete()
        self.assertIsNone(elem)
