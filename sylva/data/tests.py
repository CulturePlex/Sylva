# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.test import TestCase
try:
    import ujson as json
except ImportError:
    import json  # NOQA
from rest_framework.test import APIClient, APITestCase, APIRequestFactory
from data.models import Data, MediaNode, MediaFile, MediaLink
from graphs.models import Graph


# Utils: Methods for the API test
def check_nodes_get(test, url, data):
    # First, we check the get method
    response = test.client.get(url)
    # We check that the request is correct
    test.assertEqual(response.status_code, 200)
    # We check that the results is an empty list
    test.assertEqual(response.data, [])

    # Then, we check the post method
    response = test.client.post(url, data)

    # We check that the request is correct
    test.assertEqual(response.status_code, 201)
    nodetype_name = response.data['name']
    test.assertEqual(nodetype_name, test.nodetype_name)
    # Let's get again the nodetypes and we select one of them
    response = test.client.get(url)
    nodetype_slug = response.data[0]['slug']
    url = reverse("api_node_type",
                  args=[test.graph_slug, nodetype_slug])
    response = test.client.get(url)
    test.assertEqual(response.status_code, 200)
    test.assertEqual(response.data['slug'], nodetype_slug)
    test.assertEqual(response.data['nodes_info'], [])
    return nodetype_slug


def create_property(test, url, data, property_name):
    property_data_serialized = json.dumps(data)
    response = test.client.post(url, property_data_serialized,
                                format='json')

    test.assertEqual(response.status_code, 201)
    test.assertEqual(response.data['properties'][0]['name'], property_name)


def create_nodes(test, url, nodes_list):
    nodes_list_serialized = json.dumps(nodes_list)
    response = test.client.post(url, nodes_list_serialized, format='json')
    nodes_ids = response.data
    test.assertEqual(response.status_code, 201)
    return nodes_ids


def delete_nodes(test, url, nodes_ids):
    nodes_ids_serialized = json.dumps(nodes_ids)
    response = test.client.delete(url, nodes_ids_serialized, format='json')
    test.assertEqual(response.status_code, 204)
    test.assertEqual(len(response.data), 2)
    test.assertIsNotNone(response.data[0])
    test.assertIsNotNone(response.data[1])


def check_relationships(test, url, data_source, data_target):
    response = test.client.post(url, data_source)
    # We check that the request is correct
    test.assertEqual(response.status_code, 201)
    source_slug = response.data['slug']
    response = test.client.post(url, data_target)
    # We check that the request is correct
    test.assertEqual(response.status_code, 201)
    target_slug = response.data['slug']
    data = {'name': test.relationshiptype_name,
            'source': source_slug,
            'target': target_slug}
    url = reverse("api_relationship_types", args=[test.graph_slug])
    # Then, we check the post method
    response = test.client.post(url, data)
    data = {'name': test.relationshiptype_name}
    relationshiptype_name = response.data['name']
    test.assertEqual(relationshiptype_name, test.relationshiptype_name)
    response = test.client.get(url)
    relationshiptype_slug = response.data[0]['slug']
    url = reverse("api_relationship_type",
                  args=[test.graph_slug, relationshiptype_slug])
    response = test.client.get(url)
    test.assertEqual(response.status_code, 200)
    test.assertEqual(response.data['name'], test.relationshiptype_name)
    test.assertEqual(response.data['rels_info'], [])
    return (relationshiptype_slug, source_slug, target_slug)


def create_relationships(test, url, rels_list):
    rels_list_serialized = json.dumps(rels_list)
    response = test.client.post(url, rels_list_serialized, format='json')
    test.assertEqual(response.status_code, 201)
    return response.data


