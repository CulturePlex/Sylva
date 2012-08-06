// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true */


/****************************************************************************
 * Sigma.js visualizations
 ****************************************************************************/

;(function(sylv, sigma, $, window, document, undefined) {

  var isDrawing;

  var Sigma = {

    init: function() {
      // Parse nodes and edges.
      var sylv_nodes = JSON.parse(JSON.stringify(sylv.total_nodes));
      var sylv_edges = JSON.parse(JSON.stringify(sylv.total_edges));
      // Node info.
      var $tooltip;

      // Instanciate Sigma.js and customize rendering.
      var sigInst = sigma.init(document.getElementById('graph-container')).drawingProperties({
        defaultLabelColor: '#000',
        defaultLabelSize: 14,
        defaultLabelBGColor: '#fff',
        defaultLabelHoverColor: '#000',
        labelThreshold: 16,
        defaultEdgeType: 'curve'
      }).graphProperties({
        minNodeSize: 0.5,
        maxNodeSize: 5,
        minEdgeSize: 3,
        maxEdgeSize: 3
      }).mouseProperties({
        maxRatio: 32
      });

      // Add nodes.
      for (var n in sylv_nodes) {
        sigInst.addNode(n, {
          x: Math.random(),
          y: Math.random(),
          color: sylv.colors[sylv_nodes[n].type]
        });
      }

      // Add edges.
      for (var e in sylv_edges) {
        sigInst.addEdge(sylv_edges[e].id, sylv_edges[e].source, sylv_edges[e].target);
      }

      // Show node info and hide the rest of nodes and edges.
      sigInst.bind('overnodes', function(event) {
        var nodes = event.content;
        var nodePK = nodes[0];  // node primary key
        var neighbors = {};
        var isOrphan = true;

        // Converts obj properties into a string.
        var attributesToString = function(obj) {
          var str = [];
          for (var prop in obj) {
            if (obj.hasOwnProperty(prop)) {
              str.push('<li>' + prop + ': ' + obj[prop] + '</li>');
            }
          }
          return str.join('');
        };

        var showInfo = $('#sigma-node-info').prop('checked');
        if (showInfo) {
          // Show node popup info.
          sigInst.iterNodes(function(node) {
            $tooltip =
              $('<div class="node-info"></div>')
                .append('<ul>' + attributesToString(sylv_nodes[nodePK]) + '</ul>')
                .css({
                  'left': node.displayX+212,
                  'top': node.displayY+61
                });
            $('#graph-container').append($tooltip);
          }, [nodePK]);
        }

        // Hide edges and nodes.
        sigInst.iterEdges(function(e) {
          if (nodes.indexOf(e.source) >= 0 || nodes.indexOf(e.target) >= 0) {
            neighbors[e.source] = true;
            neighbors[e.target] = true;
            isOrphan = false;
          }
        });

        if (isOrphan) {
          neighbors[nodePK] = true;
        }

        sigInst.iterNodes(function(n) {
          if (!neighbors[n.id]) {
            n.hidden = true;
          }
        });

        // draw graph.
        sigInst.draw();

        // Update node legend.
        var nodeEditURL = sylv.editLinkURL.replace(/nodes\/0\/edit/,
                                                   'nodes/' + sylv_nodes[nodePK].id + '/edit');
        $('#element-info').html(
            '<h2>' + nodePK + '</h2>' +
            '<a href="' + nodeEditURL + '">Edit node</a>'
        );
      });

      // Hide node popup info and show the rest of nodes and edges.
      sigInst.bind('outnodes', function(event) {
        // Hide node info.
        $('.node-info').remove();
        // Show nodes and edges.
        sigInst.iterEdges(function(e) {
          e.hidden = false;
        }).iterNodes(function(n) {
          n.hidden = false;
        }).draw();
      });

      // Bind pause.
      $('#sigma-pause').on('click', function() {
        if (isDrawing === true) {
          isDrawing = false;
          sigInst.stopForceAtlas2();
          $(this).html('Play');
        } else {
          isDrawing = true;
          sigInst.startForceAtlas2();
          $(this).html('Pause');
        }
      });

      // Activate the FishEye.
      // sigInst.activateFishEye().draw();

      // Start the ForceAtlas2 algorithm.
      sigInst.startForceAtlas2();
      isDrawing = true;
    },

    start: function() {
      var sigInst = sigma.instances[1];
      if (sigInst) {
        sigInst.startForceAtlas2();
      } else {
        Sigma.init();
      }
      isDrawing = true;
      $('#sigma-pause').html('Pause');
    },

    stop: function() {
      var sigInst = sigma.instances[1];
      if (sigInst) {
        sigInst.stopForceAtlas2();
        isDrawing = false;
        $('#sigma-pause').html('Play');
      }
    }

  };

  // Reveal module.
  window.sylv.Sigma = Sigma;

})(sylv, sigma, jQuery, window, document);
