import requests
import os

from django.test import LiveServerTestCase
from django.utils.unittest import skipIf

from splinter import Browser

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type
from graphs.models import Graph


@skipIf(os.environ['INTERFACE'] == "0", 'Interface test')
class SchemaTestCase(LiveServerTestCase):
    """
    A set of tests for testing export schema, import schema and everything
    related to advanced types (patterns, options, etc.).
    """

    def setUp(self):
        self.browser = Browser()
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')

    def tearDown(self):
        logout(self)
        self.browser.quit()

    def test_export_schema(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        self.browser.find_by_id('toolsMenu').first.click()
        cookies = {self.browser.cookies.all()[0]["name"]: self.browser.cookies.all()[0]["value"], self.browser.cookies.all()[1]["name"]: self.browser.cookies.all()[1]["value"]}
        result = requests.get(self.live_server_url + '/schemas/bobs-graph/export/', cookies=cookies)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertEqual(self.browser.status_code.is_success(), True)
        f = open('sylva/base/tests/files/bobs-graph_schema.json')
        self.assertEqual(f.read().split("\n")[0], result.content)

    def test_import_schema(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_by_id('schemaImport').first.click()
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'files/bobs-graph_schema.json'
        )
        self.browser.attach_file('file', file_path)
        self.browser.find_by_value('Continue').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        text = self.browser.find_by_id('diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Name")

    def test_new_type(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_xpath(
            "//div[@class='content2-first']/p/textarea[@name='description']").first.fill('The loved type')
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_xpath(
            "//div[@id='diagramBox_bobs-type']/div[@class='title']").first.value
        self.assertNotEqual(text.find("Bob's type"), -1)

    def test_new_advanced_type(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_name('properties-0-default').first.fill(
            "Bob's node default name")
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Name")

    def test_new_advanced_type_string_empty(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('String name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Basic']/option[@value='s']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "String name")
        # Testing data
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption new']").first.click()
        self.browser.find_by_name('String name').first.fill('')
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'This field is required.')
        Graph.objects.get(name="Bob's graph").destroy()

    def test_new_advanced_type_boolean(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Boolean name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Basic']/option[@value='b']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Boolean name")

    def test_new_advanced_type_number(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Number name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Number name")

    def test_new_advanced_type_number_float(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Number name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Number name")
        # Testing data
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption new']").first.click()
        self.browser.find_by_name('Number name').first.fill('1.5')
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a whole number.')
        Graph.objects.get(name="Bob's graph").destroy()

    def test_new_advanced_type_number_string(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Number name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Number name")
        # Testing data
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption new']").first.click()
        self.browser.find_by_name('Number name').first.fill('number')
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a whole number.')
        Graph.objects.get(name="Bob's graph").destroy()

    def test_new_advanced_type_text(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Text name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='x']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Text name")

    def test_new_advanced_type_date(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Date name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='d']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Date name")

    def test_new_advanced_type_time(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Time name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='t']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Time name")

    def test_new_advanced_type_time_string(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Time name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='t']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Time name")
        # Testing data
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption new']").first.click()
        self.browser.find_by_name('Time name').first.fill('0123456789')
        self.browser.find_by_xpath("//button[@class='ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all']").first.click()
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid time.')
        Graph.objects.get(name="Bob's graph").destroy()

    def test_new_advanced_type_choices(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Choices name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='c']").first.click()
        self.browser.find_by_name('properties-0-default').first.fill('Bob, Alice')
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Choices name")

    def test_new_advanced_type_float(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('float name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='f']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "float name")

    def test_new_advanced_type_collaborator(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('collaborator name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Advanced']/option[@value='r']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "collaborator name")

    def test_new_advanced_type_auto_now(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('auto now name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Auto']/option[@value='w']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "auto now name")

    def test_new_advanced_type_auto_now_add(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('auto now add name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Auto']/option[@value='a']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "auto now add name")

    def test_new_advanced_type_auto_increment(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('auto increment name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Auto']/option[@value='i']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "auto increment name")

    def test_new_advanced_type_auto_increment_update(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('auto increment update')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Auto']/option[@value='o']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "auto increment update")

    def test_new_advanced_type_auto_user(self):
        create_graph(self)
        create_schema(self)
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        self.assertEqual(text, 'Type')
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('auto user name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']/optgroup[@label='Auto']/option[@value='e']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "auto user name")

    def test_schema_allowed_rel_addition(self):
        create_graph(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_schema(self)
        create_type(self)
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('Bob\'s rel')
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill('This the allowed relationship for Bob\'s graph')
        self.browser.find_by_value('Save Type').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        self.assertNotEqual(text.find('Bob\'s rel'), -1)

    def test_schema_allowed_rel_addition_deletion(self):
        create_graph(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_schema(self)
        create_type(self)
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('Bob\'s rel')
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill('This the allowed relationship for Bob\'s graph')
        self.browser.find_by_value('Save Type').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        self.assertNotEqual(text.find('Bob\'s rel'), -1)
        self.browser.find_by_xpath("//div[@class='form-row indent']/div[@class='form-row indent']/a").first.click()
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkRight']/a[@class='delete']").first.click()
        self.browser.choose('confirm', '1')
        self.browser.find_by_value('Continue').first.click()
        notExists = self.browser.is_element_not_present_by_xpath(
            "//div[@class='form-row indent']/label")
        self.assertEqual(notExists, True)
