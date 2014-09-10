import os
import requests
import socket
from time import sleep

from django.test import LiveServerTestCase

from splinter import Browser

from sylva.tests.user import signup, signin, logout
from graphs.models import Graph

from utils import spin_assert


def create_graph(test, name):
    """
    Create a graph with the name passed by parameter
    """
    test.browser.visit(test.live_server_url + '/graphs/create/')
    text = test.browser.find_by_xpath(
        "//header[@class='global']/h2").first.value
    spin_assert(lambda: test.assertNotEqual(text.find('Create New Graph'), -1))
    spin_assert(lambda: test.assertEqual(text, 'Create New Graph'))
    test.browser.find_by_name('name').first.fill(name)
    test.browser.find_by_xpath(
        "//form[@name='graphs_create']/p/textarea[@name='description']").first.fill('The loved graph')
    test.browser.find_by_name('addGraph').first.click()
    text = test.browser.find_by_xpath(
        "//header[@class='global']/h1").first.value
    spin_assert(lambda: test.assertEqual(text, 'Dashboard'))
    text = test.browser.find_link_by_href(
        '/graphs/' + name + '/').first.value
    spin_assert(lambda: test.assertEqual(text, name))


def create_advanced_schema(test, name):
    """
    Create a schema for the graph. The name of the graph
    is passed by parameter.
    """
    test.browser.find_link_by_href(
        '/graphs/' + name + '/').first.click()
    test.browser.is_text_present('Your Schema is empty.')
    spin_assert(lambda: test.assertEqual(test.browser.title, "SylvaDB - " + name))
    test.browser.find_link_by_href(
        '/schemas/' + name + '/').first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='body-inside']/p").first.value
    spin_assert(lambda: test.assertEqual(text,
                                         'There are no types defined yet.'))


def create_advanced_type(test, name, datatype):
    """
    Create a type for the graph. The name of the graph
    is passed by parameter and the datatype too.
    """
    test.browser.find_link_by_href(
        '/schemas/' + name + '/types/create/').first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='content2-first']/h2").first.value
    spin_assert(lambda: test.assertEqual(text, 'Type'))
    test.browser.find_by_name('name').first.fill("Bob's type")
    test.browser.find_by_xpath(
        "//div[@class='content2-first']/p/textarea[@name='description']").first.fill('The loved type')
    test.browser.find_by_name('properties-0-key').first.fill('Name')
    test.browser.find_by_name('properties-0-display').first.check()
    test.browser.find_by_id('advancedModeButton').first.click()
    test.browser.find_by_xpath("//optgroup[@label='Auto']/option[@value='" + datatype + "']").first.click()
    test.browser.find_by_value('Save Type').first.click()
    text = test.browser.find_by_id(
        'diagramBoxField_bobgraph.bobs-type.undefined').first.value
    spin_assert(lambda: test.assertEqual(text, "Name"))


def create_advanced_type_and_relationship(test, name, datatype):
    """
    Create a type for the graph. The name of the graph
    is passed by parameter and the datatype too.
    """
    test.browser.find_link_by_href(
        '/schemas/' + name + '/types/create/').first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='content2-first']/h2").first.value
    spin_assert(lambda: test.assertEqual(text, 'Type'))
    test.browser.find_by_name('name').first.fill("Bob's type")
    test.browser.find_by_xpath(
        "//div[@class='content2-first']/p/textarea[@name='description']").first.fill('The loved type')
    test.browser.find_by_name('properties-0-key').first.fill('Name')
    test.browser.find_by_name('properties-0-display').first.check()
    test.browser.find_by_id('advancedModeButton').first.click()
    test.browser.find_by_xpath("//optgroup[@label='Auto']/option[@value='" + datatype + "']").first.click()
    test.browser.find_by_value('Save Type').first.click()
    text = test.browser.find_by_id(
        'diagramBoxField_bobgraph.bobs-type.undefined').first.value
    spin_assert(lambda: test.assertEqual(text, "Name"))
    # We create a relationship
    test.browser.find_by_id('allowedRelations').first.click()


def create_advanced_data(test):
    """
    Create advanced data for the graph.
    """
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//a[@class='dataOption new']").first.click()
    text = test.browser.find_by_id('propertiesTitle').first.value
    spin_assert(lambda: test.assertEqual(text, 'Properties'))
    test.browser.find_by_value("Save Bob's type").first.click()
    text = test.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
    # The next line must be more 'specific' when we can destroy Neo4j DBs
    spin_assert(lambda: test.assertNotEqual(
        text.find(" elements Bob's type."), -1))


