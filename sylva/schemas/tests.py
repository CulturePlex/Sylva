# -*- coding:utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase, APIRequestFactory

from datetime import date, time

from graphs.models import Graph
from schemas.models import (Schema, NodeType, RelationshipType, NodeProperty,
                            RelationshipProperty)


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
        'float': (u'f', 1.9),
        'collaborator': (u'r', ""),
        'auto now': (u'w', ""),
        'auto now add': (u'a', ""),
        'auto increment': (u'i', ""),
        'auto increment update': (u'o', ""),
        'auto user': (u'e', "")}
    property_test.new_value = u"Bob's fake property value"
    property_test.schema = Schema.objects.create()


class NodePropertyTest(TestCase):
    """
    A set of tests for testing NodeProperty.
    """

    def setUp(self):
        """
        Sets up a few objects for the tets we'll run.
        """
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
            self.assertIsNotNone(node_property)
            self.assertIsNotNone(node_property.id)

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
        """
        Sets up a few objects for the tets we'll run.
        """
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
            self.assertIsNotNone(relationship_property)
            self.assertIsNotNone(relationship_property.id)

            k = relationship_property.key
            properties = self.properties[k]

            self.assertIsNotNone(relationship_property.id)
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
        NodeType.objects.get(pk=id_nt).delete()
        try:
            NodeType.objects.get(pk=id_nt)
            exists = True
        except NodeType.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)


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
        RelationshipType.objects.get(pk=id_rt).delete()
        try:
            RelationshipType.objects.get(pk=id_rt)
            exists = True
        except RelationshipType.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)


