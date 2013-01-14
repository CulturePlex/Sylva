// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, prompt:true, alert:true, FileReader:true, Processing:true,
clearTimeout:true */


/****************************************************************************
 * Processing.js visualization
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  // setTimeout id.
  var timeout_id = 0;

  function updateInfo(evt, nodeName, nodeId) {
    if (nodeId === undefined) {
      nodeId = nodeName;
    }

    var expandNode = function(){
      var edgeId;
      var edgeIds = $.map(sylv.edges, function(e) { return e.id; });

      var expandNodeLinkURL = sylv.expandNodeLinkURL;
      expandNodeLinkURL = expandNodeLinkURL.replace('0/expand/', nodeId + '/expand/');

      $.ajax({
        url: expandNodeLinkURL,
        success: function(result){
          var parsedResult = JSON.parse(result);
          var newNodes = parsedResult.nodes;
          var newEdges = parsedResult.edges;

          $.each(newNodes, function(i, node){
            if (!sylv.nodes.hasOwnProperty(i)) {
              sylv.GraphEditor.addNode(i, node);
              sylv.nodes[i] = node;
            }
          });

          $.each(newEdges, function(i, edge){
            edgeId = edge.id;
            if ($.inArray(edgeId, edgeIds) === -1) {
              sylv.edges.push(edge);
              sylv.GraphEditor.addEdge(edge.source, edge.type, edge.target, edge);
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

      $.each(sylv.nodes, function(i, node) {
        if (node.id == nodeId) {
          selectedNode = node;
          selectedNodeName = i;
          return false;
        }
      });

      if (selectedNode === undefined) { return false; }

      $.each(sylv.edges, function(i, edge) {
        if (edge.source === selectedNodeName || edge.target === selectedNodeName) {
          indexesToDelete.push(i);
        }
      });
      $.each(indexesToDelete, function(i, index) {
          sylv.edges.splice(index,1);
          sylv.GraphEditor.deleteEdge(index);
      });
      sylv.GraphEditor.deleteNode(selectedNodeName);
      delete sylv.nodes[selectedNodeName];

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
    sylv.GraphEditor.PDE_URL = sylv.PDE_URL;
    sylv.GraphEditor.USES_DRAWER = true;

    sylv.GraphEditor.init();

    $('#id_graph_nodes').val(JSON.stringify(sylv.nodes));
    $('#id_graph_edges').val(JSON.stringify(sylv.edges));

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
        sylv.nodeTypesLegend[element.getKey()] = '#' + element.getValue();
        sylv.colors[element.getKey()] = sylv.nodeTypesLegend[element.getKey()];
      }
      $('#node-type-legend').empty();
      var list = $('#node-type-legend').append($('<ul>'));
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(sylv.nodeTypesLegend, function(type, color){
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
    var size = sylv.size;
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
  window.sylv.Processing = {
    updateInfo: updateInfo,
    updateInfoRelationship: updateInfoRelationship,
    init: init,
    start: start,
    stop: stop
  };

})(sylv, jQuery, window, document);