def export_advanced_schema(test, name):
    """
    Export the schema for one graph. The name of the graph
    is passed by parameter.
    """
    test.browser.find_by_id('toolsMenu').first.click()
    cookies = {test.browser.cookies.all()[0]["name"]: test.browser.cookies.all()[0]["value"], test.browser.cookies.all()[1]["name"]: test.browser.cookies.all()[1]["value"]}
    result = requests.get(test.live_server_url + '/schemas/' + name + '/export/', cookies=cookies)
    spin_assert(lambda: test.assertEqual(
        result.headers['content-type'], 'application/json'))
    spin_assert(lambda: test.assertEqual(
        test.browser.status_code.is_success(), True))
    fw = open('sylva/sylva/tests/files/gexf/' + name + '_schema.json', 'w')
    fw.write(result.content)
    fw.close()
    f = open('sylva/sylva/tests/files/gexf/' + name + '_schema.json')
    spin_assert(lambda: test.assertEqual(
        f.read().split("\n")[0], result.content))


def import_advanced_schema(test, name_export, name_import):
    """
    Import the schema for one graph. The parameters are the name of
    the graph to import and the graph from import.
    """
    create_graph(test, name_import)
    spin_assert(lambda: test.assertEqual(
        test.browser.title, 'SylvaDB - Dashboard'))
    test.browser.find_link_by_href('/graphs/' + name_import + '/').first.click()
    test.browser.is_text_present('Your Schema is empty.')
    spin_assert(lambda: test.assertEqual(
        test.browser.title, "SylvaDB - " + name_import))
    test.browser.find_link_by_href('/schemas/' + name_import + '/').first.click()
    spin_assert(lambda: test.assertEqual(
        test.browser.title, "SylvaDB - " + name_import))
    test.browser.find_by_id('schemaImport').first.click()
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'files/gexf/bobgraph_schema.json'
    )
    test.browser.attach_file('file', file_path)
    test.browser.find_by_value('Continue').first.click()
    spin_assert(lambda: test.assertEqual(
        test.browser.title, "SylvaDB - " + name_import))
    text = test.browser.find_by_id('diagramBoxField_' + name_import + '.bobs-type-2.undefined').first.value
    spin_assert(lambda: test.assertEqual(text, "Name"))


def import_advanced_schema_csv(test, name_export, name_import):
    """
    Import the schema for one graph. The parameters are the name of
    the graph to import and the graph from import. Csv format.
    """
    create_graph(test, name_import)
    spin_assert(lambda: test.assertEqual(
        test.browser.title, 'SylvaDB - Dashboard'))
    test.browser.find_link_by_href('/graphs/' + name_import + '/').first.click()
    test.browser.is_text_present('Your Schema is empty.')
    spin_assert(lambda: test.assertEqual(
        test.browser.title, "SylvaDB - " + name_import))
    test.browser.find_link_by_href(
        '/schemas/' + name_import + '/').first.click()
    spin_assert(lambda: test.assertEqual(test.browser.title, "SylvaDB - " + name_import))
    test.browser.find_by_id('schemaImport').first.click()
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'files/csv/bobgraph_rel_schema.json'
    )
    test.browser.attach_file('file', file_path)
    test.browser.find_by_value('Continue').first.click()
    spin_assert(lambda: test.assertEqual(test.browser.title, "SylvaDB - " + name_import))
    text = test.browser.find_by_id('diagramBoxField_' + name_import + '.bobs-type-2.undefined').first.value
    spin_assert(lambda: test.assertEqual(text, "Name"))


def data_export_gexf(test):
    test.browser.find_by_id('toolsMenu').first.click()
    cookies = {test.browser.cookies.all()[0]["name"]: test.browser.cookies.all()[0]["value"], test.browser.cookies.all()[1]["name"]: test.browser.cookies.all()[1]["value"]}
    result = requests.get(test.live_server_url + '/tools/bobgraph/export/gexf/', cookies=cookies)
    spin_assert(lambda: test.assertEqual(
        result.headers['content-type'], 'application/xml'))
    spin_assert(lambda: test.assertEqual(
        test.browser.status_code.is_success(), True))
    fw = open('sylva/sylva/tests/files/gexf/bobs-graph.gexf', 'w')
    fw.write(result.content)
    fw.close()
    f = open('sylva/sylva/tests/files/gexf/bobs-graph.gexf')
    xmlFile = ""
    for line in f:
        xmlFile += line
    f.close()
    spin_assert(lambda: test.assertEqual(xmlFile, result.content))


