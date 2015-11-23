import os
import socket
from time import sleep

from django.test import LiveServerTestCase

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type, create_data
from graphs.models import Graph

from utils import spin_assert, Browser


BASIC = ['s', 'b', 'n']
ADVANCED = ['x', 'd', 't', 'c', 'f', 'r']
AUTO = ['w', 'a', 'i', 'o', 'e']


def queries_menu(test):
    test.browser.find_by_id('queriesMenu').first.click()
    button_text = test.browser.find_by_id('create-query').first.value
    spin_assert(lambda: test.assertEqual(button_text, "New Query"))


def create_query(test):
    new_query_button = test.browser.find_by_id('create-query').first
    new_query_button.click()
    diagram_title = test.browser.find_by_id('diagramTitle').first.value
    spin_assert(lambda: test.assertEqual(diagram_title, "Diagram"))
    node_type = test.browser.find_by_xpath(
        "//table[@id='node-types']/tbody/tr/td/a").first
    node_type_text = node_type.value
    node_type.click()
    # This node type name is the name that we use in the create_type method
    spin_assert(lambda: test.assertEqual(node_type_text, "Bob's type"))


def run_query(test):
    run_query = test.browser.find_by_id('run-query').first
    run_query.click()


def test_results(test):
    result = test.browser.find_by_xpath(
        "//div[@class='shorten-text']").first
    bobs_type = u"Bob's type 1.Name"
    spin_assert(lambda: test.assertEqual(result.value, bobs_type))


def test_no_results(test):
    results_value = test.browser.find_by_xpath(
        "//div[@id='content2']//p").first.value
    results_text = ("There are not results for this query. "
                    "Please, check your query or your data.")
    spin_assert(lambda: test.assertEqual(results_value, results_text))


# Special methods to test all the available datatypes

def create_complex_type(test, box_name, datatype, type_name, type_value):
    test.browser.find_link_by_href(
        '/schemas/bobs-graph/types/create/').first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='content2-first']/h2").first.value
    spin_assert(lambda: test.assertEqual(text, 'Type'))
    test.browser.find_by_name('name').first.fill(box_name)
    description = test.browser.find_by_xpath(
        "//div[@class='content2-first']/p/textarea[@name='description']").first
    description.fill('The loved type')
    # Advanced mode
    test.browser.find_by_id('advancedModeButton').first.click()
    test.browser.find_by_name('properties-0-key').first.fill(
        type_name)
    test.browser.find_by_name('properties-0-display').first.check()
    test.browser.find_by_name('properties-0-required').first.check()

    label = 'Basic'
    if datatype in ADVANCED:
        label = 'Advanced'
    elif datatype in AUTO:
        label = 'Auto'

    if datatype == 'u':
        datatype_selection = test.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/option[@value='" + datatype + "']")
    else:
        datatype_selection = test.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/optgroup[@label='" + label + "']/option[@value='" + datatype + "']")
    datatype_selection.first.click()
    test.browser.find_by_name('properties-0-default').first.fill(
        type_value)
    test.browser.find_by_name('properties-0-order').first.fill('1')
    test.browser.find_by_name('properties-0-description').first.fill(
        "The name of this Bob's node")
    test.browser.find_by_value('Save Type').first.click()


