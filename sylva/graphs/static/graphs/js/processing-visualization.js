// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, prompt:true, alert:true, FileReader:true, Processing:true,
clearTimeout:true */


/****************************************************************************
 * Processing.js visualization
 ****************************************************************************/

;(function(sylva, $, window, document, undefined) {

  // setTimeout id.
  var timeout_id = 0;

  function updateInfo(evt, nodeName, nodeId) {
    if (nodeId === undefined) {
      nodeId = nodeName;
    }

    var expandNode = function(){
      var edgeId;
      var edgeIds = $.map(sylva.edges, function(e) { return e.id; });

      var expandNodeLinkURL = sylva.expandNodeLinkURL;
      expandNodeLinkURL = expandNodeLinkURL.replace('0/expand/', nodeId + '/expand/');

      $.ajax({
        url: expandNodeLinkURL,
        success: function(result){
          var parsedResult = JSON.parse(result);
          var newNodes = parsedResult.nodes;
          var newEdges = parsedResult.edges;

          $.each(newNodes, function(i, node){
            if (!sylva.nodes.hasOwnProperty(i)) {
              sylva.GraphEditor.addNode(i, node);
              sylva.nodes[i] = node;
            }
          });

          $.each(newEdges, function(i, edge){
            edgeId = edge.id;
            if ($.inArray(edgeId, edgeIds) === -1) {
              sylva.edges.push(edge);
              sylva.GraphEditor.addEdge(edge.source, edge.type, edge.target, edge);
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

      $.each(sylva.nodes, function(i, node) {
        if (node.id == nodeId) {
          selectedNode = node;
          selectedNodeName = i;
          return false;
        }
      });

      if (selectedNode === undefined) { return false; }

      $.each(sylva.edges, function(i, edge) {
        if (edge.source === selectedNodeName || edge.target === selectedNodeName) {
          indexesToDelete.push(i);
        }
      });
      $.each(indexesToDelete, function(i, index) {
          sylva.edges.splice(index,1);
          sylva.GraphEditor.deleteEdge(index);
      });
      sylva.GraphEditor.deleteNode(selectedNodeName);
      delete sylva.nodes[selectedNodeName];

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
    sylva.Utils.updateNodeLegend(nodeId, nodeName, 'element-info', htmlContent);
    $('#element-info div').hide();

  }

  function updateInfoRelationship(evt, relationshipId) {
    var title = $('<h2>').text("Relationship: " + relationshipId);
    $('#canvas-info')
      .empty()
      .append(title);
  }


  function init() {
    $('#sec-debug').hide();  // Comment this line to Debug the graph creation
    sylva.GraphEditor.PDE_URL = sylva.PDE_URL;
    sylva.GraphEditor.USES_DRAWER = true;

    sylva.GraphEditor.init();

    $('#id_graph_nodes').val(JSON.stringify(sylva.nodes));
    $('#id_graph_edges').val(JSON.stringify(sylva.edges));

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
        sylva.nodeTypesLegend[element.getKey()] = '#' + element.getValue();
        sylva.colors[element.getKey()] = sylva.nodeTypesLegend[element.getKey()];
      }
      $('#node-type-legend').empty();
      var list = $('#node-type-legend').append($('<ul>'));
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(sylva.nodeTypesLegend, function(type, color){
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

    // Stop layout algoritm after `timeout` ms.
    var size = sylva.size;
    var timeout;
    if (size <= 20) {
      timeout = 10000;
    } else if (size <= 50) {
      timeout = 15000;
    } else if (size <= 100) {
      timeout = 20000;
    } else {
      timeout = 30000;
    }
    addTimeout(timeout);
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
    removeTimeout();
    var processingInst = Processing.instances[0];
    if (processingInst) {
      processingInst.stop();
    }
  }

  // Stop layout algoritm after `timeout` ms.
  function addTimeout(timeout) {
    timeout_id = setTimeout(function() {
      stop();
    }, timeout);
  }

  function removeTimeout() {
    clearTimeout(timeout_id);
  }

  // reveal module
  window.sylva.Processing = {
    updateInfo: updateInfo,
    updateInfoRelationship: updateInfoRelationship,
    init: init,
    start: start,
    stop: stop
  };

})(sylva, jQuery, window, document);
