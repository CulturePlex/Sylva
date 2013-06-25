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
    'graph-uploaded': 'Data uploaded.',
    'validation-error': 'Sorry, your data does not match your graph schema.',
    'loading-error': 'Sorry, your data can not be loaded.'
  };


  // Set user message.
  var setMessage = function(messageType) {
    return $('#loading-message')
             .text(gettext(helpTexts[messageType]))
             .fadeIn(FADING_DURATION / 4);
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
        return setMessage(messageType)
                 .delay(FADING_DURATION * 3)
                 .fadeOut(FADING_DURATION / 4)
                 .promise();
      },
      // fail filter
      function() {
        setMessage('loading-error');
      }
    );
  };


  // Show CSS animations and run validating and uploading steps.
  var runLastSteps = function(promise, $container) {
    var promiseContainer,
        promiseMessage,
        promiseSend,
        promiseFinish;

    promiseContainer = fadeoutContainer(promise, $container);

    promiseMessage = fadeinLoadedMessage(promiseContainer, 'file-loaded');

    promiseSend = promiseMessage.then(function() {
      if (validateData()) {
        $('#progress-bar')
          .attr('max', DI.edges.length + DI.nodesLength)
          .parent()
          .fadeIn(FADING_DURATION / 4);
        return sendData();
      } else {
        $('#progress-wrapper').hide();
        setMessage('validation-error');
        return $.Deferred().reject();
      }
    });

    promiseSend.progress(function() {
      var max, value, percentage;
      max = parseInt($('#progress-bar').attr('max'), 10);
      value = parseInt($('#progress-bar').attr('value'), 10);
      percentage = ((value / max) * 100).toFixed();
      $('#progress-bar').attr('value', value + 1);
      $('#percentage').text(percentage + '%');
    });

    promiseFinish = promiseSend.then(function() {
      var value = parseInt($('#progress-bar').attr('value'), 10);
      $('#progress-bar').attr('value', value + 2);
      $('#percentage').text('100%');
      return $('#progress-bar')
               .parent()
               .fadeOut(FADING_DURATION / 4)
               .promise();
    });

    promiseFinish.done(function() {
      setMessage('graph-uploaded');
    });
  };


  // Show CSS animations beetween CSV nodes and CSV edges loading steps.
  var runCSVSteps = function(promise, $container) {
    var promiseContainer,
        promiseMessage;

    promiseContainer = fadeoutContainer(promise, $container);

    promiseMessage = fadeinLoadedMessage(promiseContainer, 'csv-steps');

    promiseMessage.done(function() {
      $('#files-container2')
        .text(gettext(helpTexts['csv-edges']))
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
        runCSVSteps($.Deferred().resolve(), $('#files-container'));
      } else {
        runCSVSteps($.Deferred().reject(), $('#files-container'));
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