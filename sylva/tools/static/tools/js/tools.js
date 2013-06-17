// jQuery stuff.

/* jshint strict: true, undef: true, unused: true, eqeqeq: true, maxlen: 80 */
/* global jQuery, console */

;(function($, window, document, undefined) {

  'use strict';


  // Django i18n.
  var gettext = window.gettext || String;

  // Sylva global namespace.
  var sylv = window.sylv || {};

  if (!sylv.DataImporter) {
    console.log("Error: Sylva DataImporter library not found.");
    return;
  }

  // Shortcut to data importer library.
  var DI = sylv.DataImporter;


  // Validate graph and print message.
  var validateData = function() {
    var isValid = DI.validateGraph(DI.nodes, DI.edges, DI.schemaNodes,
                                   DI.schemaEdges);

    if (isValid) {
      console.log('Ok! Data is valid.');
    } else {
      console.log('Sorry, data is not valid.');
    }

    return isValid;
  };


  // Send data to the server.
  var sendData = function() {
    if (validateData()) {
      DI.sendGraph(DI.nodes, DI.edges, sylv.nodesCreateURL,sylv.edgesCreateURL);
    }
  };


  // Handle GEXF file input.
  var handleGEXF = function($gexf) {
    var promiseGEXF = DI.loadGEXF($gexf);

    promiseGEXF.done(function() {
      console.log('Ok! Gephi loaded.');
    });
  };


  // Handle CSV file inputs.
  var handleCSV = function($nodes, $edges) {
    var promiseCSV = DI.loadCSV($nodes, $edges);

    promiseCSV.done(function() {
      console.log('Ok! CSV loaded.');
    });
  };


  // DOM ready.
  $(function() {
    // handleGEXF();
    // handleCSV();
  });

}(jQuery, window, document));