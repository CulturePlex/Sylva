import requests

from django.test import LiveServerTestCase

from splinter import Browser

from user import signin, logout
from dashboard import create_graph, create_schema, create_type


def create_allowed_rel(test):
    create_graph(test)
    test.assertEqual(test.browser.title, 'SylvaDB - Dashboard')
    create_schema(test)
    create_type(test)
    test.assertEqual(test.browser.title, "SylvaDB - Bob's graph")
    test.browser.find_by_id('allowedRelations').first.click()
    test.browser.select('source', '1')
    test.browser.find_by_name('name').fill('Bob\'s rel')
    test.browser.select('target', '1')
    test.browser.find_by_id('id_description').fill('This the allowed relationship for Bob\'s graph')
    test.browser.find_by_value('Save Type').first.click()
    test.assertEqual(test.browser.title, "SylvaDB - Bob's graph")


class SchemaTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = Browser('phantomjs')
        signin(self)

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
        f = open('sylva/base/tests/bobs-graph_schema.json')
        self.assertEqual(f.read().split("\n")[0], result.content)

    def test_import_schema(self):
        create_graph(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        self.assertEqual(self.browser.title, "SylvaDB - Bob's graph")
        self.browser.find_by_id('schemaImport').first.click()
        self.browser.attach_file('file', 'sylva/base/tests/bobs-graph_schema.json')
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
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Basic']/option[@value='s']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Basic']/option[@value='b']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Basic']/option[@value='n']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='x']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='d']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='t']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='t']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "Time name")
        # Testing data
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//td[@class='dataActions']/a[@class='dataOption new']").first.click()
        self.browser.find_by_name('Time name').first.fill('time time time')
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath("//ul[@class='errorlist']/li").first.text
        self.assertEqual(text, 'Enter a valid time.')

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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='c']").first.click()
        self.browser.find_by_name('properties-0-default').first.fill('Bob, Alice')
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
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
        self.browser.find_by_xpath("//select[@id='id_properties-0-datatype']").first.click()
        self.browser.find_by_xpath("//optgroup[@label='Advanced']/option[@value='f']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of the this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        self.assertEqual(text, "float name")

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
