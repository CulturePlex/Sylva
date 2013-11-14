#-*- coding:utf8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

from accounts.models import Account, UserProfile


class UserAccountTest(TestCase):
    """
    A set of tests for testing Users, Accounts and UserProfiles.
    """

    def setUp(self):
        """
        Sets up a few attributes for the new objects we'll create.
        """
        self.username = 'bob'
        self.password = 'bob_secret'
        self.email = 'bob@cultureplex.ca'
        self.default_type = 1
        self.new_type = 2
        self.gender = 1
        self.website = 'bob.cultureplex.ca'
        self.birth_date = date(1988, 12, 14)

        self.user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email)
        self.user_profile = UserProfile.objects.get(user__id=self.user.id)

    def test_user_creation(self):
        """
        Tests User creation from the setUp() method.
        """
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.user.id)
        self.assertEqual(self.user.email, self.email)

    def test_account_creation(self):
        """
        Tests Account and UserProfile through User creation.
        """
        self.assertIsNotNone(self.user_profile.account)
        self.assertEqual(self.user_profile.account.type, self.default_type)
        self.assertIsNotNone(self.user_profile)
        self.assertIsNotNone(self.user_profile.id)
        self.assertIsNone(self.user_profile.gender)
        self.assertEqual(self.user_profile.website, '')
        self.assertIsNone(self.user_profile.birth_date)

    def test_account_edition(self):
        """
        Tests Account and UserProfile edition.
        """
        self.user_profile.account = Account.objects.filter(
            type=self.new_type)[0]
        self.user_profile.gender = self.gender
        self.user_profile.website = self.website
        self.user_profile.birth_date = self.birth_date
        self.user_profile.save()

        self.assertEqual(self.user_profile.account.type, self.new_type)
        self.assertEqual(self.user_profile.gender, self.gender)
        self.assertEqual(self.user_profile.website, self.website)
        self.assertEqual(
            self.user_profile.birth_date.year, self.birth_date.year)

    def test_account_deletion(self):
        """
        Tests User and UserProfile deletion.
        """
        self.user.is_active = False
        self.user.save()
        self.user_profile.delete()

        try:
            UserProfile.objects.get(id=self.user.id)
            exist = True
        except UserProfile.DoesNotExist:
            exist = False

        self.assertEquals(self.user.is_active, False)
        self.assertEquals(exist, False)
