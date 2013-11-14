#-*- coding:utf8 -*-

from django.test import TestCase

from data.models import Data, MediaNode, MediaLink


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
