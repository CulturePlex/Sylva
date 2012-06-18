// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true */

;(function(sylv, sigma, $, window, document, undefined) {

  var Sigma = {
    init: function() {
      // Instanciate Sigma.js and customize rendering
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

      // Parse a GEXF encoded file to fill the graph
      var graph_name = window.location.pathname.split('/')[2];
      var url = 'http://' + window.location.host + '/tools/' + graph_name + '/export/';
      sigInst.parseGexf(url);

      // Draw the graph
      sigInst.draw();
    }
  };

  // Reveal module
  window.sylv.Sigma = Sigma;

})(sylv, sigma, jQuery, window, document);
