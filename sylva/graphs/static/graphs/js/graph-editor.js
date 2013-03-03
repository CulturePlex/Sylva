// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, DOMParser:true */

;(function(sylv, $, window, document, undefined) {

  var GraphEditor = {
    DEBUG: true,

    USES_DRAWER: undefined,
    USES_TYPES: undefined,

    PDE_URL: sylv.PDE_URL,

    // This parameter should be set to true with long batch
    // operations (loading from GEXF) and set to false again
    // when done. Method "refresh" should be manually called
    _stopRefreshing: false,

    graphNodesId: "id_graph_nodes",
    graphEdgesId: "id_graph_edges",
    progressBarId: "progress-bar",

    schema: null,

    progressBar: {
      show: function() {
        $('#'+GraphEditor.progressBarId).show();
        GraphEditor._stopRefreshing = true;
      },
      hide: function() {
        $('#'+GraphEditor.progressBarId).hide();
        GraphEditor._stopRefreshing = false;
        $('body').trigger($.Event('fileLoaded'));
        GraphEditor.refresh();
      },
      set: function(value) {$('#'+GraphEditor.progressBarId+' progress').val(value);}
    },

    addNodeToList: function(name){
      var nodeList = document.getElementById("node-list");
      var node = this.getGraphNodesJSON()[name];
      if (node.type !== undefined){
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
        console.log("ERROR: That node already exists");
        return;
      }
      var data = _properties !== undefined ? _properties : {};
      if (this.USES_TYPES) {
        data.type = data.hasOwnProperty('type') ? data.type : prompt("Enter new node type");
      }
      json[nodeName] = data;
      this.setGraphNodesJSON(json);
      if (this.USES_DRAWER) {
        if (data.hasOwnProperty('position')){
          this.drawer.addLocatedNode(nodeName, _properties.position.x, _properties.position.y, data.type, data.id);
        } else {
          this.drawer.addNode(nodeName, data.type, data.id);
        }
      }
    },

    deleteNode: function(name){
      var nodeName = (name !== undefined) ? name : prompt("Enter node to be deleted");
      if (!this.nodeExists(nodeName)){
        console.log("ERROR: Unknown node: " + nodeName);
        return;
      }
      if (this.nodeBelongsToEdge(nodeName)){
        console.log("ERROR: node " + nodeName + " belongs to a relationship. Delete relationship first");
        return;
      }
      var json = this.getGraphNodesJSON();
      delete json[nodeName];
      this.setGraphNodesJSON(json);
      if (this.USES_DRAWER) {
        this.drawer.deleteNode(nodeName);
      }
    },

    addEdge: function(_source, _type, _target, _properties){
      // Only prompts if the parameter is not sent
      var edgeSource = _source !== undefined ? _source : prompt("Enter source node");
      var edgeType = _type !== undefined ? _type: prompt("Enter relationship type");
      var edgeTarget = _target !== undefined ? _target: prompt("Enter target node");

      if (!this.nodeExists(edgeSource)){
        console.log("ERROR: Unknown source node: " + edgeSource);
        return;
      }
      if (!this.nodeExists(edgeTarget)){
        console.log("ERROR: Unknown target node: " + edgeTarget);
        return;
      }
      if (edgeType === "") {
        console.log("ERROR: empty edge label");
        return;
      }
      var json = this.getGraphEdgesJSON();
      var properties = (_properties !== undefined) ? _properties : {};
      var newEdge = {source: edgeSource, target: edgeTarget, type: edgeType, properties: properties};
      json.push(newEdge);
      this.setGraphEdgesJSON(json);
      if (this.USES_DRAWER) {
        var edgeId = (_properties.hasOwnProperty('id')) ? _properties.id : undefined;
        this.drawer.addEdge(edgeSource, edgeType, edgeTarget, edgeId);
      }
    },

    deleteEdge: function(number){
      var edgeNumber = (number !== undefined) ? number : parseInt(prompt("Enter edge number to be deleted"), 10) - 1;
      var json = this.getGraphEdgesJSON();
      if (edgeNumber>json.length || edgeNumber<0) {
        console.log("Invalid edge number: " + (edgeNumber+1));
        return;
      }
      var newList = [];
      $.each(json, function(index, value){
        if (index!=edgeNumber) {
          newList.push(value);
        } else {
          if (GraphEditor.USES_DRAWER) {
            GraphEditor.drawer.deleteEdge(value.source,
                                          value.type,
                                          value.target);
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

    edgeText: function(sourceLabel, targetLabel, typeLabel){
      return sourceLabel + ' &rarr; ' + targetLabel + ' (' + typeLabel + ')';
    },

    loadGEXF: function() {
      function handleFileSelect(evt) {
        GraphEditor.progressBar.show();

        var files = evt.target.files; // FileList object
        var reader = new FileReader();

        reader.onload = function(e) {
          var parser = new DOMParser();
          var gexf = parser.parseFromString(e.target.result, "text/xml");

          var nodesAttributes = {};
          var edgesAttributes = {};
          var attributesNodes = gexf.getElementsByTagName('attributes');

          var id, title, type;
          var attribute, attributeId, attributeTitle;
          var i, j, k, li, lj, lk;

          // loop through attributes elements and store attributes for nodes and edges
          for (i = 0, li = attributesNodes.length; i< li; i++) {
            var attributesNode = attributesNodes[i];

            if (attributesNode.getAttribute('class') == 'node') {
              var attributeNodes = attributesNode.getElementsByTagName('attribute');

              for (j = 0, lj = attributeNodes.length; j < lj; j++) {
                var attributeNode = attributeNodes[j];

                id = attributeNode.getAttribute('id').trim();
                title = attributeNode.getAttribute('title').trim();
                type = attributeNode.getAttribute('type').trim();

                // store node attributes
                nodesAttributes[id] = {title: title, type: type};
              }
            } else if (attributesNode.getAttribute('class') == 'edge') {
              var attributeEdges = attributesNode.getElementsByTagName('attribute');

              for (j = 0, lj = attributeEdges.length; j < lj; j++) {
                var attributeEdge = attributeEdges[j];

                id = attributeEdge.getAttribute('id').trim();
                title = attributeEdge.getAttribute('title').trim();
                type = attributeEdge.getAttribute('type').trim();

                // store edge attributes
                edgesAttributes[id] = {title: title, type: type};
              }
            }
          }

          var nodesNodes = gexf.getElementsByTagName('nodes');

          // loop through <nodes> elements
          for (i = 0, li = nodesNodes.length; i < li; i++) {
            var nodesNode = nodesNodes[i];
            var nodeNodes = nodesNode.getElementsByTagName('node');

            // loop through <node> elements
            for (j = 0, lj = nodeNodes.length; j < lj; j++) {
              var nodeNode = nodeNodes[j];

              var nodeId = nodeNode.getAttribute('id').trim(),
                  nodeLabel = nodeNode.getAttribute('label').trim(),
                  nodeType = nodeNode.getAttribute('type').trim();
              // TODO: store node position (x,y)
              var nodeAttributes = {_label: nodeLabel, type: nodeType};

              var attvalueNodes = nodeNode.getElementsByTagName('attvalue');

              // loop through <attvalue> elements
              for (k = 0, lk = attvalueNodes.length; k < lk; k++) {
                var attvalueNode = attvalueNodes[k];

                attributeId = attvalueNode.getAttribute('for');
                attribute = nodesAttributes[attributeId];
                if (attribute !== undefined) {
                  attributeTitle = attribute.title;
                  nodeAttributes[attributeTitle] = attvalueNode.getAttribute('value');
                }
              }

              // finally, add node
              GraphEditor.addNode(nodeId, nodeAttributes);
            }
          }

          var edgesNodes = gexf.getElementsByTagName('edges');

          // loop through <edges> elements
          for (i = 0, li = edgesNodes.length; i < li; i++) {
            var edgesNode = edgesNodes[i];
            var edgeNodes = edgesNode.getElementsByTagName('edge');

            // loop through <edge> elements
            for (j = 0, lj = edgeNodes.length; j < lj; j++) {
              var edgeNode = edgeNodes[j];

              var edgeSource = edgeNode.getAttribute('source').trim(),
                  edgeTarget = edgeNode.getAttribute('target').trim(),
                  edgeType = edgeNode.getAttribute('label').trim();

              var edgeAttributes = {};

              var attvalueEdges = edgeNode.getElementsByTagName('attvalue');

              // loop through <attvalue> elements
              for (k = 0, lk = attvalueEdges.length; k < lk; k++) {
                var attvalueEdge = attvalueEdges[k];

                attributeId = attvalueEdge.getAttribute('for');
                if (attributeId !== "_id") {
                  attribute = edgesAttributes[attributeId];
                  if (attribute !== undefined) {
                    attributeTitle = attribute.title;
                    edgeAttributes[attributeTitle] = attvalueEdge.getAttribute('value');
                  }
                }
              }

              // finally, add edge
              GraphEditor.addEdge(edgeSource, edgeType, edgeTarget, edgeAttributes);
            }
          }

          GraphEditor.progressBar.hide();
        };

        reader.readAsText(files[0]);
      }
      $('#files').bind('change', handleFileSelect);
    },

    loadCSVs: function(){
      // Load nodes
      function handleNodeFile(evt) {
        $('#csv-nodes-progress-bar').show();

        var f = evt.target.files[0];
        var reader = new FileReader();

        reader.onload = (function(nodeFile){
          return function(e){
            var titleRow;
            var attributes;

            var content = e.target.result;
            var lines = content.split('\n');

            $.each(lines, function(index, line){
              // Ignoring blank lines
              if (!!line) {
                // TODO Text may be quoted
                var columns = line.split(',');

                // First line contains the labels of each column
                if (index === 0) {
                  titleRow = columns;
                } else {
                  attributes = {};
                  $.each(columns, function(i, item) {
                    attributes[titleRow[i]] = item;
                  });

                  GraphEditor.addNode(columns[0], attributes);
                }
              }
            });
            $('#csv-nodes-progress-bar').hide();
          };
        })(f);

        reader.readAsText(f);
      }

      function handleEdgeFile(evt) {
        $('#csv-edges-progress-bar').show();

        var f = evt.target.files[0];
        var reader = new FileReader();

        reader.onload = (function(edgeFile){
          return function(e){
            var titleRow;
            var source, type, target;
            var attributes;

            var content = e.target.result;
            var lines = content.split('\n');

            $.each(lines, function(index, line){
              // Ignoring blank lines
              if (!!line) {
                // TODO Text may be quoted
                var columns = line.split(',');

                // First line contains the labels of each column
                if (index === 0) {
                  titleRow = columns;
                } else {
                  source = undefined;
                  type = undefined;
                  target = undefined;
                  attributes = {};
                  $.each(columns, function(i, item) {
                    switch (titleRow[i]) {
                      case "source":
                        source = item;
                        break;
                      case "type":
                        type = item;
                        break;
                      case "target":
                        target = item;
                        break;
                      default:
                        attributes[titleRow[i]] = item;
                    }
                  });

                  GraphEditor.addEdge(source, type, target, attributes);
                }
              }
            });
            $('#csv-edges-progress-bar').hide();
          };
        })(f);

        reader.readAsText(f);
      }

      $('#csv-nodes').bind('change', handleNodeFile);
      $('#csv-edges').bind('change', handleEdgeFile);
    },

    refresh: function(){
      //Clear everything
      this.clearLists();
      //Set nodes
      var nodes = this.getGraphNodesJSON();
      $.each(nodes, function(index, item){
        GraphEditor.addNodeToList(index);
      });
      //Set edges
      var edges = this.getGraphEdgesJSON();
      $.each(edges, function(index, item){
        var edgeText = GraphEditor.edgeText(item.source, item.target, item.type);
        GraphEditor.addEdgeToList(edgeText);
      });
    },

    loadSchema: function(nodeTypeLabel, edgeTypeLabel){
      var _nodeTypeLabel = (nodeTypeLabel === undefined) ? "type" : nodeTypeLabel;
      var _edgeTypeLabel = (edgeTypeLabel === undefined) ? "type" : edgeTypeLabel;
      // Introspect graph schema
      var nodes = this.getGraphNodesJSON();
      var nodeTypes = {};
      var nodeTypeProperties;
      $.each(nodes, function(index, item){

        // Node properties
        nodeTypeProperties = {_nameLabel: {}};
        $.each(item, function(pIndex, pValue){
          if (pIndex !== _nodeTypeLabel && pIndex !== "position"){
            nodeTypeProperties[pIndex] = {};
          }
        });
        if (!nodeTypes.hasOwnProperty(item[_nodeTypeLabel])) {
          nodeTypes[item[_nodeTypeLabel]] = nodeTypeProperties;
        } else {
          $.each(nodeTypeProperties, function(pIndex, pValue){
            nodeTypes[item[_nodeTypeLabel]][pIndex] = {};
          });
        }
      });
      var edgeTypes = {};
      var edges = this.getGraphEdgesJSON();
      $.each(edges, function(index, item){
        var edgeLabel = nodes[item.source].type + "_" +
            item[_edgeTypeLabel] +
            "_" + nodes[item.target].type;
        if (!edgeTypes.hasOwnProperty(edgeLabel)){
          edgeTypes[edgeLabel] = {
            source: nodes[item.source][_nodeTypeLabel],
            label: item[_edgeTypeLabel],
            target: nodes[item.target][_nodeTypeLabel],
            properties: item.properties
          };
        }
      });
      var schema = {
        nodeTypes: nodeTypes,
        allowedEdges: edgeTypes
      };
      this.schema = schema;
      this.schemaToList('graph-schema-nodes',
                        'graph-schema-edges',
                        schema);
      $('#id_graph_schema').val(JSON.stringify(schema));
      return schema;
    },

    schemaToList: function(nodeElement, edgeElement, schema){
      var elementType, elementAttributes, edgeText;
      // NodeType list
      $.each(schema.nodeTypes, function(index, value){
        // NodeType attributes
        elementAttributes = $('<ul>');
        $.each(value, function(index2, value2){
          elementAttributes.append(
            $('<li>').append(index2));
        });
        // NodeType element
        elementType = $('<li>');
        elementType.append(index);
        elementType.append(elementAttributes);
        $('#'+nodeElement).append(elementType);
      });


      // RelationshipType list
      $.each(schema.allowedEdges, function(index, value){

        // EdgeTypes attributes
        elementAttributes = $('<ul>');
        if (value.properties !== undefined){
          $.each(value.properties, function(index2, value2){
            elementAttributes.append(
              $('<li>').append(index2));
          });
        }

        // RelationshipType element
        elementType = $('<li>');
        edgeText = GraphEditor.edgeText(value.source.trim(), value.target.trim(), value.label.trim());
          elementType.append(edgeText);
          elementType.append(elementAttributes);
          $('#'+edgeElement).append(elementType);
      });
    },

    init: function(){
      // Default parameters
      this.USES_DRAWER = (this.USES_DRAWER !== undefined) ? this.USES_DRAWER : true;
      this.USES_TYPES = (this.USES_TYPES !== undefined) ? this.USES_TYPES : true;

      this.loadGEXF();
      this.loadCSVs();
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
              $('#graphcanvas').trigger('pde_loaded');
            }
          }
        );
      }
      GraphEditor.refresh();
    },

    drawInitialData: function(){
      var self = this;
      $.each(this.getGraphNodesJSON(), function(index, item){
        if (item.hasOwnProperty('position')){
          self.drawer.addLocatedNode(index, item.position.x, item.position.y, item.type, item.id);
        } else {
          self.drawer.addNode(index, item.type, item.id);
        }
      });
      var edges = this.getGraphEdgesJSON();
      $.each(edges, function(index, item){
        self.drawer.addEdge(item.source, item.type, item.target, item.id);
      });
    }
  };

  window.sylv.GraphEditor = GraphEditor;

})(sylv, jQuery, window, document);
