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
        self.assertEqual(self.browser.find_by_css('.body-inside').first.value, 'Thank you for signing up with us!\nYou can now use the supplied credentials to signin.')
        self.assertEqual(self.browser.title, 'SylvaDB - Signup almost done!')

    def test_user_signin(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        logout(self)

    def test_user_logout(self):
        signin(self)
        logout(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Signed out')
        self.assertEqual(self.browser.find_by_css('.body-inside').first.value, 'You have been signed out. Till we meet again.')

    def test_user_details(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/edit/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Account setup')
        self.browser.find_by_name('first_name').fill('Bob')
        self.browser.find_by_name('last_name').fill('Doe')
        self.browser.attach_file('mugshot', 'http://www.gravatar.com/avatar/3d4bcca5d9c3a56a0282f308f9acda07?s=90')
        self.browser.select('language', 'en')
        self.browser.select('gender', '1')
        self.browser.find_by_name('website').fill('http://www.bobweb.com')
        self.browser.find_by_name('location').fill('London, Ontario')
        self.browser.find_by_name('birth_date').fill('01/01/1975')
        self.browser.find_by_name('about_me').fill('I am a very nice guy')
        self.browser.find_by_name('instituion').fill('University')
        self.browser.find_by_name('company').fill('CulturePlex')
        self.browser.find_by_name('lab').fill('CulturePlex')
        self.browser.find_by_value('Save changes').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        logout(self)

    def test_user_pass(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/password/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Change password')
        self.browser.find_by_name('old_password').fill('bob_secret')
        self.browser.find_by_name('new_password1').fill('bob_password')
        self.browser.find_by_name('new_password2').fill('bob_password')
        self.browser.find_by_value('Change password').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Password changed')
        logout(self)

    def test_user_mail_change(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/email/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Welcome to The Sylva Project')
        self.browser.find_by_name('email').fill('bobnew@cultureplex.ca')
        self.browser.find_by_value('Change email').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Email verification')
