// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, prompt:true, alert:true, FileReader:true, Processing:true */


/****************************************************************************
 * Processing.js visualization
 ****************************************************************************/

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

    var expandNodeLink = $('<a>')
      .attr('href', "#")
      .text('Expand node')
      .attr('href', "#")
      .click(expandNode);

    var hideNodeLink = $('<a>')
      .attr('href', "#")
      .text('Hide node')
      .attr('href', "#")
      .click(hideNode);

    var htmlContent = $('<div>')
      .append(expandNodeLink)
      .append($('<br>'))
      .append(hideNodeLink);

    // Update node legend.
    sylv.Utils.updateNodeLegend(nodeId, nodeName, 'element-info', htmlContent);

  }

  function updateInfoRelationship(evt, relationshipId) {
    var title = $('<h2>').text("Relationship: " + relationshipId);
    $('#canvas-info')
      .empty()
      .append(title);
  }


  function init() {
    $('#sec-debug').hide();  // Comment this line to Debug the graph creation
    GraphEditor.PDE_URL = sylv.PDE_URL;
    GraphEditor.USES_DRAWER = true;

    GraphEditor.init();

    $('#id_graph_nodes').val(JSON.stringify(nodes));
    $('#id_graph_edges').val(JSON.stringify(edges));

    // Attach the nodeSelect event from the canvas to update the node info box
    $('body').bind('nodeSelected', updateInfo);
    $('body').bind('edgeSelected', updateInfoRelationship);

    $('#graphcanvas').on('pde_loaded', function(e) {
      e.stopPropagation();
      var p = Processing.getInstanceById('graphcanvas');
      var colors = p.getNodeTypeColors();
      var iterator = colors.entrySet().iterator();
      while (iterator.hasNext()) {
        var element = iterator.next();
        nodeTypesLegend[element.getKey()] = '#' + element.getValue();
        sylv.colors[element.getKey()] = nodeTypesLegend[element.getKey()];
      }
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
      $('#graphcanvas').trigger('graph_init');
    });
  }

  function start() {
    var processingInst = Processing.instances[0];
    if (processingInst) {
      processingInst.start();
    } else {
      init();
    }
  }

  function stop() {
    var processingInst = Processing.instances[0];
    if (processingInst) {
      processingInst.stop();
    }
  }

  // reveal module
  window.sylv.Processing = {
    updateInfo: updateInfo,
    updateInfoRelationship: updateInfoRelationship,
    init: init,
    start: start,
    stop: stop
  };

})(sylv.GraphEditor, sylv.nodes, sylv.edges, sylv.nodeTypesLegend, sylv, jQuery, window, document);
