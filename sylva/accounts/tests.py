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

    def test_user_creation(self):
        """
        Tests User creation.
        """
        user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email)

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, self.email)

    def test_account_creation(self):
        """
        Tests Account and UserProfile through User creation.
        """
        user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email)

        user_profile = UserProfile.objects.get(user__id=user.id)
        account = user_profile.account

        self.assertIsNotNone(user_profile)
        self.assertIsNotNone(account)
        self.assertEqual(account.type, 1)

    def test_account_edition(self):
        """
        Tests Account and UserProfile edition.
        """
        user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email)

        user_profile = UserProfile.objects.get(user__id=user.id)

        self.assertIsNone(user_profile.gender)
        self.assertEqual(user_profile.website, '')
        self.assertIsNone(user_profile.birth_date)

        user_profile.account = Account.objects.filter(type=2)[0]
        user_profile.gender = 1
        user_profile.website = 'bob.cultureplex.ca'
        user_profile.birth_date = date(1988, 12, 14)
        user_profile.save()

        account = user_profile.account

        self.assertEqual(account.type, 2)
        self.assertEqual(user_profile.gender, 1)
        self.assertEqual(user_profile.website, 'bob.cultureplex.ca')
        self.assertEqual(user_profile.birth_date.year, 1988)

    def test_account_deletion(self):
        """
        Tests User and UserProfile deletion.
        """
        user = User.objects.create(
            username=self.username,
            password=self.password,
            email=self.email)
        user_profile = UserProfile.objects.get(user__id=user.id)

        user.is_active = False
        user.save()
        user_profile.delete()

        try:
            UserProfile.objects.get(id=user.id)
            exist = True
        except UserProfile.DoesNotExist:
            exist = False

        self.assertEquals(user.is_active, False)
        self.assertEquals(exist, False)
