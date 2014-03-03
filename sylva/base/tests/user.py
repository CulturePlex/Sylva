from django.test import LiveServerTestCase

from splinter import Browser


def signup(test, username, email, password):
    test.browser.visit(test.live_server_url + '/accounts/signup/')
    test.browser.find_by_name('username').fill(username)
    test.browser.find_by_name('email').fill(email)
    test.browser.find_by_name('password1').fill(password)
    test.browser.find_by_name('password2').fill(password)
    test.browser.find_by_value('Signup').first.click()


def signin(test, username, password):
    test.browser.visit(test.live_server_url + '/accounts/signin/')
    test.browser.find_by_name('identification').fill(username)
    test.browser.find_by_name('password').fill(password)
    test.browser.find_by_xpath(
        "//div[@id='body']/div/form/input").first.click()


def logout(test):
    test.browser.find_link_by_href('/accounts/signout/').first.click()


class UserTestCase(LiveServerTestCase):
    """
    A set of tests for testing Users, Accounts and UserProfiles. Also, we
    check the patterns for the required fields for signup, signin, the menu of
    user details, the change password view and the change email view.
    """

    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.browser.quit()

    def test_user_signup(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        self.assertEqual(self.browser.find_by_css('.body-inside').first.value, 'Thank you for signing up with us!\nYou can now use the supplied credentials to signin.')
        self.assertEqual(self.browser.title, 'SylvaDB - Signup almost done!')

    def test_user_singup_empty_email(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')

    def test_user_singup_bad_email(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('bobcultureplex.ca')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid e-mail address.')

    def test_user_singup_empty_name(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('')
        self.browser.find_by_name('email').fill('bob@cultureplex.ca')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')

    def test_user_singup_empty_password(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('bob@cultureplex.ca')
        self.browser.find_by_name('password1').fill('')
        self.browser.find_by_name('password2').fill('bob_secret')
        self.browser.find_by_value('Signup').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')

    def test_user_singup_password_unmatched(self):
        self.browser.visit(self.live_server_url + '/accounts/signup/')
        self.browser.find_by_name('username').fill('bob')
        self.browser.find_by_name('email').fill('bob@cultureplex.ca')
        self.browser.find_by_name('password1').fill('bob_secret')
        self.browser.find_by_name('password2').fill('bob_password')
        self.browser.find_by_value('Signup').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'The two password fields didn\'t match.')

    def test_user_signin(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        logout(self)

    def test_user_signin_empty_user(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.browser.find_by_name('identification').fill('')
        self.browser.find_by_name('password').fill('bob_secret')
        self.browser.find_by_xpath(
            "//div[@id='body']/div/form/input").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Either supply us with your email or username.')

    def test_user_signin_bad_user(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.browser.find_by_name('identification').fill('alice')
        self.browser.find_by_name('password').fill('bob_secret')
        self.browser.find_by_xpath(
            "//div[@id='body']/div/form/input").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Please enter a correct username or email and password. Note that both fields are case-sensitive.')

    def test_user_signin_empty_password(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('')
        self.browser.find_by_xpath(
            "//div[@id='body']/div/form/input").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')

    def test_user_signin_bad_password(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        self.browser.visit(self.live_server_url + '/accounts/signin/')
        self.browser.find_by_name('identification').fill('bob')
        self.browser.find_by_name('password').fill('alice_secret')
        self.browser.find_by_xpath(
            "//div[@id='body']/div/form/input").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Please enter a correct username or email and password. Note that both fields are case-sensitive.')

    def test_user_logout(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        logout(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Signed out')
        self.assertEqual(self.browser.find_by_css('.body-inside').first.value, 'You have been signed out. Till we meet again.')

    def test_user_details(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
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
        self.browser.find_by_name('institution').fill('University')
        self.browser.find_by_name('company').fill('CulturePlex')
        self.browser.find_by_name('lab').fill('CulturePlex')
        self.browser.find_by_value('Save changes').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        logout(self)

    def test_user_details_bad_website(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
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
        self.browser.find_by_name('website').fill('bobweb')
        self.browser.find_by_name('location').fill('London, Ontario')
        self.browser.find_by_name('birth_date').fill('01/01/1975')
        self.browser.find_by_name('about_me').fill('I am a very nice guy')
        self.browser.find_by_name('institution').fill('University')
        self.browser.find_by_name('company').fill('CulturePlex')
        self.browser.find_by_name('lab').fill('CulturePlex')
        self.browser.find_by_value('Save changes').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid URL.')
        logout(self)

    def test_user_details_bad_birthdate(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
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
        self.browser.find_by_name('birth_date').fill('birthdate')
        self.browser.find_by_name('about_me').fill('I am a very nice guy')
        self.browser.find_by_name('institution').fill('University')
        self.browser.find_by_name('company').fill('CulturePlex')
        self.browser.find_by_name('lab').fill('CulturePlex')
        self.browser.find_by_value('Save changes').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid date.')
        logout(self)

    def test_user_details_future_birthdate(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
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
        self.browser.find_by_name('birth_date').fill('2015-01-11')
        self.browser.find_by_name('about_me').fill('I am a very nice guy')
        self.browser.find_by_name('institution').fill('University')
        self.browser.find_by_name('company').fill('CulturePlex')
        self.browser.find_by_name('lab').fill('CulturePlex')
        self.browser.find_by_value('Save changes').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'You need to introduce a past date.')
        logout(self)

    def test_user_change_pass(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
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

    def test_user_change_pass_empty(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/password/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Change password')
        self.browser.find_by_name('old_password').fill('')
        self.browser.find_by_name('new_password1').fill('bob_password')
        self.browser.find_by_name('new_password2').fill('bob_password')
        self.browser.find_by_value('Change password').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')
        logout(self)

    def test_user_change_pass_incorrectly(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/password/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Change password')
        self.browser.find_by_name('old_password').fill('bad_password')
        self.browser.find_by_name('new_password1').fill('bob_password')
        self.browser.find_by_name('new_password2').fill('bob_password')
        self.browser.find_by_value('Change password').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Your old password was entered incorrectly. Please enter it again.')
        logout(self)

    def test_user_change_new_pass_empty(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/password/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Change password')
        self.browser.find_by_name('old_password').fill('bob_secret')
        self.browser.find_by_name('new_password1').fill('')
        self.browser.find_by_name('new_password2').fill('bob_password')
        self.browser.find_by_value('Change password').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')
        logout(self)

    def test_user_change_new_pass_unmatched(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/password/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Change password')
        self.browser.find_by_name('old_password').fill('bob_secret')
        self.browser.find_by_name('new_password1').fill('bob_password')
        self.browser.find_by_name('new_password2').fill('alice_password')
        self.browser.find_by_value('Change password').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'The two password fields didn\'t match.')
        logout(self)

    def test_user_change_mail(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/email/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Welcome to The Sylva Project')
        self.browser.find_by_name('email').fill('bobnew@cultureplex.ca')
        self.browser.find_by_value('Change email').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Email verification')

    def test_user_change_mail_empty(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/email/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Welcome to The Sylva Project')
        self.browser.find_by_name('email').fill('')
        self.browser.find_by_value('Change email').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')

    def test_user_change_bad(self):
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/accounts/bob/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - bob\'s profile.')
        self.browser.find_link_by_href('/accounts/bob/email/').first.click()
        self.assertEqual(self.browser.title, 'SylvaDB - Welcome to The Sylva Project')
        self.browser.find_by_name('email').fill('bobnewcultureplex.ca')
        self.browser.find_by_value('Change email').first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid e-mail address.')
