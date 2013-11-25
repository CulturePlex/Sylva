from django.test import LiveServerTestCase

from splinter import Browser

from user import signin, logout
from dashboard import create_schema, create_graph


class SchemaTestCase(LiveServerTestCase):

    def setUp(self):
        self.browser = Browser('phantomjs')

    def tearDown(self):
        logout(self)
        self.browser.quit()

    """
    def test_export_schema(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_graph()
        create_schema()
        self.browser.find_by_id('toolsMenu').first.click()
        self.browser.find_link_by_href('/schemas/ejemplo/export/').first.click()
    """

    def test_import_schema(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
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

    def test_schema_allowed_rel_addition(self):
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_graph(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_schema(self)
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
        signin(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_graph(self)
        self.assertEqual(self.browser.title, 'SylvaDB - Dashboard')
        create_schema(self)
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
