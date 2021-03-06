import os
import requests
import socket
from time import sleep

from zipfile import ZipFile
from StringIO import StringIO

from django.test import LiveServerTestCase

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type, create_data
from graphs.models import Graph

from utils import spin_assert, Browser


def create_node(test, name):
    """
    It creates a node of the 'only' type in the current node.
    """
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//a[@class='dataOption new']").first.click()
    text = test.browser.find_by_id('propertiesTitle').first.value
    spin_assert(lambda: test.assertEqual(text, 'Properties'))
    test.browser.find_by_name('Name').first.fill(name)
    test.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
    text = test.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
    spin_assert(lambda: test.assertNotEqual(
        text.find(" elements Bob's type."), -1))


class DataNodeTestCase(LiveServerTestCase):
    """
    A set of tests to test all interaction related to the creation and
    deletion of nodes and relationships. Also, we test export the data in two
    formats: gexf and csv.
    """

    def setUp(self):
        self.browser = Browser(firefox_path=os.getenv('FIREFOX_PATH', None))
        socket.setdefaulttimeout(30)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')

    def tearDown(self):
        logout(self)
        self.browser.quit()

    @classmethod
    def tearDownClass(cls):
        sleep(10)  # It needs some time for close the LiverServerTestCase
        super(DataNodeTestCase, cls).tearDownClass()

    def test_data_node_addition(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        # Check the node name
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a").first.click()
        self.browser.choose('confirm', '1')
        self.browser.find_by_value('Continue').first.click()
        text = self.browser.find_by_xpath("//div[@class='indent']/div").first.value
        Graph.objects.get(name="Bob's graph").destroy()
        spin_assert(lambda: self.assertEqual(text, 'Nodes: 0'))

    def test_data_node_addition_rel_add_del(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_node(self, "Bob")
        create_node(self, "Alice")
        # We create a allowed relation
        js_code = "$('a#schema-link')[0].click();"
        self.browser.execute_script(js_code)
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill("Bob's rel")
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill("This the allowed relationship for Bob's graph")
        self.browser.find_by_value('Save Type').first.click()
        spin_assert(lambda: self.assertEqual(
            self.browser.title, "SylvaDB - Bob's graph"))
        # We create the link between the nodes
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input").first.fill('Alice')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        # Delete the relationship
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//span[@class='all-relationships outgoing-relationships o_bobs_rel1-relationships']/span/a[@class='delete-row initial-form floating']").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        spin_assert(lambda: self.assertEqual(text, "0 relationships"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_node_type_deletion_keeping_nodes(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        # Adding relationship to the type
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill("Bob's rel")
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill(
            'The loved relationship')
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("Bob's rel"), -1))
        # Creating nodes
        create_node(self, 'Bob')
        create_node(self, 'Alice')
        # Creating relationship between nodes
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input").first.fill('Alice')
        self.browser.is_element_present_by_id("id_user_wait", wait_time=5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        spin_assert(lambda: self.assertEqual(text, "1 relationships"))
        # Deleting type
        js_code = "$('a#schema-link')[0].click();"
        self.browser.execute_script(js_code)
        self.browser.find_by_xpath("//fieldset[@class='module aligned wide model']/h2/a").first.click()
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a[@class='delete']").first.click()
        text = self.browser.find_by_xpath(
            "//p/label[@for='id_option_0']").first.value
        spin_assert(lambda: self.assertNotEqual(text.find(
            "We found some elements of this type"), -1))
        # Keeping nodes
        self.browser.choose('option', 'no')
        self.browser.find_by_value('Continue').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='body-inside']/p").first.value
        spin_assert(lambda: self.assertEqual(
            text, 'There are no types defined yet.'))
        # Checking
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        spin_assert(lambda: self.assertEqual(text, "2 nodes"))
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        spin_assert(lambda: self.assertEqual(text, "1 relationships"))
        text = self.browser.find_by_xpath(
            "//div[@class='graph-empty-message']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find("Your Schema is empty."), -1))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_node_type_deletion_deleting_nodes(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        # Adding relationship to the type
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill("Bob's rel")
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill(
            'The loved relationship')
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("Bob's rel"), -1))
        # Creating nodes
        create_node(self, 'Bob')
        create_node(self, 'Alice')
        # Creating relationship between nodes
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input").first.fill('Alice')
        self.browser.is_element_present_by_id("id_user_wait", wait_time=5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        spin_assert(lambda: self.assertEqual(text, "1 relationships"))
        # Deleting type
        js_code = "$('a#schema-link')[0].click();"
        self.browser.execute_script(js_code)
        self.browser.find_by_xpath("//fieldset[@class='module aligned wide model']/h2/a").first.click()
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a[@class='delete']").first.click()
        text = self.browser.find_by_xpath(
            "//p/label[@for='id_option_0']").first.value
        spin_assert(lambda: self.assertNotEqual(text.find(
            "We found some elements of this type"), -1))
        # Deleting nodes
        self.browser.choose('option', 'de')
        self.browser.find_by_value('Continue').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='body-inside']/p").first.value
        spin_assert(lambda: self.assertEqual(
            text, 'There are no types defined yet.'))
        # Checking
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        spin_assert(lambda: self.assertEqual(text, "0 nodes"))
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        spin_assert(lambda: self.assertEqual(text, "0 relationships"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_data_node_clone(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        original_name = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[1].value
        # Clone the node
        self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td/a[@class='edit']").first.click()
        self.browser.find_by_name('Name').first.fill(original_name + " clone")
        self.browser.find_by_name("as-new").first.click()
        # Check that two nodes exist
        original_name = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[1].value
        clone_name = self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td")[4].value
        spin_assert(lambda: self.assertEqual(original_name, "Bob's node"))
        spin_assert(lambda: self.assertEqual(clone_name, "Bob's node clone"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_sigma_visualization_in_node_view(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        # Adding relationship to the type
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill("Bob's rel")
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill(
            'The loved relationship')
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("Bob's rel"), -1))
        # Creating nodes
        create_node(self, 'Bob')
        create_node(self, 'Alice')
        # Creating relationship between nodes
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input").first.fill('Alice')
        self.browser.is_element_present_by_id("id_user_wait", wait_time=5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        # Checking
        self.browser.find_by_xpath("//table[@id='content_table']/tbody/tr/td/a[@title='View node']/p[text()='Alice']").first.click()
        self.browser.is_element_present_by_id('wait_for_js', 3)
        js_code = '''
            var instance = sigma.instances(0);
            sylva.test_node_count = instance.graph.nodes().length;
            '''
        self.browser.execute_script(js_code)
        text = self.browser.evaluate_script('sylva.test_node_count')
        spin_assert(lambda: self.assertEqual(text, 2))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_graph_export_gexf(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        self.browser.find_by_id('toolsMenu').first.click()
        cookies = {self.browser.cookies.all()[0]["name"]: self.browser.cookies.all()[0]["value"], self.browser.cookies.all()[1]["name"]: self.browser.cookies.all()[1]["value"]}
        result = requests.get(self.live_server_url + '/tools/bobs-graph/export/gexf/', cookies=cookies)
        spin_assert(lambda: self.assertEqual(
            result.headers['content-type'], 'application/xml'))
        spin_assert(lambda: self.assertEqual(
            self.browser.status_code.is_success(), True))
        fw = open('sylva/sylva/tests/files/bobs-graph.gexf', 'w')
        fw.write(result.content)
        fw.close()
        f = open('sylva/sylva/tests/files/bobs-graph.gexf')
        xmlFile = ""
        for line in f:
            xmlFile += line
        f.close()
        spin_assert(lambda: self.assertEqual(xmlFile, result.content))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_graph_export_csv(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        self.browser.find_by_id('toolsMenu').first.click()
        cookies = {self.browser.cookies.all()[0]["name"]: self.browser.cookies.all()[0]["value"], self.browser.cookies.all()[1]["name"]: self.browser.cookies.all()[1]["value"]}
        result = requests.get(self.live_server_url + '/tools/bobs-graph/export/csv/', cookies=cookies)
        spin_assert(lambda: self.assertEqual(
            result.headers['content-type'], 'application/zip'))
        spin_assert(lambda: self.assertEqual(
            self.browser.status_code.is_success(), True))
        test_file = StringIO(result.content)
        csv_zip = ZipFile(test_file)
        for name in csv_zip.namelist():
            fw = open('sylva/sylva/tests/files/' + name, 'w')
            fw.write(csv_zip.read(name))
            fw.close()
        for name in csv_zip.namelist():
            f = open('sylva/sylva/tests/files/' + name)
            csvFile = ""
            for line in f:
                csvFile += line
            f.close()
            spin_assert(lambda: self.assertEqual(csv_zip.read(name), csvFile))
        Graph.objects.get(name="Bob's graph").destroy()