def create_allowed_relationship(test, box_name, target_name,
                                rel_name, datatype, type_name, type_value):
    test.browser.find_by_id('allowedRelations').first.click()
    test.browser.select('source', '1')
    test.browser.find_by_name('name').fill(rel_name)
    test.browser.select('target', '2')
    test.browser.find_by_id('id_description').fill(
        "This the allowed relationship for Bob's graph")
    # Advanced mode
    test.browser.find_by_id('advancedModeButton').first.click()
    test.browser.find_by_name('properties-0-key').first.fill(
        type_name)
    test.browser.find_by_name('properties-0-display').first.check()
    test.browser.find_by_name('properties-0-required').first.check()

    label = 'Basic'
    if datatype in ADVANCED:
        label = 'Advanced'
    elif datatype in AUTO:
        label = 'Auto'

    if datatype == 'u':
        datatype_selection = test.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/option[@value='" + datatype + "']")
    else:
        datatype_selection = test.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/optgroup[@label='" + label + "']/option[@value='" + datatype + "']")
    datatype_selection.first.click()
    test.browser.find_by_name('properties-0-default').first.fill(
        type_value)
    test.browser.find_by_name('properties-0-order').first.fill('1')
    test.browser.find_by_name('properties-0-description').first.fill(
        "The name of this allowed relationship")
    test.browser.find_by_value('Save Type').first.click()
    spin_assert(lambda: test.assertEqual(
        test.browser.title, "SylvaDB - Bob's graph"))
    # We create the link between the nodes
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//td[@class='dataActions']/a[@class='dataOption list']").first.click()
    test.browser.find_by_xpath(
        "//td[@class='dataList']/a[@class='edit']").first.click()
    test.browser.find_by_xpath(
        "//li[@class='token-input-input-token']/input").first.fill(target_name)
    test.browser.is_element_present_by_id("id_user_wait", 5)
    test.browser.find_by_xpath(
        "//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
    test.browser.find_by_value("Save " + box_name).first.click()


def create_complex_data(test, box_name, type_name, type_value):
    test.browser.find_by_id('dataMenu').first.click()
    test.browser.find_by_xpath(
        "//a[@class='dataOption new']").first.click()
    text = test.browser.find_by_id('propertiesTitle').first.value
    spin_assert(lambda: test.assertEqual(text, 'Properties'))
    # test.browser.select(type_name, type_value)
    test.browser.find_by_value("Save " + box_name).first.click()
    text = test.browser.find_by_xpath(
        "//div[@class='pagination']"
        "/span[@class='pagination-info']").first.value


class QueryTestCase(LiveServerTestCase):
    """
    A set of tests for testing queries.
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
        super(QueryTestCase, cls).tearDownClass()

    def test_query_list_view(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_view(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_add_box(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        # We check if the node type is the same
        node_type.click()
        title_text = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']").first.value
        spin_assert(lambda: self.assertEqual(title_text, u"Bob's type 1"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_add_property(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        type_property = self.browser.find_by_xpath(
            "//select[@class='select-property']").first
        type_property.click()
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_get_results(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We get the button to run the query and click it
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_add_more_than_one_property(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property1.click()
        # We select another property
        select_and_or_option = self.browser.find_by_xpath(
            "//div[@id='field1']"
            "//option[@class='option-and-or' and text()='And']").first
        select_and_or_option.click()
        select_property2 = self.browser.find_by_xpath(
            "//div[@id='field2']"
            "//option[@class='option-property' and text()='Name']").first
        select_property2.click()
        # We check if the value of the selects are the value of the properties
        # and the value of the and-or select is "and".
        select_value1 = self.browser.find_by_xpath(
            "//div[@id='field1']"
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value1, u"Name"))
        select_value2 = self.browser.find_by_xpath(
            "//div[@id='field2']"
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value2, u"Name"))
        select_and_or_value = self.browser.find_by_xpath(
            "//div[@id='field1']//select[@class='select-and-or']").first.value
        spin_assert(lambda: self.assertEqual(select_and_or_value, u"and"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_add_more_than_one_property_with_or(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property1.click()
        # We select another property
        select_and_or_option = self.browser.find_by_xpath(
            "//div[@id='field1']"
            "//option[@class='option-and-or' and text()='Or']").first
        select_and_or_option.click()
        select_property2 = self.browser.find_by_xpath(
            "//div[@id='field2']"
            "//option[@class='option-property' and text()='Name']").first
        select_property2.click()
        # We check if the value of the selects are the value of the properties
        # and the value of the and-or select is "and".
        select_value1 = self.browser.find_by_xpath(
            "//div[@id='field1']"
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value1, u"Name"))
        select_value2 = self.browser.find_by_xpath(
            "//div[@id='field2']"
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value2, u"Name"))
        select_and_or_value = self.browser.find_by_xpath(
            "//div[@id='field1']//select[@class='select-and-or']").first.value
        spin_assert(lambda: self.assertEqual(select_and_or_value, u"or"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_create_wildcard_relationship(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We select the wildcard relationship
        select_rel = self.browser.find_by_xpath(
            "//select[@class='select-rel']").first
        select_wildcard_rel = self.browser.find_by_xpath(
            "//option[@class='option-rel' and text()='WildcardRel']").first
        # We need to execute these javascript commands
        js_code = "$('.select-rel').val('WildcardRel').change();"
        self.browser.execute_script(js_code)
        # We check if we have created the relationship
        relation_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBoxRel-0-WildcardRel']").first.value
        spin_assert(lambda: self.assertEqual(relation_box_name,
                                             u"WildcardRel"))
        wildcard_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-wildcard']//span").first.value
        spin_assert(lambda: self.assertEqual(wildcard_box_name, u"Wildcard"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_create_wildcard_relationship_and_get_results(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the wildcard relationship
        select_rel = self.browser.find_by_xpath(
            "//select[@class='select-rel']").first
        select_wildcard_rel = self.browser.find_by_xpath(
            "//option[@class='option-rel' and text()='WildcardRel']").first
        # We need to execute these javascript commands
        js_code = "$('.select-rel').val('WildcardRel').change();"
        self.browser.execute_script(js_code)
        # We check if we have created the relationship
        relation_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBoxRel-0-WildcardRel']").first.value
        spin_assert(lambda: self.assertEqual(relation_box_name,
                                             u"WildcardRel"))
        wildcard_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-wildcard']//span").first.value
        spin_assert(lambda: self.assertEqual(wildcard_box_name, u"Wildcard"))
        # We select a property for the wildcard box
        wildcard_property = self.browser.find_by_xpath(
            "//input[@class='wildCardInput select-property']").first.fill(
            u"Name")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We need to click somewhere for setting the property value correctly
        checkbox_wildcard = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox_wildcard.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_check_click_header(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We get the button to run the query and click it
        run_query(self)
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u"Bob's node"))
        # We check that we have only one link, the header itself
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 1))
        # We click to get the order
        header = self.browser.find_by_xpath(
            "//th[@class='header']/a/div").first
        header.click()
        # We can check that rigth now we have two more links
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 3))
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_create_self_relationship(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        # We create the relationship
        spin_assert(lambda: self.assertEqual(
            self.browser.title, "SylvaDB - Bob's graph"))
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill("Bob's rel")
        self.browser.select('target', '1')
        self.browser.find_by_id('id_description').fill("This the allowed relationship for Bob's graph")
        self.browser.find_by_value('Save Type').first.click()
        spin_assert(lambda: self.assertEqual(
            self.browser.title, "SylvaDB - Bob's graph"))
        text = self.browser.find_by_xpath(
            "//div[@class='form-row indent']/label").first.value
        spin_assert(lambda: self.assertNotEqual(text.find("Bob's rel"), -1))
        # Navigate to the menu of queries
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We select the wildcard relationship
        select_rel = self.browser.find_by_xpath(
            "//select[@class='select-rel']").first
        select_wildcard_rel = self.browser.find_by_xpath(
            "//option[@class='option-rel' and text()='WildcardRel']").first
        # We need to execute these javascript commands
        js_code = "$('.select-rel').val('WildcardRel').change();"
        self.browser.execute_script(js_code)
        # We check if we have created the relationship
        relation_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBoxRel-0-WildcardRel']").first.value
        spin_assert(lambda: self.assertEqual(relation_box_name,
                                             u"WildcardRel"))
        wildcard_box_name = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-wildcard']//span").first.value
        spin_assert(lambda: self.assertEqual(wildcard_box_name, u"Wildcard"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_two_boxes_and_get_results(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We get the button to run the query and click it
        run_query(self)
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"Bob's node Bob's node"))
        # We check that we have only one link, the header itself
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 2))
        # We click to get the order
        header = self.browser.find_by_xpath(
            "//th[@class='header']/a/div").first
        header.click()
        # We can check that rigth now we have two more links
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 4))
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_two_boxes_edit_alias_and_get_results(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We edit the aliases of both boxes
        edit_alias1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineEditSelect_bobs-type']/i").first
        edit_alias2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineEditSelect_bobs-type']/i").first
        edit_alias1.click()
        edit_alias2.click()
        js_code = '''
            $($('.select-nodetype-bobs-type')[0]).val("Bob1").change();
            $($('.select-nodetype-bobs-type')[1]).val("Bob2").change();
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        header2 = headers[1]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Bob1.Name"))
        spin_assert(lambda: self.assertEqual(header2.text,
                                             u"Bob2.Name"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"Bob's node Bob's node"))
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_two_boxes_edit_alias_and_get_results_go_back(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We edit the aliases of both boxes
        edit_alias1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineEditSelect_bobs-type']/i").first
        edit_alias2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineEditSelect_bobs-type']/i").first
        edit_alias1.click()
        edit_alias2.click()
        js_code = '''
            $($('.select-nodetype-bobs-type')[0]).val("Bob1").change();
            $($('.select-nodetype-bobs-type')[1]).val("Bob2").change();
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        header2 = headers[1]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Bob1.Name"))
        spin_assert(lambda: self.assertEqual(header2.text,
                                             u"Bob2.Name"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"Bob's node Bob's node"))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if we have loaded the boxes correctly
        title_text0 = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']")[0].value
        title_text1 = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']")[1].value
        spin_assert(lambda: self.assertEqual(title_text0, u"Bob1"))
        spin_assert(lambda: self.assertEqual(title_text1, u"Bob2"))
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    # Loading queries after executing results

    def test_query_builder_two_boxes_get_results_and_go_back(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select the correct alias
        js_code = '''
            $($('.select-nodetype-bobs-type')[1]).val("Bob's type 2").change();
        '''
        self.browser.execute_script(js_code)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We get the button to run the query and click it
        run_query(self)
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"Bob's node Bob's node"))
        # We check that we have only one link, the header itself
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 2))
        # We click to get the order
        header = self.browser.find_by_xpath(
            "//th[@class='header']/a/div").first
        header.click()
        # We can check that rigth now we have two more links
        links_len = len(self.browser.find_by_xpath("//th[@class='header']/a"))
        spin_assert(lambda: self.assertEqual(links_len, 4))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if we have loaded the boxes correctly
        title_text0 = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']")[0].value
        title_text1 = self.browser.find_by_xpath(
            "//select[@class='select-nodetype-bobs-type']")[1].value
        spin_assert(lambda: self.assertEqual(title_text0, u"Bob's type 1"))
        spin_assert(lambda: self.assertEqual(title_text1, u"Bob's type 2"))
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    # Aggregates

    def test_query_builder_one_box_with_count(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        aggregate_name = self.browser.find_by_xpath(
            "//select[@class='select-aggregate']").first.value
        spin_assert(lambda: self.assertEqual(aggregate_name,
                                             u"count"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_one_box_with_count_distinct(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        aggregate_name = self.browser.evaluate_script(
            "$('.select-aggregate option:selected').html()")
        # We need to check if the value is equals to "Count distinct".
        spin_assert(lambda: self.assertEqual(aggregate_name,
                                             u"Count distinct"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_one_box_with_aggregate_and_run(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Count (Bob's type 1.Name)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"1"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_one_box_with_aggregate_run_and_go_back(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Count (Bob's type 1.Name)"))
        # We check that the value is correct
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"1"))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the aggregate is loaded correctly
        aggregate_name = self.browser.find_by_xpath(
            "//select[@class='select-aggregate']").first.value
        spin_assert(lambda: self.assertEqual(aggregate_name,
                                             u"count"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_aggregate_run_and_go_back_distinct(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text,
            u"Count Distinct(Bob's type 1.Name)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name,
                                             u"1"))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the aggregate is loaded correctly
        aggregate_name = self.browser.evaluate_script(
            "$('.select-aggregate option:selected').html()")
        spin_assert(lambda: self.assertEqual(aggregate_name,
                                             u"Count distinct"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_two_boxes_with_aggregates(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select the correct alias
        js_code = '''
            $($('.select-nodetype-bobs-type')[1]).val("Bob's type 2").change();
        '''
        self.browser.execute_script(js_code)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We click in the advanced mode
        aggregate1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        aggregate2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        js_code = '''
            $($('.select-aggregate option[value="count"][data-distinct="false"]')[0]).prop('selected', 'selected').change();
            $($('.select-aggregate option[value="min"][data-distinct="false"]')[1]).prop('selected', 'selected').change();
        '''
        self.browser.execute_script(js_code)
        aggregates_names = self.browser.find_by_xpath(
            "//select[@class='select-aggregate']")
        spin_assert(lambda: self.assertEqual(aggregates_names[0].value,
                                             u"count"))
        spin_assert(lambda: self.assertEqual(aggregates_names[1].value,
                                             u"min"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_two_boxes_with_distinct_aggregates(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select the correct alias
        js_code = '''
            $($('.select-nodetype-bobs-type')[1]).val("Bob's type 2").change();
        '''
        self.browser.execute_script(js_code)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We click in the advanced mode
        aggregate1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        aggregate2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        js_code = '''
            $($('.select-aggregate option[value="count"][data-distinct="true"]')[0]).prop('selected', 'selected').change();
            $($('.select-aggregate option[value="min"][data-distinct="true"]')[1]).prop('selected', 'selected').change();
        '''
        self.browser.execute_script(js_code)
        aggregate_name1 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[0]).html()")
        aggregate_name2 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[1]).html()")
        spin_assert(lambda: self.assertEqual(aggregate_name1,
                                             u"Count distinct"))
        spin_assert(lambda: self.assertEqual(aggregate_name2,
                                             u"Min distinct"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_boxes_with_aggregates_run_and_go_back(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select the correct alias
        js_code = '''
            $($('.select-nodetype-bobs-type')[1]).val("Bob's type 2").change();
        '''
        self.browser.execute_script(js_code)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We click in the advanced mode
        aggregate1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        aggregate2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        js_code = '''
            $($('.select-aggregate option[value="count"][data-distinct="false"]')[0]).prop('selected', 'selected').change();
            $($('.select-aggregate option[value="min"][data-distinct="false"]')[1]).prop('selected', 'selected').change();
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header2 = headers[0]
        header1 = headers[1]
        spin_assert(lambda: self.assertEqual(
            header1.text,
            u"Count (Bob's type 1.Name)"))
        spin_assert(lambda: self.assertEqual(
            header2.text,
            u"Min (Bob's type 2.Name)"))
        # We check that the value is correct
        results_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']/td")
        result_name2 = results_name[0].text
        result_name1 = results_name[1].text
        spin_assert(lambda: self.assertEqual(result_name1,
                                             u"1"))
        spin_assert(lambda: self.assertEqual(result_name2,
                                             u"Bob's node"))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the aggregate is loaded correctly
        aggregate_name1 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[0]).html()")
        aggregate_name2 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[1]).html()")
        spin_assert(lambda: self.assertEqual(aggregate_name1,
                                             u"Count"))
        spin_assert(lambda: self.assertEqual(aggregate_name2,
                                             u"Min"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_boxes_aggregates_run_and_go_back_distinct(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        # We create two boxes
        create_query(self)
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a").first
        node_type.click()
        # We select the correct alias
        js_code = '''
            $($('.select-nodetype-bobs-type')[1]).val("Bob's type 2").change();
        '''
        self.browser.execute_script(js_code)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']")
        select_properties[0].click()
        select_properties[1].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//div[@id='field2']//input[@class='checkbox-property']").first
        checkbox2.click()
        # We click in the advanced mode
        aggregate1 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        aggregate2 = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first.click()
        js_code = '''
            $($('.select-aggregate option[value="count"][data-distinct="true"]')[0]).prop('selected', 'selected').change();
            $($('.select-aggregate option[value="min"][data-distinct="true"]')[1]).prop('selected', 'selected').change();
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header2 = headers[0]
        header1 = headers[1]
        spin_assert(lambda: self.assertEqual(
            header1.text,
            u"Count Distinct(Bob's type 1.Name)"))
        spin_assert(lambda: self.assertEqual(
            header2.text,
            u"Min Distinct(Bob's type 2.Name)"))
        # We check that the value is correct
        results_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']/td")
        result_name2 = results_name[0].text
        result_name1 = results_name[1].text
        spin_assert(lambda: self.assertEqual(result_name1,
                                             u"1"))
        spin_assert(lambda: self.assertEqual(result_name2,
                                             u"Bob's node"))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the aggregate is loaded correctly
        aggregate_name1 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[0]).html()")
        aggregate_name2 = self.browser.evaluate_script(
            "$($('.select-aggregate option:selected')[1]).html()")
        spin_assert(lambda: self.assertEqual(aggregate_name1,
                                             u"Count distinct"))
        spin_assert(lambda: self.assertEqual(aggregate_name2,
                                             u"Min distinct"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_max_no_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="max"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Max (Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_max_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="max"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text, u"Max Distinct(Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_min_no_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="min"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Min (Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_min_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="min"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text, u"Min Distinct(Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_sum_no_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="sum"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(header1.text,
                                             u"Sum (Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_sum_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="sum"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text, u"Sum Distinct(Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_avg_no_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="avg"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text, u"Average (Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1.0'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_avg_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="avg"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # We check the headers with the aliases
        headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        header1 = headers[0]
        spin_assert(lambda: self.assertEqual(
            header1.text, u"Average Distinct(Bob's type 1.Number)"))
        # We check the text u"Bob's node"
        result_name = self.browser.find_by_xpath(
            "//tr[@class='row-even']").first.text
        spin_assert(lambda: self.assertEqual(result_name, u'1.0'))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_stdev_no_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="stdev"][data-distinct="false"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # # We check the headers with the aliases
        # headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        # header1 = headers[0]
        # spin_assert(lambda: self.assertEqual(
        #    header1.text, u"Deviation (Bob's type 1.Number)"))
        # # We check the text u"Bob's node"
        # result_name = self.browser.find_by_xpath(
        #     "//tr[@class='row-even']").first.text
        # spin_assert(lambda: self.assertEqual(result_name, 1))
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_stdev_distinct(self):
        create_graph(self)
        create_schema(self)
        # Bob with Number type
        box_name = "Bob's type"
        datatype = "n"
        type_name = "Number"
        type_value = 1
        create_complex_type(self, box_name, datatype, type_name, type_value)
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name(type_name).first.fill(type_value)
        self.browser.find_by_value("Save " + box_name).first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        queries_menu(self)
        # We create one box
        create_query(self)
        # We select a property of the boxes
        select_properties = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='" +
            type_name + "']")
        select_properties[0].click()
        # We check if the value of the select is the value of the property
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, type_name))
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox1.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-1-bobs-type']"
            "//a[@id='inlineAdvancedMode_bobs-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="stdev"][data-distinct="true"]')
            .prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        # We get the button to run the query and click it
        run_query(self)
        # # We check the headers with the aliases
        # headers = self.browser.find_by_xpath("//th[@class='header']/a/div")
        # header1 = headers[0]
        # spin_assert(lambda: self.assertEqual(
        #    header1.text, u"Deviation Distinct(Bob's type 1.Number)"))
        # # We check the text u"Bob's node"
        # result_name = self.browser.find_by_xpath(
        #     "//tr[@class='row-even']").first.text
        # spin_assert(lambda: self.assertEqual(result_name, 1))
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    # Lookups tests

    def test_query_builder_lookups_equals(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value, u"eq"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"Bob's node")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_not_equals(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and "
            "text()='does not equal']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value, u"neq"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"Alice's node")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_equals_diff_value(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value, u"eq"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"Bob")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_contains(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='contains']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"icontains"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"o")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_not_contains(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and "
            "text()=\"doesn't contain\"]").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"idoesnotcontain"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"x")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_starts_with(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='starts with']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"istartswith"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"B")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_not_starts_with(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='starts with']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"istartswith"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"C")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_ends_with(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='ends with']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"iendswith"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"e")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_not_ends_with(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='ends with']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"iendswith"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']").first.fill(
            u"h")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_date_option(self):
        create_graph(self)
        create_schema(self)
        # We create the date type
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        spin_assert(lambda: self.assertEqual(text, 'Type'))
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill('Date name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/optgroup[@label='Advanced']/option[@value='d']").first.click()
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        spin_assert(lambda: self.assertEqual(text, "Date name"))
        # We create the data for the date type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.find_by_name('Date name').first.fill("2010-01-01")
        datepicker = self.browser.find_by_id("ui-datepicker-div").first
        self.browser.find_by_id('propertiesTitle').first.click()
        spin_assert(lambda: self.assertEqual(datepicker.visible, False))
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        # We navigate to the queries menu
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Date name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Date name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"eq"))
        # Let's check if the javascript calendar is showing
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        self.browser.find_by_xpath(
            "//input[@class='lookup-value time hasDatepicker']").first.fill(
            u"2010-01-01")
        calendar = self.browser.find_by_xpath("//div[@id='ui-datepicker-div']")
        spin_assert(lambda: self.assertIsNotNone(calendar))
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_choices_option(self):
        create_graph(self)
        create_schema(self)
        # We create the choices type
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='content2-first']/h2").first.value
        spin_assert(lambda: self.assertEqual(text, 'Type'))
        self.browser.find_by_name('name').first.fill("Bob's type")
        self.browser.find_by_id('advancedModeButton').first.click()
        self.browser.find_by_name('properties-0-key').first.fill(
            'Choices name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_name('properties-0-required').first.check()
        self.browser.find_by_xpath(
            "//select[@id='id_properties-0-datatype']"
            "/optgroup[@label='Advanced']/option[@value='c']").first.click()
        self.browser.find_by_name('properties-0-default').first.fill(
            'Bob, Alice')
        self.browser.find_by_name('properties-0-order').first.fill('1')
        self.browser.find_by_name('properties-0-description').first.fill(
            "The name of this Bob's node")
        self.browser.find_by_value('Save Type').first.click()
        text = self.browser.find_by_id(
            'diagramBoxField_bobs-graph.bobs-type.undefined').first.value
        spin_assert(lambda: self.assertEqual(text, "Choices name"))
        # We create the data for the date type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath(
            "//a[@class='dataOption new']").first.click()
        text = self.browser.find_by_id('propertiesTitle').first.value
        spin_assert(lambda: self.assertEqual(text, 'Properties'))
        self.browser.select('Choices name', 'bob')
        self.browser.find_by_value("Save Bob's type").first.click()
        text = self.browser.find_by_xpath(
            "//div[@class='pagination']"
            "/span[@class='pagination-info']").first.value
        spin_assert(lambda: self.assertNotEqual(
            text.find(" elements Bob's type."), -1))
        # We navigate to the queries menu
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Choices name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Choices name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value,
                                             u"eq"))
        # Let's check if the javascript calendar is showing
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        # We need to execute these javascript commands
        js_code = "$('.lookup-value option[value=\"bob\"]').prop('selected', 'selected').change();"
        self.browser.execute_script(js_code)
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_in_between(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='is between']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value, u"between"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value1 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].fill(
            u"Bob's node")
        lookup_input_value2 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[1].fill(
            u"Alice's node")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_lookups_in_between_and_go_back(self):
        create_graph(self)
        create_schema(self)
        create_type(self)
        create_data(self)
        queries_menu(self)
        create_query(self)
        # We select a property
        select_property = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name']").first
        select_property.click()
        select_value = self.browser.find_by_xpath(
            "//select[@class='select-property']").first.value
        spin_assert(lambda: self.assertEqual(select_value, u"Name"))
        checkbox = self.browser.find_by_xpath(
            "//div[@id='field1']//input[@class='checkbox-property']").first
        checkbox.click()
        # We select the lookup
        select_lookup = self.browser.find_by_xpath(
            "//select[@class='select-lookup']").first
        select_lookup.click()
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='is between']").first
        lookup_option.click()
        spin_assert(lambda: self.assertEqual(select_lookup.value, u"between"))
        # We need to click outside for a correct behaviour of the rel select
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We fill the input for the lookup value
        lookup_input_value1 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].fill(
            u"Bob")
        lookup_input_value2 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[1].fill(
            u"Alice")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the values are loaded right
        lookup_input_value1 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].value
        spin_assert(lambda: self.assertEqual(lookup_input_value1, u"Bob"))
        lookup_input_value2 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[1].value
        spin_assert(lambda: self.assertEqual(lookup_input_value2, u"Alice"))
        Graph.objects.get(name="Bob's graph").destroy()

    # Testing all the datatypes in node and relationship boxes

    def test_query_builder_datatypes_string_equals(self):
        create_graph(self)
        create_schema(self)
        box_name1 = "Bob type"
        box_name2 = "Alice type"
        # Bob with String type
        datatype = "s"
        type_name = "Name1"
        type_value = "Bob"
        create_complex_type(self, box_name1, datatype, type_name, type_value)
        create_complex_data(self, box_name1, type_name, type_value)
        # Alice with String type
        datatype = "s"
        type_name = "Name2"
        type_value = "Alice"
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        create_complex_type(self, box_name2, datatype, type_name, type_value)
        create_complex_data(self, box_name2, type_name, type_value)
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        # Relationship between them
        rel_name = "Rel"
        target_name = "Bob"
        datatype = "s"
        type_name = "Name3"
        type_value = "Bob"
        create_allowed_relationship(self, box_name2, target_name, rel_name,
                                    datatype, type_name, type_value)
        # We navigate to the queries menu
        queries_menu(self)
        # We create two boxes
        new_query_button = self.browser.find_by_id('create-query').first
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[1]
        node_type_text = node_type.value
        node_type.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text, "Bob type"))
        # We create the relationship
        # We need to execute these javascript commands
        js_code = "$('.select-rel').val('rel').change();"
        self.browser.execute_script(js_code)
        # We select the properties
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name1']").first
        select_property1.click()
        select_property2 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name2']").first
        select_property2.click()
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[0]
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[1]
        checkbox2.click()
        # We select the lookup equals
        lookup_option1 = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']")[0]
        lookup_option1.click()
        lookup_option2 = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']")[1]
        lookup_option2.click()
        # We fill the input for the lookup value
        lookup_input_value1 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].fill(
            u"Bob")
        lookup_input_value2 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[1].fill(
            u"Alice")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        result = self.browser.find_by_xpath(
            "//div[@class='shorten-text']").first
        bobs_type = u"Bob type 1.Name1"
        spin_assert(lambda: self.assertEqual(result.value, bobs_type))
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the values are loaded right
        lookup_input_value1 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].value
        spin_assert(lambda: self.assertEqual(lookup_input_value1, u"Bob"))
        lookup_input_value2 = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[1].value
        spin_assert(lambda: self.assertEqual(lookup_input_value2, u"Alice"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_datatypes_string_relationship(self):
        create_graph(self)
        create_schema(self)
        box_name1 = "Bob type"
        box_name2 = "Alice type"
        # Bob with String type
        datatype = "s"
        type_name = "Name1"
        type_value = "Bob"
        create_complex_type(self, box_name1, datatype, type_name, type_value)
        create_complex_data(self, box_name1, type_name, type_value)
        # Alice with String type
        datatype = "s"
        type_name = "Name2"
        type_value = "Alice"
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        create_complex_type(self, box_name2, datatype, type_name, type_value)
        create_complex_data(self, box_name2, type_name, type_value)
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        # Relationship between them
        rel_name = "Rel"
        target_name = "Bob"
        datatype = "s"
        type_name = "Name3"
        type_value = "Bob"
        create_allowed_relationship(self, box_name2, target_name, rel_name,
                                    datatype, type_name, type_value)
        # We navigate to the queries menu
        queries_menu(self)
        # We create two boxes
        new_query_button = self.browser.find_by_id('create-query').first
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[1]
        node_type_text = node_type.value
        node_type.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text, "Bob type"))
        # We create the relationship
        # We need to execute these javascript commands
        js_code = "$('.select-rel').val('rel').change();"
        self.browser.execute_script(js_code)
        js_code = "$('#inlineShowHideLink_rel').click();"
        self.browser.execute_script(js_code)
        # We select the properties
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name1']").first
        select_property1.click()
        select_property2 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name2']").first
        select_property2.click()
        select_property3 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name3']").first
        select_property3.click()
        # We check the property to return the property value
        checkbox1 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[0]
        checkbox1.click()
        checkbox2 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[1]
        checkbox2.click()
        checkbox3 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[2]
        checkbox3.click()
        # We select the lookup equals
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']")[2]
        lookup_option.click()
        # We fill the input for the lookup value
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[2].fill(
            u"Rel")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the values are loaded right
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[2].value
        spin_assert(lambda: self.assertEqual(lookup_input_value, u"Rel"))
        Graph.objects.get(name="Bob's graph").destroy()

    # F fields

    def test_query_builder_f_fields_equals(self):
        create_graph(self)
        create_schema(self)
        box_name1 = "Bob type"
        box_name2 = "Alice type"
        # Bob with String type
        datatype = "s"
        type_name = "Name1"
        type_value = "Bob"
        create_complex_type(self, box_name1, datatype, type_name, type_value)
        create_complex_data(self, box_name1, type_name, type_value)
        # Alice with Number type
        datatype = "s"
        type_name = "Name2"
        type_value = "Alice"
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        create_complex_type(self, box_name2, datatype, type_name, type_value)
        create_complex_data(self, box_name2, type_name, type_value)
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        # We navigate to the queries menu
        queries_menu(self)
        # We create two boxes
        new_query_button = self.browser.find_by_id('create-query').first
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type1 = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[0]
        node_type_text1 = node_type1.value
        node_type1.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text1, "Alice type"))
        node_type2 = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[1]
        node_type_text2 = node_type2.value
        node_type2.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text2, "Bob type"))
        # We select a property
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name1']").first
        select_property1.click()
        # We select another property
        select_property2 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name2']").first
        select_property2.click()
        checkbox1 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[0]
        checkbox1.click()
        # We select the lookup equals
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        # We select the F field
        f_field = self.browser.find_by_xpath(
            "//option[@class='option-other-boxes-properties' and "
            "@value='bob-type_1.1']").first
        f_field.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the values are loaded right
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].value
        spin_assert(lambda: self.assertEqual(lookup_input_value,
                                             u"Bob type 1.Name1"))
        Graph.objects.get(name="Bob's graph").destroy()

    def test_query_builder_f_fields_equals_and_aggregate(self):
        create_graph(self)
        create_schema(self)
        box_name1 = "Bob type"
        box_name2 = "Alice type"
        # Bob with String type
        datatype = "s"
        type_name = "Name1"
        type_value = "Bob"
        create_complex_type(self, box_name1, datatype, type_name, type_value)
        create_complex_data(self, box_name1, type_name, type_value)
        # Alice with Number type
        datatype = "s"
        type_name = "Name2"
        type_value = "Alice"
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        create_complex_type(self, box_name2, datatype, type_name, type_value)
        create_complex_data(self, box_name2, type_name, type_value)
        # We navigate to the schema view
        self.browser.find_link_by_href('/schemas/bobs-graph/').first.click()
        # We navigate to the queries menu
        queries_menu(self)
        # We create two boxes
        new_query_button = self.browser.find_by_id('create-query').first
        new_query_button.click()
        diagram_title = self.browser.find_by_id('diagramTitle').first.value
        spin_assert(lambda: self.assertEqual(diagram_title, "Diagram"))
        node_type1 = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[0]
        node_type_text1 = node_type1.value
        node_type1.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text1, "Alice type"))
        node_type2 = self.browser.find_by_xpath(
            "//table[@id='node-types']/tbody/tr/td/a")[1]
        node_type_text2 = node_type2.value
        node_type2.click()
        # This node type name is the name that we use in the create_type method
        spin_assert(lambda: self.assertEqual(node_type_text2, "Bob type"))
        # We select a property
        select_property1 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name1']").first
        select_property1.click()
        checkbox1 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[0]
        checkbox1.click()
        # We select another property
        select_property2 = self.browser.find_by_xpath(
            "//option[@class='option-property' and text()='Name2']").first
        select_property2.click()
        checkbox2 = self.browser.find_by_xpath(
            "//input[@class='checkbox-property']")[1]
        checkbox2.click()
        # We click in the advanced mode
        aggregate = self.browser.find_by_xpath(
            "//div[@id='diagramBox-2-bob-type']"
            "//a[@id='inlineAdvancedMode_bob-type']/i").first
        aggregate.click()
        js_code = '''
            $('.select-aggregate option[value="count"][data-distinct="false"]').prop('selected', 'selected').change()
        '''
        self.browser.execute_script(js_code)
        aggregate_name = self.browser.find_by_xpath(
            "//select[@class='select-aggregate']").first.value
        spin_assert(lambda: self.assertEqual(aggregate_name,
                                             u"count"))
        # We select the lookup equals
        lookup_option = self.browser.find_by_xpath(
            "//option[@class='lookup-option' and text()='equals']").first
        lookup_option.click()
        # We select the F field
        f_field = self.browser.find_by_xpath(
            "//option[@class='option-other-boxes-properties' and "
            "@value='Count(bob-type_1.1)']").first
        f_field.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        # We navigate to the query builder view
        breadcrumb_new = self.browser.find_by_xpath(
            "//header[@class='global']/h2/a")[2]
        breadcrumb_new.click()
        # We check if the values are loaded right
        lookup_input_value = self.browser.find_by_xpath(
            "//input[@class='lookup-value']")[0].value
        spin_assert(lambda: self.assertEqual(lookup_input_value,
                                             u"Count(Bob type 1.Name1)"))
        Graph.objects.get(name="Bob's graph").destroy()
