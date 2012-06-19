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



      // Draw the graph
      sigInst.draw();
    }
  };

  // Reveal module
  window.sylv.Sigma = Sigma;

})(sylv, sigma, jQuery, window, document);
