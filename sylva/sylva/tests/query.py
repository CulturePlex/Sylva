import socket
from time import sleep

from django.test import LiveServerTestCase

from splinter import Browser

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type

from utils import spin_assert


class QueryTestCase(LiveServerTestCase):
    """
    A set of tests for testing queries.
    """

    def setUp(self):
        self.browser = Browser()
        socket.setdefaulttimeout(30)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')

    def tearDown(self):
        logout(self)
        self.browser.quit()

    @classmethod
    def tearDownClass(cls):
        sleep(10)  # It needs some time for close the LiverServerTestCase
        super(QueryTestCase, cls).tearDownClass()

    def test_query_list_view(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        self.browser.find_by_id('queriesMenu').first.click()
        button_text = self.browser.find_by_id('create-query').first.value
        spin_assert(lambda: self.assertEqual(button_text, "New Query"))

    def test_query_builder_view(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        self.browser.find_by_id('queriesMenu').first.click()
        new_query_button = self.browser.find_by_id('create-query').first
        button_text = new_query_button.value
        spin_assert(lambda: self.assertEqual(button_text, "New Query"))
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type_text = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first.value
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text, "Bob's type"))

    def test_query_builder_add_box(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        self.browser.find_by_id('queriesMenu').first.click()
        new_query_button = self.browser.find_by_id('create-query').first
        button_text = new_query_button.value
        spin_assert(lambda: self.assertEqual(button_text, "New Query"))
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type_text = node_type.value
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text, "Bob's type"))
        # We check if the node type is the same
        node_type.click()
        title_text = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']").first.value
        spin_assert(lambda: self.assertEqual(title_text, u"Bob's type 1"))
