from django.test import LiveServerTestCase

from splinter import Browser

from user import signup, signin, logout
from dashboard import create_graph, create_schema
from graphs.models import Graph


class BugTestCase(LiveServerTestCase):
    """
    A set of tests to check the existence of bugs.
    """

    def setUp(self):
        self.browser = Browser('phantomjs')
        signup(self, 'bob', 'bob@cultureplex.ca', 'bob_secret')
        signin(self, 'bob', 'bob_secret')

    def tearDown(self):
        logout(self)
        self.browser.quit()
        Graph.objects.get(name="Bob's graph").destroy()

    def test_node_rel_count_one(self):
        '''
        This test show that reflexive outgoing `relationships` don't count if
        there are more relationships.
        '''
        real_nodes = 0
        real_rels = 0
        create_graph(self)
        create_schema(self)
        # Creating a nodetype: "First"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("First")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        # Creating another nodetype: "Second"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("Second")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        self.browser.find_by_id('dataMenu').first.click()
        # Creating an allowed relationship: "First -> First"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToFirst')
        self.browser.select('target', '1')
        self.browser.find_by_value('Save Type').first.click()
        # Creating an allowed relationship: "First -> Second"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToSecond')
        self.browser.select('target', '2')
        self.browser.find_by_value('Save Type').first.click()
        # Creating a node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating a node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second3")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Editing the "First1" node
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption list']")[0].click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First1"
        self.browser.find_by_value('Save First').first.click()
        # Checking the counts
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('sigma-pause').first.click()
        nodes = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        rels = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(str(real_nodes) + " nodes", nodes)
        self.assertEqual(str(real_rels) + " relationships", rels)

    def test_node_rel_count_two(self):
        '''
        This test shows that new `nodes` with relationships don't count.
        '''
        real_nodes = 0
        real_rels = 0
        create_graph(self)
        create_schema(self)
        # Creating a nodetype: "First"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("First")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        # Creating another nodetype: "Second"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("Second")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        self.browser.find_by_id('dataMenu').first.click()
        # Creating an allowed relationship: "First -> First"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToFirst')
        self.browser.select('target', '1')
        self.browser.find_by_value('Save Type').first.click()
        # Creating an allowed relationship: "First -> Second"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToSecond')
        self.browser.select('target', '2')
        self.browser.find_by_value('Save Type').first.click()
        # Creating a node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating a node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second3")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Editing the "First1" node
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption list']")[0].click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First1"
        self.browser.find_by_value('Save First').first.click()
        # Creating another node of the "First" type with relationships
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First3")
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First3"
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Checking the counts
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('sigma-pause').first.click()
        nodes = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        rels = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(str(real_nodes) + " nodes", nodes)
        self.assertEqual(str(real_rels) + " relationships", rels)

    def test_node_rel_count_three(self):
        '''
        This test show that reflexive outgoing `relationships` DO count if
        there are NO more relationships.
        '''
        real_nodes = 0
        real_rels = 0
        create_graph(self)
        create_schema(self)
        # Creating a nodetype: "First"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("First")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        # Creating another nodetype: "Second"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("Second")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        self.browser.find_by_id('dataMenu').first.click()
        # Creating an allowed relationship: "First -> First"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToFirst')
        self.browser.select('target', '1')
        self.browser.find_by_value('Save Type').first.click()
        # Creating an allowed relationship: "First -> Second"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToSecond')
        self.browser.select('target', '2')
        self.browser.find_by_value('Save Type').first.click()
        # Creating a node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating a node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second3")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Editing the "First1" node
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption list']")[0].click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First1"
        self.browser.find_by_value('Save First').first.click()
        # Creating another node of the "First" type with relationships
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First3")
        # Adding more "FirstToFirst" outgoing relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[0].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First3"
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Checking the counts
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('sigma-pause').first.click()
        nodes = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        rels = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(str(real_nodes) + " nodes", nodes)
        self.assertEqual(str(real_rels) + " relationships", rels)

    def test_node_rel_count_four(self):
        '''
        This test show that when there are reflexive incoming `relationships`
        only count those.
        '''
        real_nodes = 0
        real_rels = 0
        create_graph(self)
        create_schema(self)
        # Creating a nodetype: "First"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("First")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        # Creating another nodetype: "Second"
        self.browser.find_link_by_href(
            '/schemas/bobs-graph/types/create/').first.click()
        self.browser.find_by_name('name').first.fill("Second")
        self.browser.find_by_name('properties-0-key').first.fill('Name')
        self.browser.find_by_name('properties-0-display').first.check()
        self.browser.find_by_value('Save Type').first.click()
        self.browser.find_by_id('dataMenu').first.click()
        # Creating an allowed relationship: "First -> First"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToFirst')
        self.browser.select('target', '1')
        self.browser.find_by_value('Save Type').first.click()
        # Creating an allowed relationship: "First -> Second"
        self.browser.find_by_id('allowedRelations').first.click()
        self.browser.select('source', '1')
        self.browser.find_by_name('name').fill('FirstToSecond')
        self.browser.select('target', '2')
        self.browser.find_by_value('Save Type').first.click()
        # Creating a node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "First" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating a node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second1")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second2")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Creating another node of the "Second" type
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[1].click()
        self.browser.find_by_name('Name').first.fill("Second3")
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Editing the "First1" node
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption list']")[0].click()
        self.browser.find_by_xpath("//td[@class='dataList']/a[@class='edit']").first.click()
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[0].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First1"
        self.browser.find_by_value('Save First').first.click()
        # Creating another node of the "First" type with relationships
        self.browser.find_by_id('dataMenu').first.click()
        self.browser.find_by_xpath("//a[@class='dataOption new']")[0].click()
        self.browser.find_by_name('Name').first.fill("First3")
        # Adding more "FirstToSecond" relationship forms
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[1].click()
        self.browser.find_by_xpath("//a[@class='addButton inFormsets']")[2].click()
        # Adding the relationships
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[1].fill('Second1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[2].fill('Second2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[3].fill('Second3')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[4].fill('First1')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        self.browser.find_by_xpath("//li[@class='token-input-input-token']/input")[5].fill('First2')
        self.browser.is_element_present_by_id("id_user_wait", 5)
        self.browser.find_by_xpath("//div[@class='token-input-dropdown']//li[@class='token-input-dropdown-item2 token-input-selected-dropdown-item']/b").first.click()
        real_rels += 1
        # Saving "First3"
        self.browser.find_by_xpath("//span[@class='buttonLinkOption buttonLinkLeft']/input").first.click()
        real_nodes += 1
        # Checking the counts
        self.browser.find_link_by_href('/graphs/bobs-graph/').first.click()
        self.browser.find_by_id('sigma-pause').first.click()
        nodes = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-nodes']").first.value
        rels = self.browser.find_by_xpath("//div[@class='flags-block']/span[@class='graph-relationships']").first.value
        self.assertEqual(str(real_nodes) + " nodes", nodes)
        self.assertEqual(str(real_rels) + " relationships", rels)
