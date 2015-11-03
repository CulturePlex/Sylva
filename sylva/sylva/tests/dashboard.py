import os
import socket
from time import sleep

from django.test import LiveServerTestCase

from user import signup, signin, logout
from graphs.models import Graph

from utils import spin_assert, Browser


def create_graph(test):
    test.browser.visit(test.live_server_url + '/graphs/create/')
    text = test.browser.find_by_xpath(
        "//header[@class='global']/h2").first.value
    spin_assert(lambda: test.assertNotEqual(text.find('Create New Graph'), -1))
    test.browser.find_by_name('name').first.fill("Bob's graph")
    test.browser.find_by_xpath(
        "//form[@name='graphs_create']/p/textarea[@name='description']").first.fill('The loved graph')
    test.browser.find_by_name('addGraph').first.click()
    text = test.browser.find_by_xpath(
        "//header[@class='global']/h1").first.value
    spin_assert(lambda: test.assertEqual(text, 'Dashboard'))
    text = test.browser.find_link_by_href(
        '/graphs/bobs-graph/').first.value
    spin_assert(lambda: test.assertEqual(text, "Bob's graph"))


def create_schema(test):
    """
    This function only navigates to the schema section of the graph.
    """
    test.browser.find_link_by_href(
        '/graphs/bobs-graph/').first.click()
    spin_assert(lambda: test.assertEqual(test.browser.title,
                                         "SylvaDB - Bob's graph"))
    js_code = "$('a#schema-link')[0].click();"
    test.browser.execute_script(js_code)
    text = test.browser.find_by_xpath(
        "//div[@class='body-inside']/p").first.value
    spin_assert(lambda: test.assertEqual(text,
                                         'There are no types defined yet.'))


def create_type(test):
    """
    For use it after create_schema(). It creates a simple type in the schema.
    """
    test.browser.find_link_by_href(
        '/schemas/bobs-graph/types/create/').first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='content2-first']/h2").first.value
    spin_assert(lambda: test.assertEqual(text, 'Type'))
    test.browser.find_by_name('name').first.fill("Bob's type")
    test.browser.find_by_xpath(
        "//div[@class='content2-first']/p/textarea[@name='description']").first.fill('The loved type')
    test.browser.find_by_name('properties-0-key').first.fill('Name')
    test.browser.find_by_name('properties-0-display').first.check()
    test.browser.find_by_value('Save Type').first.click()
    text = test.browser.find_by_id(
        'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
    spin_assert(lambda: test.assertEqual(text, "Name"))


def create_data(test):
    """
    For use it after create_type(). It cretes a simple node with schema created
    previously.
    """
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//a[@class='dataOption new']").first.click()
    text = test.browser.find_by_id('propertiesTitle').first.value
    spin_assert(lambda: test.assertEqual(text, 'Properties'))
    test.browser.find_by_name('Name').first.fill("Bob's node")
    test.browser.find_by_value("Save Bob's type").first.click()
    text = test.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
    spin_assert(lambda: test.assertNotEqual(
        text.find(" elements Bob's type."), -1))


class DashboardTestCase(LiveServerTestCase):
    """
    These tests check basic functions of Sylva's dashboard.
    """

    def setUp(self):
        self.browser = Browser(firefox_path=os.getenv('FIREFOX_PATH', None))
        socket.setdefaulttimeout(30)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')

    def tearDown(self):
        logout(self)
        self.browser.quit()

    @classmethod
    def tearDownClass(cls):
        sleep(10)  # It needs some time for close the LiverServerTestCase
        super(DashboardTestCase, cls).tearDownClass()

    def test_dashboard(self):
        signin(self, 'bob', 'bob_secret')
        spin_assert(lambda: self.assertEquals(self.browser.title,
                                              'SylvaDB - Dashboard'))
        text = self.browser.find_by_xpath(
            "//header[@class='global']/h1").first.value
        spin_assert(lambda: self.assertEqual(text, 'Dashboard'))

    def test_dashboard_new_graph(self):
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_dashboard_graph_preview(self):
        """
        This test, after create a graph with data, checks the Sigma
        visualization running a simple JavaScript code. This code gets the
        current instance of Sigma and checks the data with Sylva JavaScript
        object.
        """
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.is_element_present_by_id('wait_for_js', 3)
        js_code = '''
            var instance = sigma.instances(0);
            var node = instance.graph.nodes()[0];
            sylva.test_node_name = node.properties.Name;
            '''
        self.browser.execute_script(js_code)
        text = self.browser.evaluate_script('sylva.test_node_name')
        Graph.objects.get(name="Bob's graph").destroy()
        spin_assert(lambda: self.assertNotEqual(text.find("Bob's node"), -1))

    def test_automatic_tour(self):
        """
        Thist test checks that the tour starts automatically after signup, only
        once.
        """
        self.browser.is_element_present_by_id('wait_for_cookie_tour', 3)
        signin(self, 'bob', 'bob_secret')
        exist = self.browser.is_element_present_by_xpath(
            "//div[@class='joyride-content-wrapper']")
        spin_assert(lambda: self.assertEqual(exist, True))
        self.browser.visit(self.live_server_url + '/dashboard/')
        exist = self.browser.is_element_present_by_xpath(
            "//div[@class='joyride-content-wrapper']")
        spin_assert(lambda: self.assertNotEqual(exist, True))
