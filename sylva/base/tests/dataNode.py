import requests

from django.test import LiveServerTestCase

from splinter import Browser

from user import signin, logout
from dashboard import create_graph, create_schema, create_type, create_data


def create_node(test, name):
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//a[@class='dataOption new']").first.click()
    text = test.browser.find_by_id('propertiesTitle').first.value
    test.assertEqual(text, 'Properties')
    test.browser.find_by_name('Name').first.fill(name)
    test.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
    text = test.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
    # The next line must be more 'specific' when we can destroy Neo4j DBs
    test.assertNotEqual(text.find(" elements Bob's type."), -1)


class DataNodeTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = Browser('phantomjs')
        signin(self)

    def tearDown(self):
        logout(self)
        self.browser.quit()

    def test_data_node_addition(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        # Check the node name
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        self.assertEqual(text, 'Properties')
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a").first.click()
        self.browser.choose('confirm', '1')
        self.browser.find_by_value('Continue').first.click()
        text = self.browser.find_by_xpath("//div[@class='indent']/div").first.value
        self.assertEqual(text, 'Nodes: 0')

    def test_data_node_addition_rel_add_del(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_node(self, "Bob")
        create_node(self, "John")
        # We create a allowed relation
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('Bob\'s rel')
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill('This the allowed relationship for Bob\'s graph')
        self.browser.find_by_value('Save Type').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        # We create the link between the nodes
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input").first.fill('John')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        self.browser.find_by_value('Save Bob\'s type').first.click()
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('visualization-type').first.click()
        self.browser.find_by_id('visualization-sigma').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(text, "1 relationships")
        # Delete the relationship
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption list']").first.click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        #import ipdb; ipdb.set_trace();
        self.browser.find_by_xpath("//span[@class='all-relationships outgoing-relationships o_bobs_rel1_1-relationships']//a[@class='delete-row initial-form floating']").first.click()
        self.browser.find_by_value('Save Bob\'s type').first.click()
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('visualization-type').first.click()
        self.browser.find_by_id('visualization-sigma').first.click()
        text = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(text, "0 relationships")

    def test_graph_export_gexf(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        self.browser.find_by_id('toolsMenu').first.click()
        cookies = {self.browser.cookies.all()[0]["name"]: self.browser.cookies.all()[0]["value"], self.browser.cookies.all()[1]["name"]: self.browser.cookies.all()[1]["value"]}
        result = requests.get(self.live_server_url + '/tools/bobs-graph/export/gexf/', cookies=cookies)
        self.assertEqual(result.headers['content-type'], 'application/xml')
        self.assertEqual(self.browser.status_code.is_success(), True)
        f = open('sylva/base/tests/bobs-graph.gexf')
        xmlFile = ""
        for line in f:
            xmlFile += line
        f.close()
        # import ipdb; ipdb.set_trace();
        self.assertEqual(xmlFile, result.content + "\n")

    def test_graph_export_csv(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        self.browser.find_by_id('toolsMenu').first.click()
        cookies = {self.browser.cookies.all()[0]["name"]: self.browser.cookies.all()[0]["value"], self.browser.cookies.all()[1]["name"]: self.browser.cookies.all()[1]["value"]}
        result = requests.get(self.live_server_url + '/tools/bobs-graph/export/csv/', cookies=cookies)
        self.assertEqual(result.headers['content-type'], 'application/zip')
        self.assertEqual(self.browser.status_code.is_success(), True)
        # import ipdb; ipdb.set_trace();
        f = open('sylva/base/tests/bobs-graph.zip')
        # We need to check the zip format
        self.assertEqual(f.read(), result.content)
