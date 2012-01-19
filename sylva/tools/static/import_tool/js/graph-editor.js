if ($ == undefined) {
  $ = django.jQuery;
}

var GraphEditor = {
  DEBUG: true,

  USES_DRAWER: undefined,
  USES_TYPES: undefined,

  PDE_URL: "/js/graphdrawer.pde",

  // This parameter should be set to true with long batch
  // operations (loading from GEXF) and set to false again
  // when done. Method "refresh" should be manually called
  _stopRefreshing: false,

  graphNodesId: "id_graph_nodes",
  graphEdgesId: "id_graph_edges",
  progressBarId: "progress-bar",

  progressBar: {
    show: function() {
      $('#'+GraphEditor.progressBarId).show();
      GraphEditor._stopRefreshing = true;
    },
    hide: function() {
      $('#'+GraphEditor.progressBarId).hide();
      GraphEditor._stopRefreshing = false;
      GraphEditor.refresh();
    },
    set: function(value) {$('#'+GraphEditor.progressBarId+' progress').val(value);}
  },

  addNodeToList: function(name){
    var nodeList = document.getElementById("node-list");
    var node = this.getGraphNodesJSON()[name];
    if (node.type != undefined){
      name += ' (type: ' + node.type  + ')';
    }
    this.addElementToList(name, nodeList, "item");
  },

  addEdgeToList: function(name){
    var edgeList = document.getElementById("edge-list");
    this.addElementToList(name, edgeList, "item");
  },

  addElementToList: function(name, list, itemClass){
    var item = document.createElement('li');
    var itemValue = document.createElement('span');
    itemValue.appendChild(document.createTextNode(name));
    item.appendChild(itemValue);
    if (itemClass !== undefined){
      item.setAttribute("class", itemClass);
    }
    list.appendChild(item);
  },

  addNode: function(_name, _properties){
    // Only prompts if the parameter is not sent
    var nodeName = _name !== undefined ? _name : prompt("Enter new node name");
    
    var json = this.getGraphNodesJSON();
    if (this.nodeExists(nodeName)){
      alert("ERROR: That node already exists");
      return;
    }
    var data = _properties !== undefined ? _properties : {};
    if (this.USES_TYPES) {
      data["type"] = data.hasOwnProperty('type') ? data["type"] : prompt("Enter new node type");
    }
    json[nodeName] = data;
    this.setGraphNodesJSON(json);
    if (this.USES_DRAWER) {
      if (data.hasOwnProperty('position')){
        this.drawer.addLocatedNode(nodeName, _properties['position']['x'], _properties['position']['y'])
      } else {
        this.drawer.addNode(nodeName);
      }
    }
  },

  deleteNode: function(name){
    var nodeName = prompt("Enter node to be deleted");
    if (!this.nodeExists(nodeName)){
      alert("ERROR: Unknown node: " + nodeName);
      return;
    }
    if (this.nodeBelongsToEdge(nodeName)){
      alert("ERROR: node " + nodeName + " belongs to a relationship. Delete relationship first");
      return;
    }
    var json = this.getGraphNodesJSON();
    delete json[nodeName];
    this.setGraphNodesJSON(json);
    if (this.USES_DRAWER) {
      this.drawer.deleteNode(nodeName);
    }
  },

  addEdge: function(_source, _type, _target){
    // Only prompts if the parameter is not sent
    var edgeSource = _source !== undefined ? _source : prompt("Enter source node");
    var edgeType = _type !== undefined ? _type: prompt("Enter relationship type");
    var edgeTarget = _target !== undefined ? _target: prompt("Enter target node");
    
    if (!this.nodeExists(edgeSource)){
      alert("ERROR: Unknown node: " + edgeSource);
      return;
    }
    if (!this.nodeExists(edgeTarget)){
      alert("ERROR: Unknown node: " + edgeTarget);
      return;
    }
    if (edgeType == "") {
      alert("Relationship type is mandatory");
      return;
    }
    var json = this.getGraphEdgesJSON();
    var newEdge = {"source": edgeSource, "target": edgeTarget, "type": edgeType};
    json.push(newEdge);
    this.setGraphEdgesJSON(json);
    if (this.USES_DRAWER) {
      this.drawer.addEdge(edgeSource, edgeType, edgeTarget);
    }
  },

  deleteEdge: function(number){
    var edgeNumber= parseInt(prompt("Enter edge number to be deleted")) - 1;
    var json = this.getGraphEdgesJSON();
    if (edgeNumber>json.length || edgeNumber<0) {
      alert("Invalid edge number: " + (edgeNumber+1));
      return;
    }
    var newList = [];
    $.each(json, function(index, value){
      if (index!=edgeNumber) {
        newList.push(value);
      } else {
        if (GraphEditor.USES_DRAWER) {
          GraphEditor.drawer.deleteEdge(value["source"],
                                      value["type"],
                                      value["target"]);
        }
      }
    });
    this.setGraphEdgesJSON(newList);
  },

  nodeExists: function(nodeName){
    var nodesJSON = this.getGraphNodesJSON();
    return nodesJSON.hasOwnProperty(nodeName);
  },

  nodeBelongsToEdge: function(name){
    var edges = this.getGraphEdgesJSON();
    for(var i=0;i<edges.length;i++){
      if (edges[i].source==name || edges[i].target==name)
        return true;
    }
    return false;
  },

  getGraphNodesJSON: function(){
    return JSON.parse($('#'+this.graphNodesId).val());
  },

  getGraphEdgesJSON: function(){
    return JSON.parse($('#'+this.graphEdgesId).val());
  },

  setGraphNodesJSON: function(json){
    $('#'+this.graphNodesId).val(JSON.stringify(json));
    if (!this._stopRefreshing) {
      this.refresh();
    }
  },

  setGraphEdgesJSON: function(json){
    $('#'+this.graphEdgesId).val(JSON.stringify(json));
    if (!this._stopRefreshing) {
      this.refresh();
    }
  },

  clearLists: function(){
    $.each($(".item"), function(index, item){
      item.parentNode.removeChild(item);
    });
  },

  loadGEXF: function(){
        function handleFileSelect(evt) {
        GraphEditor.progressBar.show();
        var files = evt.target.files; // FileList object
    
        for (var i = 0, f; f = files[i]; i++) {
    
          var reader = new FileReader();
    
          // Closure to capture the file information.
          reader.onload = (function(theFile) {
            return function(e) {
              var gexfContent = e.target.result;
              // GEXF IMPORTATION FUNCTION
              $(gexfContent).find('node').each(function(){
                GraphEditor.addNode($(this).attr('label'), {
                                    "score": 0,
                                    "type": $(this).find('attvalue').attr('value'),
                                    "position": {
                                      "x":$(this).find('viz\\:position').attr('x'),
                                      "y":$(this).find('viz\\:position').attr('y')
                                    }
                });
              });
              $(gexfContent).find('edge').each(function(){
                var sourceId = $(this).attr('source');
                var targetId = $(this).attr('target');
                var source = $(gexfContent).find('node#'+sourceId).attr('label');
                var target = $(gexfContent).find('node#'+targetId).attr('label');
                var type = $(this).attr('label');
                GraphEditor.addEdge(source, type, target);
              });
              GraphEditor.progressBar.hide();
            };
          })(f);
    
          reader.readAsText(f);
        }
      }
    document.getElementById('files').addEventListener('change', handleFileSelect, false);
  },
  
  refresh: function(){
    //Clear everything
    this.clearLists();
    //Set nodes
    $.each(this.getGraphNodesJSON(), function(index, item){
      GraphEditor.addNodeToList(index);
    });
    //Set edges
    $.each(this.getGraphEdgesJSON(), function(index, item){
      var edgeText = item.source + " -> " + item.target + " (" + item.type + ")";
      GraphEditor.addEdgeToList(edgeText);
    });
  },

  loadSchema: function(){
    // Introspect graph schema
    var nodes = this.getGraphNodesJSON();
    var nodeTypes = {};
    $.each(nodes, function(index, item){
      if (!nodeTypes.hasOwnProperty(item.type)) {
        nodeTypes[item["type"]] = {};
      }
    });
    var edgeTypes = {}
    $.each(this.getGraphEdgesJSON(), function(index, item){
      var edgeLabel = nodes[item.source].type + "_" + item.type + "_" + nodes[item.target].type;
      if (!edgeTypes.hasOwnProperty(edgeLabel)){
        edgeTypes[edgeLabel] = {
          source: nodes[item.source].type,
          label: item.type,
          target: nodes[item.target].type
        };
      }
    });
    var schema = {
      nodeTypes: nodeTypes,
      allowedEdges: edgeTypes
    }
    this.schemaToList('graph-schema-nodes',
                      'graph-schema-edges',
                      schema);
    $('#id_graph_schema').val(JSON.stringify(schema));
    return schema;
  },

  schemaToList: function(nodeElement, edgeElement, schema){
    var list = document.getElementById(nodeElement);
    $.each(schema.nodeTypes, function(index, value){
      GraphEditor.addElementToList(index, list);
    });
    var list = document.getElementById(edgeElement);
    $.each(schema.allowedEdges, function(index, value){
      var edgeText = value.source + " -> " + value.target + " (" + value.label + ")";
      GraphEditor.addElementToList(edgeText, list);
    });
  },

  init: function(){
    // Default parameters
    this.USES_DRAWER = (this.USES_DRAWER != undefined) ? this.USES_DRAWER : true;
    this.USES_TYPES = (this.USES_TYPES != undefined) ? this.USES_TYPES : true;

    this.loadGEXF();
    GraphEditor.refresh();
    
    // Black magic to have the Processing drawer ready to call the drawInitialData method
    // The ajax petition is a straightforward copy from the Processing original code in
    // its init method
    if (GraphEditor.USES_DRAWER){
      $.ajax({
        url: GraphEditor.PDE_URL,
        success: function(block, error){
          GraphEditor.drawer = new Processing(document.getElementById('graphcanvas'), block);
          GraphEditor.drawInitialData();
        },
        error: function(){console.log("error")}
        }
      );
    }
    GraphEditor.refresh();
  },
  
  drawInitialData: function(){
    $.each(this.getGraphNodesJSON(), function(index, item){
      if (item.hasOwnProperty('position')){
        this.drawer.addLocatedNode(index, item['position']['x'], item['position']['y'])
      } else {
        this.drawer.addNode(index);
      }
    });
    $.each(this.getGraphEdgesJSON(), function(index, item){
      this.drawer.addEdge(item.source, item.type, item.target);
    });
  }
}

$(document).ready(function(){
  // Events linking
  $('#schema-link').click(function(){
    GraphEditor.loadSchema();
  });

  //Progress bar
  $('#progress-bar').hide();
});

