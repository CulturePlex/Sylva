"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import LiveServerTestCase
from django.core.management import call_command

from splinter import Browser


class SplinterTestCase(LiveServerTestCase):
    """
    A set of tests for testing Users, Accounts and UserProfiles.
    """

    def setUp(self):
        self.browser = Browser('phantomjs')

    def tearDown(self):
        self.browser.quit()

    def test_splinter_singup(self):
        call_command('check_permissions')
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('bob@cultureplex.ca')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        self.assertEquals(self.browser.find_by_css('.body-inside').first.value, 'Thank you for signing up with us!\nYou have been sent an e-mail with an activation link to the supplied email.\nWe will store your signup information for 7 days on our server.')

    """
    def test_splinter_signin(self):
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.assertEquals(self.browser.title, 'SylvaDB - Signin')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('bob_secret')
        self.browser.find_by_value('Signin').first.click()
        self.assertEquals(self.browser.title, 'SylvaDB - Dashboard')

    def test_splinter_logout(self):
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.assertEquals(self.browser.title, 'SylvaDB - Signin')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('bob_secret')
        self.browser.find_by_value('Signin').first.click()
        self.browser.find_link_by_href('/accounts/signout/').first.click()
        self.assertEquals(self.browser.title, 'SylvaDB - Signed out')
        self.assertEquals(self.browser.find_by_css('.body-inside').first.value, 'You have been signed out. Till we meet again.')
    """
