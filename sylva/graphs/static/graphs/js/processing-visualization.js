// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, prompt:true, alert:true, FileReader:true, Processing:true */

;(function(GraphEditor, nodes, edges, nodeTypesLegend, sylv, $, window, document, undefined) {

  function updateInfo(evt, nodeName, nodeId) {
    if (nodeId === undefined) {
      nodeId = nodeName;
    }

    var expandNode = function(){
      var edgeId;
      var edgeIds = $.map(edges, function(e) { return e.id; });

      var expandNodeLinkURL = sylv.expandNodeLinkURL;
      expandNodeLinkURL = expandNodeLinkURL.replace('0/expand/', nodeId + '/expand/');

      $.ajax({
        url: expandNodeLinkURL,
        success: function(result){
          var parsedResult = JSON.parse(result);
          var newNodes = parsedResult.nodes;
          var newEdges = parsedResult.edges;

          $.each(newNodes, function(i, node){
            if (!nodes.hasOwnProperty(i)) {
              GraphEditor.addNode(i, node);
              nodes[i] = node;
            }
          });

          $.each(newEdges, function(i, edge){
            edgeId = edge.id;
            if ($.inArray(edgeId, edgeIds) === -1) {
              edges.push(edge);
              GraphEditor.addEdge(edge.source, edge.type, edge.target, edge);
            }
          });

        }
      });
      return false;
    };

    var hideNode = function() {
      var selectedNode;
      var selectedNodeName;
      var indexesToDelete = [];

      $.each(nodes, function(i, node) {
        if (node.id == nodeId) {
          selectedNode = node;
          selectedNodeName = i;
          return false;
        }
      });

      if (selectedNode === undefined) { return false; }

      $.each(edges, function(i, edge) {
        if (edge.source === selectedNodeName || edge.target === selectedNodeName) {
          indexesToDelete.push(i);
        }
      });
      $.each(indexesToDelete, function(i, index) {
          edges.splice(index,1);
          GraphEditor.deleteEdge(index);
      });
      GraphEditor.deleteNode(selectedNodeName);
      delete nodes[selectedNodeName];
      return false;
    };

    var title = $('<h2>').text(nodeName);

    var editLinkURL = sylv.editLinkURL;
    editLinkURL = editLinkURL.replace('0/edit/', nodeId + '/edit/');
    var editLink = $('<a>')
      .attr('href', editLinkURL)
      .text('Edit node');

    var expandNodeLink = $('<a>')
      .attr('href', "#")
      .text('Expand node')
      .attr('href', 'javascript:void(0);') // TODO: refactor
      .click(expandNode);

    var hideNodeLink = $('<a>')
      .attr('href', "#")
      .text('Hide node')
      .attr('href', 'javascript:void(0);') // TODO: refactor
      .click(hideNode);

    $('#element-info')
      .empty()
      .append(title)
      .append(editLink)
      .append($('<br>'))
      .append(expandNodeLink)
      .append($('<br>'))
      .append(hideNodeLink);
  }

  function updateInfoRelationship(evt, relationshipId) {
    /*
    var editLinkURL = "";
    editLinkURL = editLinkURL.replace('0/edit/', relationshipId, '/edit/');
    var editLink = $('<a>')
      .attr('href', editLinkURL)
      .text('Edit relationship');
    */
    var title = $('<h2>').text("Relationship: " + relationshipId);

    $('#canvas-info')
      .empty()
      .append(title);
  }

  function init() {
    // // Events linking
    // $('#schema-link').click(function(){
    //   GraphEditor.loadSchema();
    // });

    // //Progress bar
    // $('#progress-bar').hide();

    $('#sec-debug').hide(); // Comment this line to Debug the graph creation
    GraphEditor.PDE_URL = sylv.PDE_URL;
    GraphEditor.USES_DRAWER = true;
    GraphEditor.init();
    $('#id_graph_nodes').val(JSON.stringify(nodes));
    $('#id_graph_edges').val(JSON.stringify(edges));

    // Attach the nodeSelect event from the canvas to update the
    // node info box
    $('body').bind('nodeSelected', updateInfo);
    $('body').bind('edgeSelected', updateInfoRelationship);

    // Type legend extraction from Processing
    function loadNodeTypes() {
      var element;
      var p = Processing.getInstanceById('graphcanvas');
      var colors = p.getNodeTypeColors();
      var iterator = colors.entrySet().iterator();
      while (iterator.hasNext()) {
        element = iterator.next();
        nodeTypesLegend[element.getKey()] = '#' + element.getValue();
      }
      // Create legend in canvas
      $('#node-type-legend').empty();
      var list = $('#node-type-legend').append($('<ul>'));
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(nodeTypesLegend, function(type, color){
        if (type !== "notype"){
          list
            .append($('<li>')
              .css({
                backgroundColor: color,
                minHeight: "20px",
                paddingLeft: "3px"
              })
              .text(type)
            );
        }
      });
    }
    setTimeout(loadNodeTypes, 200);
  }

  // reveal module
  window.sylv.Processing = {
    updateInfo: updateInfo,
    updateInfoRelationship: updateInfoRelationship,
    init: init
  };

})(sylv.GraphEditor, sylv.nodes, sylv.edges, sylv.nodeTypesLegend, sylv, jQuery, window, document);
