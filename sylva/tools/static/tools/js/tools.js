// jQuery stuff.

/* jshint strict: true, undef: true, unused: true, eqeqeq: true, maxlen: 80 */
/* global window, document, jQuery, console */

;(function($, window, document, undefined) {

  'use strict';


  // Sylva global namespace.
  var sylv = window.sylv || {};

  if (!sylv.DataImporter) {
    console.log("Error: Sylva DataImporter library not found.");
    return;
  }

  // Shortcut to data importer library.
  var DI = sylv.DataImporter;

  // Django i18n.
  var gettext = window.gettext || String;

  // Fading out/in duration.
  var FADING_DURATION = 1000;

  // The type of file currently selected: GEXF, CSV nodes, CSV edges, ...
  var currentFileType = '';

  // CSV nodes and edges FileLists.
  var CSVFileLists = {};

  // Drag and Drop help texts.
  var helpTexts = {
    'gexf': 'Drop your file here',
    'csv-nodes': 'Drop your nodes files here',
    'csv-edges': 'Now drop your edges files',
    'csv-steps': 'Nodes files loaded. Loading edges files...',
    'file-loaded': 'Data loaded. Uploading to the server...',
    'graph-uploaded': 'OK! Data uploaded.',
    'validation-error': 'Sorry, your data does not match your graph schema.',
    'loading-error': 'Sorry, your data can not be loaded.'
  };


  // Hide drag and drop container.
  var fadeoutContainer = function(promise, $container) {
    return promise.then(
      // done filter
      function() {
        return $container
                 .fadeOut(FADING_DURATION / 4)
                 .promise();
      },
      // fail filter
      function() {
        $container.hide();
        return promise;
      }
    );
  };


  // Show message when data is loaded into the browser.
  var fadeinLoadedMessage = function(promise, messageType) {
    return promise.then(
      // done filter
      function() {
        return $('#loading-message')
                 .text(gettext(helpTexts[messageType]))
                 .fadeIn(FADING_DURATION / 4)
                 .delay(FADING_DURATION * 3)
                 .fadeOut(FADING_DURATION / 4)
                 .promise();
      },
      // fail filter
      function() {
        $('#loading-message')
          .text(gettext(helpTexts['loading-error']))
          .fadeIn(FADING_DURATION / 2);
      }
    );
  };


  // Show CSS animations and run validating and uploading steps.
  var runLastSteps = function(promise, $container) {
    var promise1,
        promise2,
        promise3,
        promise4;

    promise1 = fadeoutContainer(promise, $container);

    promise2 = fadeinLoadedMessage(promise1, 'file-loaded');

    promise3 = promise2.then(function() {
      var sendPromise = $.Deferred();

      if (validateData()) {
        $('#progress-bar')
          .attr('max', DI.edges.length + DI.nodesLength)
          .fadeIn(FADING_DURATION / 4);
        // Finally, send graph data to the server.
        sendPromise = sendData();
      } else {
        $('#progress-bar').hide();
        $('#loading-message')
          .text(gettext(helpTexts['validation-error']))
          .fadeIn(FADING_DURATION / 4);
      }

      return sendPromise;
    });

    promise4 = promise3.then(function() {
      return $('#progress-bar')
               .fadeOut(FADING_DURATION / 4)
               .promise();
    });

    promise4.then(function() {
      $('#loading-message')
        .text(gettext(helpTexts['graph-uploaded']))
        .fadeIn(FADING_DURATION / 4);
    });
  };


  // Show CSS animations beetween CSV nodes and CSV edges loading steps.
  var finishCSVSteps = function(promise, $container) {
    var promise1,
        promise2;

    promise1 = fadeoutContainer(promise, $container);

    promise2 = fadeinLoadedMessage(promise1, 'csv-steps');

    promise2.done(function() {
      $('#files-container2')
        .text(gettext(helpTexts[currentFileType]))
        .fadeIn(FADING_DURATION / 4);
    });
  };


  // File handlers.
  var fileHandlers = {
    // Handle GEXF file.
    'gexf': function(files) {
      var promiseGEXF = DI.loadGEXF(files[0]);
      runLastSteps(promiseGEXF, $('#files-container'));
    },

    // Handle CSV nodes files.
    'csv-nodes': function(nodesFiles) {
      var isValid = true,
          file,
          i, li;

      for (i = 0, li = nodesFiles.length; i < li; i++) {
        file = nodesFiles[i];
        if (file.type !== 'text/csv') {
          isValid = false;
          break;
        }
      }

      if (isValid) {
        CSVFileLists['nodes'] = nodesFiles;
        currentFileType = 'csv-edges';
        finishCSVSteps($.Deferred().resolve(), $('#files-container'));
      } else {
        finishCSVSteps($.Deferred().reject(), $('#files-container'));
      }
    },

    // Handle CSV edges files.
    'csv-edges': function(edgesFiles) {
      var promiseCSV = DI.loadCSV(CSVFileLists.nodes, edgesFiles);
      runLastSteps(promiseCSV, $('#files-container2'));
    }
  };


  // Validate graph and print message.
  var validateData = function() {
    return DI.validateGraph(DI.nodes, DI.edges, DI.schemaNodes, DI.schemaEdges);
  };


  // Send data to the server.
  var sendData = function() {
    return DI.sendGraph(DI.nodes, DI.edges, sylv.nodesCreateURL,
                        sylv.edgesCreateURL);
  };


  // Dinamically call a file handler depending of the current file type.
  var loadFiles = function(files) {
    fileHandlers[currentFileType](files);
  };


  // Handle 'dragover' event.
  var handleDragOver = function(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.originalEvent.dataTransfer.dropEffect = 'copy';
  };


  // Handle 'dragenter' event.
  var handleDragEnter = function(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    $(this).addClass('dragenter');
  };


  // Handle 'dragleave' event.
  var handleDragLeave = function(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    $(this).removeClass('dragenter');
  };


  // Handle 'drop' event.
  var handleDrop = function(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    var files = evt.originalEvent.dataTransfer.files;
    loadFiles(files);

    // Disable radio buttons.
    $('.option input').attr('disabled', 'disabled');
  };


  // Handle radio inputs for file format selection.
  var handleRadioInputs = function(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    if (evt.target.value === 'gexf') {
      currentFileType = 'gexf';
      $('#files-container').text(gettext(helpTexts[currentFileType]));
    } else if (evt.target.value === 'csv') {
      currentFileType = 'csv-nodes';
      $('#files-container').text(gettext(helpTexts[currentFileType]));
    }

    $('#files-container').fadeIn(FADING_DURATION);
  };


  // DOM ready.
  $(function() {

    // Drag and drop events handlers.
    var eventsHandlers = {
      'dragover': handleDragOver,
      'dragenter': handleDragEnter,
      'dragleave': handleDragLeave,
      'drop': handleDrop
    };

    // Drag and Drop containers.
    $('#files-container').on(eventsHandlers);
    $('#files-container2').on(eventsHandlers);

    // Radio inputs for file type selection.
    $('.option').on('change', handleRadioInputs);
  });

}(jQuery, window, document));