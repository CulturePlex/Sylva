// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true,
clearTimeout */


/****************************************************************************
 * Sigma.js visualization
 ****************************************************************************/

;(function(sylv, sigma, $, window, document, undefined) {

  // Layout algorithm state.
  var isDrawing = false;
  // setTimeout id.
  var timeout_id = 0;


  var Sigma = {

    init: function() {
      var that = this;
      // Nodes and edges.
      var sylv_nodes = sylv.total_nodes;
      var sylv_edges = sylv.total_edges;
      // Node info.
      var $tooltip;
      // Graph size.
      var size = sylv.size;

      // Instanciate Sigma.js and customize rendering.
      var sigInst = sigma.init(document.getElementById('sigma-container')).drawingProperties({
        defaultLabelColor: '#000',
        defaultLabelSize: 14,
        defaultLabelBGColor: '#fff',
        defaultLabelHoverColor: '#000',
        labelThreshold: 15,
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
          // Show node info popup.
          sigInst.iterNodes(function(node) {
            $tooltip =
              $('<div class="node-info"></div>')
                .append('<ul>' + attributesToString(sylv_nodes[nodePK]) + '</ul>')
                .css({
                  'left': node.displayX+212,
                  'top': node.displayY+61
                });
            $('#sigma-container').append($tooltip);
          }, [nodePK]);
        }

        var showRelatedNodes = $('#sigma-related-nodes').prop('checked');
        if (showRelatedNodes) {
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
          // Draw graph.
          sigInst.draw();
        }

        // Update node legend.
        sylv.Utils.updateNodeLegend(sylv_nodes[nodePK].id, nodePK, 'element-info');

      });

      // Hide node info popup and show the rest of nodes and edges.
      sigInst.bind('outnodes', function(event) {
        // Hide node info.
        $('.node-info').remove();
        var showRelatedNodes = $('#sigma-related-nodes').prop('checked');
        if (showRelatedNodes) {
          // Show nodes and edges.
          sigInst.iterEdges(function(e) {
            e.hidden = false;
          }).iterNodes(function(n) {
            n.hidden = false;
          }).draw();
        }
      });

      // Bind pause button.
      $('#sigma-pause').on('click', function() {
        if (isDrawing === true) {
          that.stop();
        } else {
          that.start();
        }
      });

      // Bind FishEye checkbox.
      $('#sigma-fisheye').on('change', function() {
        var fisheye = $(this).prop('checked');
        if (fisheye) {
        sigInst.activateFishEye().draw();
        } else {
        sigInst.desactivateFishEye().draw();
        }
      });

      $('#sigma-export-image').on('mouseover', function() {
        that.stop();
      });

      // Save as a PNG image.
      $('#sigma-export-image').on('click', function() {
        var $canvas = $('<canvas id="sigma_export_image">');
        var width = $('#sigma-container').children().first().width();
        var height = $('#sigma-container').children().first().height();
        $canvas.attr('width', width);
        $canvas.attr('height', height);
        $('#sigma-container').append($canvas);
        var canvas = $canvas[0];
        var ctx = canvas.getContext('2d');
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage(document.getElementById('sigma_nodes_1'), 0, 0);
        ctx.drawImage(document.getElementById('sigma_edges_1'), 0, 0);
        var img_data = canvas.toDataURL('image/png');
        $(this).attr('href', img_data.replace('image/png', 'image/octet-stream'));
        $canvas.remove();
      });

      sigInst.startForceAtlas2();
      isDrawing = true;

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
      that.addTimeout(timeout);
    },

    // Start layout algorithm.
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

    // Stop layout algorithm.
    stop: function() {
      this.removeTimeout();
      var sigInst = sigma.instances[1];
      if (sigInst) {
        sigInst.stopForceAtlas2();
        isDrawing = false;
        $('#sigma-pause').html('Play');
      }
    },

    // Stop layout algorithm after `timeout` ms.
    addTimeout: function(timeout) {
      var that = this;
      timeout_id = setTimeout(function() {
        that.stop();
      }, timeout);
    },

    // Clear setTimeout.
    removeTimeout: function() {
      clearTimeout(timeout_id);
    }

  };

  // Reveal module.
  window.sylv.Sigma = Sigma;

})(sylv, sigma, jQuery, window, document);
