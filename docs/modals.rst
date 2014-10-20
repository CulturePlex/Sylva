Modals
======

It has 4 main parts in 2 blocks, you need to use entire blocks. Also the first one and the server side code are obligatory:

Block I
-------

* preapreModal: Gets the HTML to show. Its parameters are:

  * url: Where to get the HTML
  * showOverlay: Does the background need to be dark? (Only for the first modal)
  * modalActions: A dictionary with three functions, two of them for use them in the next function

* showModal: Changes what its necesary in the recevied HTML with the the help of two of the three fucntions commented before. Its parameter are:

  * html: The HTML to show
  * modalActions: A dictionary with three functions, here it only use two of them:

    * preProcessHTML: Here you can change wathever you need from your HTML and return a dictionary with the objects you'll ned in the 'onShow' function need from your HTML
    * onShow: Function for call it in the 'onShow' event of the dropit library. Here you can change again whatever you need. Also you receive a dictonary with the returned object in the 'preProcessHTML' function plus the next ones:

      * html: The HTML inside the modal
      * modalHTML: The parent HTML element that contains the modal
      * windowHeight: The height of the browser window
      * windowWidth: The width of the browser window
      * modalPadding: The padding added to the modal HTML element

Block II
--------

* saveModalForm: Send a form to the backend for save it. Its parameter is a dictonary called 'requestInfo' with these keys:

  * url: The URL for perform the request
  * formSelector: The selector of the form to serialize
  * extraParams: A string to append at the end of the serialized form

* handleFormServerResponse: The only 'changing' function of the framework, because it needs to be changed with new behaviours. It handles the response of the previous function, 'saveModalForm', by reloading a from with erros or whatever you need.

Server side
-----------

The views always return a JSON for the requests with a param *as_modal* in the GET or POST dictionaries. The JSON must have:

* type: *html* or *action*
* action: It's like an identifier for the modal
* html: Only for the *html type*
* Whatever you need: For the *action type*

Play with the *as_param* variable for return a normal view or a *modal_view*.

How to use the *mini-framework*
-------------------------------

Create a dictionary like the *editNode* or the *deleteNode* of the *modal.js* file. After that, call whenever you need the *start* function of that dictionary.

Created modals
--------------

The next list is a list of the created modals, the dictionaries commented in the previous section.

* editNode

  * View: data/views.py:nodes_edit
  * Template: data/templates/nodes_editcreate.html

* deleteNode

  * View: data/views.py:nodes_delete
  * Template: data/templates/nodes_delete.html

* createNode

  * View: data/views.py:nodes_create
  * Template: data/templates/nodes_editcreate.html

* listNodes

  * View: data/views.py:nodes_list_full
  * Template: data/templates/node_list.html

* collaborators

  * View: graphs/views.py:graph_collaborators
  * Template: graphs/templates/graph_collaborators.html

* importSchema

  * View: schema/views.py:schema_import
  * Template: schema/templates/schema_import.html

* importData

  * View: tools/vies.py:graph_import_tool
  * Template: tools/templates/graph_import_tool.html
