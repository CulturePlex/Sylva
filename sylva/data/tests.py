"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from data.models import Data, MediaNode, MediaFile


class MediaNodeTest(TestCase):
    def setUp(self):
        self.media_label = "test"
        self.media_file = "example.txt"
        self.data = Data.objects.create()
        self.mediaNode = MediaNode.objects.create(data=self.data)

    def test_mediaNode_creation(self):
        """
        Tests that a graph is created.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        self.assertIsNotNone(mf)

    def test_mediaNode_edition(self):
        """
        Tests that a graph is edited.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        self.assertIsNotNone(mf)
        self.assertEqual(mf.media_label, self.media_label)
        mf.media_label = "example"
        self.assertEqual(mf.media_label, "example")

    def test_mediaNode_deletion(self):
        """
        Tests that a graph is deleted.
        """
        mf = MediaFile(media_node=self.mediaNode,
            media_label=self.media_label,
            media_file=self.media_file)
        mf.save()
        id_mf = mf.id
        elem = MediaNode.objects.get(pk=id_mf)
        self.assertIsNotNone(elem)
        elem = MediaNode.objects.get(pk=id_mf).delete()
        self.assertIsNone(elem)
