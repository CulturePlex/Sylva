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

        # First, we check the get method
        response = self.client.get(url)
        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list
        self.assertEqual(response.data, [])

        # Then, we check the post method
        response = self.client.post(url, data)

        # We check that the request is correct
        self.assertEqual(response.status_code, 201)
        nodetype_name = response.data['name']
        self.assertEqual(nodetype_name, self.nodetype_name)

        # Let's get again the nodetypes and we select one of them
        response = self.client.get(url)
        nodetype_slug = response.data[0]['slug']

        url = reverse("api_node_type",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], nodetype_slug)
        self.assertEqual(response.data['nodes_info'], [])

    def test_api_nodes_post(self):
        # # Creating the nodetype
        data = {'name': self.nodetype_name}
        url = reverse("api_node_types", args=[self.graph_slug])

        # First, we check the get method
        response = self.client.get(url)
        # We check that the request is correct
        self.assertEqual(response.status_code, 200)
        # We check that the results is an empty list
        self.assertEqual(response.data, [])
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

        url = reverse("api_node_type",
                      args=[self.graph_slug, nodetype_slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], nodetype_slug)

        # # Creating the property for the nodetype
        url = reverse("api_node_type_schema_properties",
                      args=[self.graph_slug, nodetype_slug])
        property_name = 'prop_name'
        property_datatype = 'default'
        property_data = {
            'key': property_name,
            'datatype': property_datatype
        }

        response = self.client.post(url, property_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['properties'][0]['name'], property_name)

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
        nodes_list_serialized = json.dumps(nodes_list)
        response = self.client.post(url, nodes_list_serialized, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 2)
