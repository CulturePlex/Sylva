#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import shutil

from django.test import TestCase
from django.core.files.storage import default_storage

from data.models import Data, MediaNode, MediaFile, MediaLink


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
