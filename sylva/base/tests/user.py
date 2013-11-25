"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import LiveServerTestCase

from splinter import Browser


def signup(test):
    test.browser.visit(test.live_server_url + '/accounts/signup/')
    test.browser.find_by_name('username').fill('bob')
    test.browser.find_by_name('email').fill('bob@cultureplex.ca')
    test.browser.find_by_name('password1').fill('bob_secret')
    test.browser.find_by_name('password2').fill('bob_secret')
    test.browser.find_by_value('Signup').first.click()


def signin(test):
    signup(test)
    test.browser.visit(test.live_server_url + '/accounts/signin/')
    test.browser.find_by_name('identification').fill('bob')
    test.browser.find_by_name('password').fill('bob_secret')
    test.browser.find_by_value('Signin').first.click()


def logout(test):
    test.browser.find_link_by_href('/accounts/signout/').first.click()


class UserTestCase(LiveServerTestCase):
    """
    A set of tests for testing Users, Accounts and UserProfiles.
    """

    def setUp(self):
        self.browser = Browser('phantomjs')

    def tearDown(self):
        self.browser.quit()

    def test_user_signup(self):
        signup(self)
        self.assertEquals(self.browser.find_by_css('.body-inside').first.value, 'Thank you for signing up with us!\nYou can now use the supplied credentials to signin.')
        self.assertEquals(self.browser.title, 'SylvaDB - Signup almost done!')

    def test_splinter_signin(self):
        signin(self)
        self.assertEquals(self.browser.title, 'SylvaDB - Dashboard')

    def test_splinter_logout(self):
        signin(self)
        logout(self)
        self.assertEquals(self.browser.title, 'SylvaDB - Signed out')
        self.assertEquals(self.browser.find_by_css('.body-inside').first.value, 'You have been signed out. Till we meet again.')

    """
    def test_user_details(self):
        signin(self)
        self.browser.visit(self.live_server_url + '/accounts/bob/edit/')
        self.assertEquals(self.browser.title, 'SylvaDB - Account setup')
        self.browser.find_by_name('first_name').fill('Bob')
        self.browser.find_by_name('last_name').fill('Doe')
        self.browser.find_by_name('mugshot').fill('') # Is a type file
        self.browser.find_by_name('language').fill('') # Is a select field
        self.browser.find_by_name('gender').fill('') # Is a select field
        self.browser.find_by_name('website').fill('')
        self.browser.find_by_name('location').fill('')
        self.browser.find_by_name('birth_date').fill('')
        self.browser.find_by_name('about_me').fill('')
        self.browser.find_by_name('instituion').fill('')
        self.browser.find_by_name('company').fill('')
        self.browser.find_by_name('lab').fill('')
        self.browser.find_by_value('Save changes').first.click()

    def test_user_pass(self):
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.assertEquals(self.browser.title, 'SylvaDB - Signin')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('bob_password')
        self.browser.find_by_value('Signin').first.click()
        self.assertEquals(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.visit(self.live_server_url + '/accounts/bob/password/')
        self.assertEquals(self.browser.title, 'SylvaDB - Change pasword')
        self.browser.find_by_name('old_password').fill('bob_password')
        self.browser.find_by_name('new_password1').fill('')
        self.browser.find_by_name('new_password2').fill('')
        self.browser.find_by_value('Change password').first.click()

    def test_user_mail_change(self):
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.assertEquals(self.browser.title, 'SylvaDB - Signin')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('bob_password')
        self.browser.find_by_value('Signin').first.click()
        self.assertEquals(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.visit(self.live_server_url + '/accounts/bob/email/')
        self.assertEquals(self.browser.title, 'SylvaDB - Welcome to The Sylva Project')
        self.browser.find_by_name('email').fill('')
        self.browser.find_by_value('Change email').first.click()
    """