def data_import_gexf(test):
    test.browser.find_by_id('toolsMenu').first.click()
    test.browser.find_link_by_href('/tools/' + test.secondGraphName + '/import/').first.click()
    test.browser.find_by_id('gexf-radio').first.click()
    # Change the display field of input to attach the file
    script = """
                $('#files').css('display', '');
             """
    test.browser.execute_script(script)
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'files/gexf/bobs-graph.gexf'
    )
    test.browser.attach_file('file', file_path)
    # Wait until the data is imported
    test.browser.is_text_present('Data uploaded.', wait_time=10)
    # Check that nodes and relationships are ok
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath("//a[@class='dataOption list']").first.click()


class ToolsTestCaseGexf(LiveServerTestCase):
    """
    A master test to check the behaviour of the new 'auto' fields.
    Actually only works with gephi format.
    """

    def setUp(self):
        self.browser = Browser()
        socket.setdefaulttimeout(30)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.firstGraphName = "bobgraph"
        self.secondGraphName = "alicegraph"

    def tearDown(self):
        logout(self)
        self.browser.quit()

    @classmethod
    def tearDownClass(cls):
        sleep(10)  # It needs some time for close the LiverServerTestCase
        super(ToolsTestCaseGexf, cls).tearDownClass()

    def test_graph_export_gexf_autoincrement(self):
        # Create a graph with an auto_increment property
        create_graph(self, self.firstGraphName)
        create_advanced_schema(self, self.firstGraphName)
        create_advanced_type(self, self.firstGraphName, "i")
        create_advanced_data(self)
        # Schema export
        export_advanced_schema(self, self.firstGraphName)
        # Data export in gexf format
        data_export_gexf(self)
        # Create new graph for import the data
        import_advanced_schema(self, self.firstGraphName, self.secondGraphName)
        # Data import
        data_import_gexf(self)
        bobgraph = Graph.objects.get(name=self.firstGraphName)
        alicegraph = Graph.objects.get(name=self.secondGraphName)
        alicegraphNodes = alicegraph.nodes.count()
        spin_assert(lambda: self.assertEqual(
            bobgraph.nodes.count(), alicegraph.nodes.count()))
        spin_assert(lambda: self.assertEqual(
            bobgraph.relationships.count(), alicegraph.relationships.count()))
        # We store the auto value to compare later
        alice_type = alicegraph.schema.nodetype_set.get()
        alice_properties = alice_type.properties.values()[0]
        alice_auto = alice_properties['auto']
        # Add new nodes and relationships and check all is correct
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        spin_assert(lambda: self.assertEqual(
            alicegraphNodes + 1, alicegraph.nodes.count()))
        # We check the new value for auto
        alice_type_new = alicegraph.schema.nodetype_set.get()
        alice_properties_new = alice_type_new.properties.values()[0]
        alice_auto_new = alice_properties_new['auto']
        spin_assert(lambda: self.assertEqual(alice_auto + 1, alice_auto_new))
        # Destroy the databases
        Graph.objects.get(name=self.firstGraphName).destroy()
        Graph.objects.get(name=self.secondGraphName).destroy()

    '''
    def test_graph_export_gexf_autonow(self):
        # Create a graph with an auto_increment property
        create_graph(self, self.firstGraphName)
        create_advanced_schema(self, self.firstGraphName)
        create_advanced_type(self, self.firstGraphName, "a")
        create_advanced_data(self)
        # Schema export
        export_advanced_schema(self, self.firstGraphName)
        # Data export in gexf format
        data_export_gexf(self)
        # Create new graph for import the data
        import_advanced_schema(self, self.firstGraphName, self.secondGraphName)
        # Data import
        data_import_gexf(self)
        bobgraph = Graph.objects.get(name=self.firstGraphName)
        alicegraph = Graph.objects.get(name=self.secondGraphName)
        alicegraphNodes = alicegraph.nodes.count()
        spin_assert(lambda: self.assertEqual(
            bobgraph.nodes.count(), alicegraph.nodes.count()))
        spin_assert(lambda: self.assertEqual(
            bobgraph.relationships.count(), alicegraph.relationships.count()))
        # We store the auto now value to compare
        auto_now_date_bob = ""
        auto_now_date_alice = ""
        for node in bobgraph.nodes.all():
            auto_now_date_bob = node.properties.values()[0]
        for node in alicegraph.nodes.all():
            auto_now_date_alice = node.properties.values()[0]
        spin_assert(lambda: self.assertEqual(
            auto_now_date_bob, auto_now_date_alice))
        # Add new nodes and relationships and check all is correct
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        spin_assert(lambda: self.assertEqual(
            alicegraphNodes + 1, alicegraph.nodes.count()))
        # Destroy the databases
        Graph.objects.get(name=self.firstGraphName).destroy()
        Graph.objects.get(name=self.secondGraphName).destroy()
    '''

    def test_graph_export_gexf_autouser(self):
        # Create a graph with an auto_increment property
        create_graph(self, self.firstGraphName)
        create_advanced_schema(self, self.firstGraphName)
        create_advanced_type(self, self.firstGraphName, "e")
        create_advanced_data(self)
        # Schema export
        export_advanced_schema(self, self.firstGraphName)
        # Data export in gexf format
        data_export_gexf(self)
        # Create new graph for import the data
        import_advanced_schema(self, self.firstGraphName, self.secondGraphName)
        # Data import
        data_import_gexf(self)
        bobgraph = Graph.objects.get(name=self.firstGraphName)
        alicegraph = Graph.objects.get(name=self.secondGraphName)
        alicegraphNodes = alicegraph.nodes.count()
        spin_assert(lambda: self.assertEqual(
            bobgraph.nodes.count(), alicegraph.nodes.count()))
        spin_assert(lambda: self.assertEqual(
            bobgraph.relationships.count(), alicegraph.relationships.count()))
        # Add new nodes and relationships and check all is correct
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        spin_assert(lambda: self.assertEqual(
            alicegraphNodes + 1, alicegraph.nodes.count()))
        # Destroy the databases
        Graph.objects.get(name=self.firstGraphName).destroy()
        Graph.objects.get(name=self.secondGraphName).destroy()


