"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import shutil

from django.test import TestCase
from django.core.files.storage import default_storage

from data.models import Data, MediaNode, MediaFile


class MediaFileTest(TestCase):
    def setUp(self):
        # We modify the default storage path to store
        # the media file in our test directory
        self._old_default_storage_location = default_storage.location
        default_storage.location = 'data/fixtures/'
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
