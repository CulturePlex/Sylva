"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import LiveServerTestCase
from django.core import mail

from splinter import Browser


class UserTestCase(LiveServerTestCase):
    """
    A set of tests for testing Users, Accounts and UserProfiles.
    """

    def setUp(self):
        self.browser = Browser('phantomjs')

    def tearDown(self):
        self.browser.quit()

    def test_splinter_singup(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('bob@cultureplex.ca')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        self.assertEquals(self.browser.find_by_css('.body-inside').first.value, 'Thank you for signing up with us!\nYou have been sent an e-mail with an activation link to the supplied email.\nWe will store your signup information for 7 days on our server.')
        self.assertEquals(len(mail.outbox), 1)
        for line in mail.outbox[0].body.splitlines():
            if line.startswith('    http://example.com/accounts/activate/'):
                url = line[22:]
        self.browser.visit(self.live_server_url + url)
        print self.browser.html
        self.assertEquals(self.browser.title, 'SylvaDB - Dashboard')