class APISchemaTest(APITestCase):
    def setUp(self):
        # We register a user
        self.user = User.objects.create(username='john', password='doe',
                                        is_active=True, is_staff=True)
        self.user.save()

        # We create a graph
        self.graph_name = "graphTest"
        self.graph = Graph.objects.create(name=self.graph_name,
                                          owner=self.user)
        self.graph_slug = self.graph.slug

        # We login with the new user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.factory = APIRequestFactory()

        # Let's store the basic url, useful for the calls
        self.schemas_url = '/api/graphs/' + self.graph_slug + '/types/'

        # Let's store some features for node types and relationship types
        self.nodetype_name = 'nodetypeName'
        self.nodetype_description = 'nodetypeDescription'
        self.relationshiptype_name = 'relationshiptypeName'
        self.relationshiptype_description = 'relationshiptypeDescription'

    def tearDown(self):
        self.client.logout()

    def test_api_nodetypes_get(self):
        url = self.schemas_url + 'nodes/'
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

    def test_api_nodetypes_post(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # First, we check the get method
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

    def test_api_relationshiptypes_get(self):
        url = self.schemas_url + 'relationships/'
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

    def test_api_relationshiptypes_post(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = self.schemas_url + 'nodes/'

        response = self.client.post(url, data_source)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        source_slug = response.data['slug']

        response = self.client.post(url, data_target)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        target_slug = response.data['slug']

        data = {'name': self.relationshiptype_name,
                'source': source_slug,
                'target': target_slug}
        url = self.schemas_url + 'relationships/'

        # First, we check the get method
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.relationshiptype_name)

    def test_api_nodetypes_nodetype_get(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # First, we check the get method
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = self.schemas_url + 'nodes/' + nodetype_slug + '/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], nodetype_slug)
        self.assertEqual(response.data['nodes_info'], list())

    def test_api_nodetypes_nodetype_delete(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # First, we check the get method
        response = self.client.get(url)

        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list()
        self.assertEqual(response.data, list())

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = self.schemas_url + 'nodes/' + nodetype_slug + '/'

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)

    def test_api_relationshiptypes_relationshiptype_get(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = self.schemas_url + 'nodes/'

        response = self.client.post(url, data_source)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        source_slug = response.data['slug']

        response = self.client.post(url, data_target)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        target_slug = response.data['slug']

        data = {'name': self.relationshiptype_name,
                'source': source_slug,
                'target': target_slug}
        url = self.schemas_url + 'relationships/'

        # Then, we check the post method
        response = self.client.post(url, data)

        data = {'name': self.relationshiptype_name}
        url = self.schemas_url + 'relationships/'

        # We check that the results is an empty list()
        relationshiptype_name = response.data['name']
        self.assertEqual(relationshiptype_name, self.relationshiptype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        relationshiptype_slug = response.data[0]['slug']
        url = self.schemas_url + 'relationships/' + relationshiptype_slug + '/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], relationshiptype_slug)
        self.assertEqual(response.data['rels_info'], list())

    def test_api_relationshiptypes_relationshiptype_delete(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = self.schemas_url + 'nodes/'

        response = self.client.post(url, data_source)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        source_slug = response.data['slug']

        response = self.client.post(url, data_target)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        target_slug = response.data['slug']

        data = {'name': self.relationshiptype_name,
                'source': source_slug,
                'target': target_slug}
        url = self.schemas_url + 'relationships/'

        # Then, we check the post method
        response = self.client.post(url, data)

        data = {'name': self.relationshiptype_name}
        url = self.schemas_url + 'relationships/'

        # We check that the results is an empty list()
        relationshiptype_name = response.data['name']
        self.assertEqual(relationshiptype_name, self.relationshiptype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        relationshiptype_slug = response.data[0]['slug']
        url = self.schemas_url + 'relationships/' + relationshiptype_slug + '/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)

    def test_api_nodetype_schema_get(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = self.schemas_url + 'nodes/' + nodetype_slug + '/schema/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.nodetype_name)

    def test_api_nodetype_schema_patch(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = self.schemas_url + 'nodes/' + nodetype_slug + '/schema/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.nodetype_name)

        nodetype_new_name = 'nodetypeNameChanged'
        data = {'name': nodetype_new_name}

        # And then, the patch to see the changes
        response = self.client.patch(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the result has the same name
        response_nodetype_name = response.data['name']
        self.assertEqual(response_nodetype_name, nodetype_new_name)

    def test_api_nodetype_schema_put(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = self.schemas_url + 'nodes/' + nodetype_slug + '/schema/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.nodetype_name)

        nodetype_new_name = 'nodetypeNameChanged'
        data = {'name': nodetype_new_name}

        # And then, the patch to see the changes
        response = self.client.put(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the result has the same name
        response_nodetype_name = response.data['name']
        self.assertEqual(response_nodetype_name, nodetype_new_name)

    def test_api_relationshiptype_schema_get(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = self.schemas_url + 'nodes/'

        response = self.client.post(url, data_source)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        source_slug = response.data['slug']

        response = self.client.post(url, data_target)
        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        target_slug = response.data['slug']

        data = {'name': self.relationshiptype_name,
                'source': source_slug,
                'target': target_slug}
        url = self.schemas_url + 'relationships/'

        # Then, we check the post method
        response = self.client.post(url, data)

        data = {'name': self.relationshiptype_name}
        url = self.schemas_url + 'relationships/'

        # We check that the results is an empty list()
        relationshiptype_name = response.data['name']
        self.assertEqual(relationshiptype_name, self.relationshiptype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        relationshiptype_slug = response.data[0]['slug']
        url = (
            self.schemas_url +
            'relationships/' +
            relationshiptype_slug +
            '/schema/')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.relationshiptype_name)

    def test_api_nodetype_properties_get(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = (self.schemas_url +
               'nodes/' +
               nodetype_slug +
               '/schema/properties/')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['properties'], list())

    def test_api_nodetype_properties_post(self):
        data = {'name': self.nodetype_name}
        url = self.schemas_url + 'nodes/'

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        # We check that the results is an empty list()
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = (self.schemas_url +
               'nodes/' +
               nodetype_slug +
               '/schema/properties/')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['properties'], list())

        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }

        response = self.client.post(url, property_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['properties'][0]['name'], property_name)