class MediaFileTest(TestCase):
    def setUp(self):
        # We modify the default storage path to store
        # the media file in our test directory
        self._old_default_storage_location = default_storage.location
        default_storage.location = 'sylva/data/fixtures/'
        self.media_label = "test"
        self.media_file = "lorem.json"
        self.data = Data.objects.create()
        self.mediaNode = MediaNode.objects.create(data=self.data)

    def tearDown(self):
        # We restart the default storage value after execute the tests
        default_storage.location = self._old_default_storage_location

    def test_mediaFile_creation(self):
        """
        Tests that a mediaFile node is created.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        self.assertIsNotNone(mf)

    def test_mediaFile_edition(self):
        """
        Tests that a mediaFile node is edited.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        self.assertIsNotNone(mf)
        self.assertEqual(mf.media_label, self.media_label)
        mf.media_label = "example"
        self.assertEqual(mf.media_label, "example")

    def test_mediaFile_deletion(self):
        """
        Tests that a mediaFile node is deleted.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        id_mf = mf.id
        elem = MediaFile.objects.get(pk=id_mf)
        self.assertIsNotNone(elem)
        MediaFile.objects.get(pk=id_mf).delete()
        try:
            MediaFile.objects.get(pk=id_mf)
            exists = True
        except MediaFile.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)


class MediaLinkTest(TestCase):
    """
    A set of tests for testing MedaLink .
    """

    def setUp(self):
        """
        Sets up a few attributes and and objects for the tests we'll run.
        """
        self.label = "Bob's link"
        self.link = 'bob.cultureplex.ca'
        self.new_label = "Robert's link"
        self.new_link = 'robert.cultureplex.ca'
        data = Data.objects.create()
        self.media_node = MediaNode.objects.create(data=data)
        self.media_link = MediaLink.objects.create(
            media_node=self.media_node, media_label=self.label,
            media_link=self.link)
        self.media_link_id = self.media_link.id

    def test_media_link_creation(self):
        """
        Test MediaLink creation from the setUp() method.
        """
        self.assertIsNotNone(self.media_link)
        self.assertIsNotNone(self.media_link.id)
        self.assertEqual(self.media_link.media_node, self.media_node)
        self.assertEqual(self.media_link.media_label, self.label)
        self.assertEqual(self.media_link.media_link, self.link)

    def test_media_link_edition(self):
        """
        Test MediaLink edition from the created one.
        """
        self.media_link.media_label = self.new_label
        self.media_link.media_link = self.new_link
        self.media_link.save()

        self.assertEqual(self.media_link.media_label, self.new_label)
        self.assertEqual(self.media_link.media_link, self.new_link)

    def test_media_link_deletion(self):
        """
        Test MediaLink deletion from the created one.
        """
        self.media_link.delete()

        try:
            MediaLink.objects.get(id=self.media_link_id)
            exist = True
        except MediaLink.DoesNotExist:
            exist = False

        self.assertEquals(exist, False)


class APIDataTest(APITestCase):
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

        # Let's store some features for node types and relationship types
        self.nodetype_name = 'nodetypeName'
        self.nodetype_description = 'nodetypeDescription'
        self.relationshiptype_name = 'relationshiptypeName'
        self.relationshiptype_description = 'relationshiptypeDescription'

    def tearDown(self):
        Graph.objects.get(name=self.graph_name).destroy()
        self.client.logout()

    def test_api_nodes_get(self):
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        check_nodes_get(self, url, data)

    def test_api_nodes_post(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)

    def test_api_nodes_delete(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])

        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)

        # # Deleting the nodes
        delete_nodes(self, url, nodes_ids)

    def test_api_relationships_get(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        check_relationships(self, url, data_source, data_target)

    def test_api_relationships_post(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        relationshiptype_slug, source_slug, target_slug = (
            check_relationships(self, url, data_source, data_target))
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, source_slug])
        property_name1 = 'prop1_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name1,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name1)
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, target_slug])
        property_name2 = 'prop2_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name2,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name2)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, source_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name1: node_name1}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        source_id = nodes_ids[0]
        url = reverse("api_nodes",
                      args=[self.graph_slug, target_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name2 = "nodeName2"
        node_data2 = {property_name2: node_name2}
        nodes_list = []
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        target_id = nodes_ids[0]
        # # Creating the relationships
        url = reverse("api_relationships",
                      args=[self.graph_slug, relationshiptype_slug])
        relationship_data = {'source_id': source_id, 'target_id': target_id}
        rels_list = []
        rels_list.append(relationship_data)
        rels_ids = create_relationships(self, url, rels_list)
        self.assertEqual(len(rels_ids), 1)

    def test_api_relationships_delete(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        relationshiptype_slug, source_slug, target_slug = (
            check_relationships(self, url, data_source, data_target))
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, source_slug])
        property_name1 = 'prop1_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name1,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name1)
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, target_slug])
        property_name2 = 'prop2_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name2,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name2)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, source_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name1: node_name1}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        source_id = nodes_ids[0]
        url = reverse("api_nodes",
                      args=[self.graph_slug, target_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name2 = "nodeName2"
        node_data2 = {property_name2: node_name2}
        nodes_list = []
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        target_id = nodes_ids[0]
        # # Creating the relationships
        url = reverse("api_relationships",
                      args=[self.graph_slug, relationshiptype_slug])
        relationship_data = {'source_id': source_id, 'target_id': target_id}
        rels_list = []
        rels_list.append(relationship_data)
        rels_ids = create_relationships(self, url, rels_list)
        self.assertEqual(len(rels_ids), 1)

        # # Deleting the relationships
        url = reverse("api_relationships",
                      args=[self.graph_slug, relationshiptype_slug])
        rels_list_serialized = json.dumps(rels_ids)
        response = self.client.delete(url, rels_list_serialized, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(response.data), 1)

    def test_api_node_get(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])

        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)
        # We get one of the nodes
        node_id = nodes_ids[0]
        url = reverse("api_node",
                      args=[self.graph_slug, nodetype_slug, node_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['properties'][property_name],
                         node_name1)

    def test_api_node_patch(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)
        # We get one of the nodes
        node_id = nodes_ids[0]
        url = reverse("api_node",
                      args=[self.graph_slug, nodetype_slug, node_id])
        new_node_name = 'new_node_name'
        new_data = {}
        new_data['properties'] = {}
        new_data['properties'][property_name] = new_node_name
        new_data_serialized = json.dumps(new_data)
        response = self.client.patch(url, new_data_serialized, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['properties'][property_name],
                         new_node_name)

    def test_api_node_put(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)
        # We get one of the nodes
        node_id = nodes_ids[0]
        url = reverse("api_node",
                      args=[self.graph_slug, nodetype_slug, node_id])
        new_node_name = 'new_node_name'
        new_data = {}
        new_data['properties'] = {}
        new_data['properties'][property_name] = new_node_name
        new_data_serialized = json.dumps(new_data)
        response = self.client.put(url, new_data_serialized, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['properties'][property_name],
                         new_node_name)

    def test_api_node_delete(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        nodetype_slug = check_nodes_get(self, url, data)
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name: node_name1}
        node_name2 = "nodeName2"
        node_data2 = {property_name: node_name2}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 2)
        # We get one of the nodes
        node_id = nodes_ids[0]
        url = reverse("api_node",
                      args=[self.graph_slug, nodetype_slug, node_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_api_relationship_get(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        relationshiptype_slug, source_slug, target_slug = (
            check_relationships(self, url, data_source, data_target))
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, source_slug])
        property_name1 = 'prop1_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name1,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name1)
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, target_slug])
        property_name2 = 'prop2_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name2,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name2)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, source_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name1: node_name1}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        source_id = nodes_ids[0]
        url = reverse("api_nodes",
                      args=[self.graph_slug, target_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name2 = "nodeName2"
        node_data2 = {property_name2: node_name2}
        nodes_list = []
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        target_id = nodes_ids[0]
        # # Creating the relationships
        url = reverse("api_relationships",
                      args=[self.graph_slug, relationshiptype_slug])
        relationship_data = {'source_id': source_id, 'target_id': target_id}
        rels_list = []
        rels_list.append(relationship_data)
        rels_ids = create_relationships(self, url, rels_list)
        self.assertEqual(len(rels_ids), 1)
        # We get one of the relationships
        rel_id = rels_ids[0]
        url = reverse("api_relationship",
                      args=[self.graph_slug, relationshiptype_slug, rel_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_relationship_delete(self):
        # We create the nodetypes for the source and the target
        source_name = self.nodetype_name + '_source'
        target_name = self.nodetype_name + '_target'
        data_source = {'name': source_name}
        data_target = {'name': target_name}
        url = reverse("api_node_types", args=[self.graph_slug])
        relationshiptype_slug, source_slug, target_slug = (
            check_relationships(self, url, data_source, data_target))
        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, source_slug])
        property_name1 = 'prop1_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name1,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name1)
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, target_slug])
        property_name2 = 'prop2_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name2,
            'datatype': property_datatype
        }
        create_property(self, url, property_data, property_name2)
        # # Creating the nodes
        url = reverse("api_nodes",
                      args=[self.graph_slug, source_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name1 = "nodeName1"
        node_data1 = {property_name1: node_name1}
        nodes_list = []
        nodes_list.append(node_data1)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        source_id = nodes_ids[0]
        url = reverse("api_nodes",
                      args=[self.graph_slug, target_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nodes'], [])
        node_name2 = "nodeName2"
        node_data2 = {property_name2: node_name2}
        nodes_list = []
        nodes_list.append(node_data2)
        nodes_ids = create_nodes(self, url, nodes_list)
        self.assertEqual(len(nodes_ids), 1)
        target_id = nodes_ids[0]
        # # Creating the relationships
        url = reverse("api_relationships",
                      args=[self.graph_slug, relationshiptype_slug])
        relationship_data = {'source_id': source_id, 'target_id': target_id}
        rels_list = []
        rels_list.append(relationship_data)
        rels_ids = create_relationships(self, url, rels_list)
        self.assertEqual(len(rels_ids), 1)
        # We get one of the relationships
        rel_id = rels_ids[0]
        url = reverse("api_relationship",
                      args=[self.graph_slug, relationshiptype_slug, rel_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
