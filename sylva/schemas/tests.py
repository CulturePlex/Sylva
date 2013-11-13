"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from schemas.models import Schema


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
        self.assertEquals(schema.get_option('boolean'), True)
