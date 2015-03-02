import socket
from time import sleep

from django.test import LiveServerTestCase

from splinter import Browser

from user import signup, signin, logout
from dashboard import create_graph, create_schema, create_type, create_data
from graphs.models import Graph

from utils import spin_assert


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
            "//input[@class='lookup-value']").first.fill(u"Bob's node")
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
            "//input[@class='lookup-value']").first.fill(u"Alice's node")
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
            "//input[@class='lookup-value']").first.fill(u"Bob")
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
            "//input[@class='lookup-value']").first.fill(u"o")
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
            "//input[@class='lookup-value']").first.fill(u"x")
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
            "//input[@class='lookup-value']").first.fill(u"B")
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
            "//input[@class='lookup-value']").first.fill(u"C")
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
            "//input[@class='lookup-value']").first.fill(u"e")
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
            "//input[@class='lookup-value']").first.fill(u"h")
        # We need to click outside for a correct behaviour of the input field
        self.browser.find_by_xpath("//div[@id='diagram']").first.click()
        # We run the query
        run_query(self)
        # Right now, we are in the results view. Let's check it
        test_no_results(self)
        Graph.objects.get(name="Bob's graph").destroy()
