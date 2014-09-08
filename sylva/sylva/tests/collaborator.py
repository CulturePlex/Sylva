import socket

from django.test import LiveServerTestCase

from splinter import Browser

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type, create_data
from graphs.models import Graph

from utils import spin_assert

GRAPH_VIEW = 'chk_graph_view_graph'
GRAPH_CHANGE = 'chk_graph_change_graph'
SCHEMA_VIEW = 'chk_schema_view_schema'
SCHEMA_CHANGE = 'chk_schema_change_schema'
DATA_VIEW = 'chk_data_view_data'
DATA_CHANGE = 'chk_data_change_data'
DATA_ADD = 'chk_data_add_data'
DATA_DELETE = 'chk_data_delete_data'
CREATE_COLLAB = GRAPH_VIEW


def create_collaborator(test, username):
    """
    It creates a collaborator. For use it inside change_permission().
    """
    test.browser.find_by_xpath(
        "//div[@id='id_new_collaborator_chzn']/a").first.click()
    test.browser.find_by_xpath("//div[@class='chzn-drop']/div[@class='chzn-search']/input").first.fill(username)
    test.browser.is_element_present_by_xpath('//body', wait_time=1)
    test.browser.find_by_xpath("//div[@class='chzn-drop']/ul[@class='chzn-results']/li[text()='" + username + "']").first.click()
    test.browser.find_by_xpath(
        "//div[@id='content2']/div/form/input")[1].click()


def add_permission(test, username, permission):
    """
    Add the pemission to the referenced use in the graph that we are viewing.
    """
    test.browser.find_by_xpath(
        "//nav[@class='menu']/ul/li[4]/a").first.click()
    if permission is CREATE_COLLAB:
        create_collaborator(test, username)
    else:
        test.browser.find_by_xpath("//tr/td/a[text()='" + username + "']/../../td/input[@id='" + permission + "']").first.click()


class CollaboratorTestCase(LiveServerTestCase):
    """
    These tests check the permissions system creating two users: one creates a
    graph and gives permissions to the other, the other tests the permissions
    given.
    On these tests, is the developer who must keep the logic of the
    permissions. If he/she wants to give any permission to an user he/she must
    first creates the usar and then creates the collaboration adding the basic
    perrmission: 'chk_graph_view_graph'.
    The name of the tests self-explain the behaviour of them.
    """

    @classmethod
    def setUpClass(cls):
        cls.browser = Browser()
        socket.setdefaulttimeout(30)
        super(CollaboratorTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(CollaboratorTestCase, cls).tearDownClass()

    def setUp(self):
        pass

    def tearDown(self):
        logout(self)

    def test_graph_view_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        self.browser.find_by_xpath("//div[@class='dashboard-graphs']/div/div/span[@class='graph-title']/a").first.click()
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.visit(self.live_server_url + '/graphs/bobs-graph/')
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_graph_view_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        self.browser.find_by_xpath("//div[@class='dashboard-graphs']/div/div/span[@class='graph-title']/a").first.click()
        add_permission(self, 'alice', CREATE_COLLAB)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='graph-item']/span[@class='graph-title']/a").first.value
        spin_assert(lambda: self.assertEqual(text, "Bob's graph"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_graph_change_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        self.browser.find_by_xpath("//div[@class='dashboard-graphs']/div/div/span[@class='graph-title']/a").first.click()
        add_permission(self, 'alice', CREATE_COLLAB)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//div[@class='graph-item']/span[@class='graph-title']/a").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_graph_change_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        self.browser.find_by_xpath("//div[@class='dashboard-graphs']/div/div/span[@class='graph-title']/a").first.click()
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', GRAPH_CHANGE)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//div[@class='graph-item']/span[@class='graph-title']/a").first.click()
        self.browser.find_by_xpath(
            "//input[@id='id_name']").first.fill("Alice's graph")
        self.browser.find_by_xpath(
            "//form/input[@type='submit']").first.click()
        text = self.browser.find_by_xpath("//div[@class='graph-item']/span[@class='graph-title']/a").first.value
        spin_assert(lambda: self.assertEqual(text, "Alice's graph"))
        Graph.objects.get(name="Alice's graph").destroy()

    def test_schema_view_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath(
            "//nav[@class='menu']/ul/li[3]/a").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_schema_view_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', SCHEMA_VIEW)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath(
            "//nav[@class='menu']/ul/li[3]/a").first.click()
        text = self.browser.find_by_xpath(
            "//fieldset[@class='module aligned wide model']/h2/a").first.value
        spin_assert(lambda: self.assertEqual(text, "Bob's type"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_schema_change_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', SCHEMA_VIEW)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath(
            "//nav[@class='menu']/ul/li[3]/a").first.click()
        self.browser.find_by_xpath("//fieldset[@class='module aligned wide model']/h2/a").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_schema_change_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', SCHEMA_VIEW)
        add_permission(self, 'alice', SCHEMA_CHANGE)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath(
            "//nav[@class='menu']/ul/li[3]/a").first.click()
        self.browser.find_by_xpath("//fieldset[@class='module aligned wide model']/h2/a").first.click()
        self.browser.find_by_xpath(
            "//input[@id='id_name']").first.fill("Alice's type")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input[@type='submit']").first.click()
        text = self.browser.find_by_xpath(
            "//fieldset[@class='module aligned wide model']/h2/a").first.value
        spin_assert(lambda: self.assertEqual(text, "Alice's type"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_view_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_view_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        text = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[1].value
        spin_assert(lambda: self.assertEqual(text, "Bob's node"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_change_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td/a[@title='Edit node']").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_change_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        add_permission(self, 'alice', DATA_CHANGE)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td/a[@title='Edit node']").first.click()
        self.browser.find_by_xpath(
            "//input[@id='id_Name']").first.fill("Alice's node")
        self.browser.find_by_xpath("//input[@type='submit']").first.click()
        text = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[1].value
        spin_assert(lambda: self.assertEqual(text, "Alice's node"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_add_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption new']").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_add_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        add_permission(self, 'alice', DATA_ADD)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption new']").first.click()
        self.browser.find_by_xpath(
            "//input[@id='id_Name']").first.fill("Alice's node")
        self.browser.find_by_xpath("//input[@type='submit']").first.click()
        text = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[1].value
        spin_assert(lambda: self.assertEqual(text, "Alice's node"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_delete_without_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        add_permission(self, 'alice', DATA_CHANGE)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td/a[@title='Edit node']").first.click()
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a[text()='Remove']").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='heading']/h1").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("403"), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_delete_with_permissions(self):
        signup(self, 'alice', 'alice@cultureplex.ca', 'alice_secret')
        signin(self, 'alice', 'alice_secret')
        logout(self)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        add_permission(self, 'alice', CREATE_COLLAB)
        add_permission(self, 'alice', DATA_VIEW)
        add_permission(self, 'alice', DATA_CHANGE)
        add_permission(self, 'alice', DATA_DELETE)
        logout(self)
        signin(self, 'alice', 'alice_secret')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_xpath("//a[@id='dataMenu']").first.click()
        self.browser.find_by_xpath("//div[@id='dataBrowse']/table/tbody/tr/td/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td/a[@title='Edit node']").first.click()
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a[text()='Remove']").first.click()
        self.browser.choose('confirm', '1')
        self.browser.find_by_xpath("//input[@type='submit']").first.click()
        text = self.browser.find_by_xpath(
            "//div[@id='content2']/div[@class='indent']").first.value
        spin_assert(lambda: self.assertNotEqual(text.find('Nodes: 0'), -1))
        Graph.objects.get(name="Bob's graph").destroy()
