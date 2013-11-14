"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
import shutil

from django.test import TestCase

from data.models import Data, MediaNode, MediaFile


class MediaFileTest(TestCase):
    def setUp(self):
        # We create the "media" directory to store
        # the media file
        try:
            os.makedirs("sylva/media")
        except OSError:
            if not os.path.isdir("sylva/media"):
                raise
        if os.path.exists("sylva/media/example.txt"):
            f = file("sylva/media/example.txt", "r+")
        else:
            f = file("sylva/media/example.txt", "w")
        self.media_label = "test"
        self.media_file = "example.txt"
        self.data = Data.objects.create()
        self.mediaNode = MediaNode.objects.create(data=self.data)

    def tearDown(self):
        # We remove the directory after execute the tests
        shutil.rmtree('sylva/media')

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