class ToolsTestCaseCsv(LiveServerTestCase):
    """
    A master test to check the behaviour of the new 'auto' fields.
    Actually only works with gephi format.
    """

    def setUp(self):
        self.browser = Browser()
        socket.setdefaulttimeout(30)
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')
        self.firstGraphName = "bobgraph"
        self.secondGraphName = "alicegraph"

    def tearDown(self):
        logout(self)
        self.browser.quit()

    @classmethod
    def tearDownClass(cls):
        sleep(10)  # It needs some time for close the LiverServerTestCase
        super(ToolsTestCaseCsv, cls).tearDownClass()

    def test_graph_export_csv(self):
        # Create a graph with a auto_user property
        create_graph(self, self.firstGraphName)
        create_advanced_schema(self, self.firstGraphName)
        create_advanced_type(self, self.firstGraphName, "e")
        create_advanced_data(self)
        # Create new graph for import the data
        import_advanced_schema_csv(self, self.firstGraphName, self.secondGraphName)
        # Data import
        self.browser.find_by_id('toolsMenu').first.click()
        self.browser.find_link_by_href('/tools/' + self.secondGraphName + '/import/').first.click()
        self.browser.find_by_id('csv-radio').first.click()
        # Change the display field of input to attach the file
        script = """
            $('#files').css('display', '');
            """
        self.browser.execute_script(script)
        self.browser.is_text_present('Drop your nodes files here', wait_time=10)
        # Import the nodes
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'files/csv/bobs-type.csv'
        )
        self.browser.attach_file('file', file_path)
        self.browser.is_text_present('Nodes files loaded. Loading edges files...', wait_time=10)
        # Wait until the data is imported
        self.browser.is_text_present('Now drop your edges files', wait_time=10)
        # Change the display field of input to attach the file
        script = """
            $('#files2').css('display', '');
            """
        self.browser.execute_script(script)
        # Import the relationships
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'files/csv/bobs-rels.csv'
        )
        self.browser.attach_file('file2', file_path)
        self.browser.is_text_present('Data loaded. Uploading to the server...', wait_time=10)
        # Wait until the data is imported
        self.browser.is_text_present('Data uploaded.', wait_time=10)
        # Check that nodes and relationships are ok
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption list']").first.click()
        alicegraph = Graph.objects.get(name=self.secondGraphName)
        alicegraphNodes = alicegraph.nodes.count()
        spin_assert(lambda: self.assertEqual(3, alicegraph.nodes.count()))
        spin_assert(lambda: self.assertEqual(
            1, alicegraph.relationships.count()))
        # Add new nodes and relationships and check all is correct
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//div[@class='pagination']/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        spin_assert(lambda: self.assertEqual(
            alicegraphNodes + 1, alicegraph.nodes.count()))
        # Destroy the databases
        Graph.objects.get(name=self.firstGraphName).destroy()
        Graph.objects.get(name=self.secondGraphName).destroy()
