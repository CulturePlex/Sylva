// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true */


/****************************************************************************
 * Sigma.js visualizations
 ****************************************************************************/

;(function(sylv, sigma, $, window, document, undefined) {

  var Sigma = {
    init: function() {
      // Instanciate Sigma.js and customize rendering.
      var sigInst = sigma.init(document.getElementById('graph-container')).drawingProperties({
        defaultLabelColor: '#fff',
        defaultLabelSize: 14,
        defaultLabelBGColor: '#fff',
        defaultLabelHoverColor: '#000',
        labelThreshold: 6,
        defaultEdgeType: 'curve'
      }).graphProperties({
        minNodeSize: 0.5,
        maxNodeSize: 5,
        minEdgeSize: 1,
        maxEdgeSize: 1
      }).mouseProperties({
        maxRatio: 32
      });

      // Parse nodes and edges.
      var nodes = JSON.parse(JSON.stringify(sylv.nodes));
      var edges = JSON.parse(JSON.stringify(sylv.edges));

      // Add nodes.
      for (var k in nodes) {
        sigInst.addNode(k, {
          x: Math.random(),
          y: Math.random(),
          color: sylv.colors[nodes[k].type]
        });
      }

      // Add edges.
      for (var v in edges) {
        sigInst.addEdge(edges[v].id, edges[v].source, edges[v].target);
      }

      // Hide nodes and edges.
      sigInst.bind('overnodes', function(event) {
        var nodes = event.content;
        var neighbors = {};
        var isOrphan = true;
        sigInst.iterEdges(function(e) {
          if (nodes.indexOf(e.source) >= 0 || nodes.indexOf(e.target) >= 0) {
            neighbors[e.source] = true;
            neighbors[e.target] = true;
            isOrphan = false;
          }
        });
        if (isOrphan) {
          neighbors[nodes[0]] = true;
        }
        sigInst.iterNodes(function(n) {
          if (!neighbors[n.id]) {
            n.hidden = true;
          }
        });
        sigInst.draw();
      });

      // Show nodes and edges.
      sigInst.bind('outnodes', function(event) {
        sigInst.iterEdges(function(e) {
          e.hidden = false;
        }).iterNodes(function(n) {
          n.hidden = false;
        }).draw();
      });

      // Bind pause.
      var running = true;
      $('#sigma-pause').on('click', function() {
        if (running === true) {
          running = false;
          sigInst.stopForceAtlas2();
        } else {
          running = true;
          sigInst.startForceAtlas2();
        }
      });

      // Activate the FishEye.
      // sigInst.activateFishEye().draw();

      // Start the ForceAtlas2 algorithm.
      sigInst.startForceAtlas2();

    }
  };

  // Reveal module
  window.sylv.Sigma = Sigma;

})(sylv, sigma, jQuery, window, document);
