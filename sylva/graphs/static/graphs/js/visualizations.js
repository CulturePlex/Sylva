// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var visualizations = {

    processing: function() {
      sylv.Sigma.stop();
      $('#graph-container').hide();
      $('.sigma-checkbox').hide();
      $('.pause').hide();
      $('#canvas-box').show();
      $('#element-info').html('Click any node to interact');
      sylv.Processing.start();
    },

    sigma: function() {
      sylv.Processing.stop();
      $('#canvas-box')
        .hide()
        .append('<canvas id="graphcanvas">Your browser does not support graph visualization</canvas>');
      $('#graph-container').show();
      $('.pause').show();
      $('#element-info').html('Click any node to interact');
      $('.sigma-checkbox').css('display', 'inline-block');
      sylv.Sigma.start();
    }

  };

  // DOM
  $(function() {

    var opts = {
      lines: 15,            // The number of lines to draw
      length: 14,           // The length of each line
      width: 5,             // The line thickness
      radius: 11,           // The radius of the inner circle
      corners: 1,           // Corner roundness (0..1)
      rotate: 0,            // The rotation offset
      color: '#000',        // #rgb or #rrggbb
      speed: 1,             // Rounds per second
      trail: 60,            // Afterglow percentage
      shadow: false,         // Whether to render a shadow
      hwaccel: false,       // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9,          // The z-index (defaults to 2000000000)
      top: '105',           // Top position relative to parent in px
      left: '637'           // Left position relative to parent in px
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);

    $('#graph-container').append('<div id="graph-loading" class="graph-loading-wrapper" style="opacity: 0.5;">' +
                                   '<div id="graph-loading-message" class="graph-loading-inner" style="top: 170px;">' +
                                    gettext('loading...') +
                                   '</div>' +
                                 '</div>');

    // Graph rendering
    var jqxhr = $.getJSON(sylv.ajax_url, function(data) {
      $('#graph-loading').remove();
      spinner.stop();

      // partial graph (Processing.js)
      sylv.nodes = data.nodes;
      sylv.edges = data.edges;

      // full graph (Sigma.js and others)
      sylv.total_nodes = data.total_nodes;
      sylv.total_edges = data.total_edges;

      sylv.size = data.size;
      sylv.disableProcessing = data.size > sylv.MAX_SIZE;

      if (sylv.disableProcessing) {
        $('#visualization-processing').remove();
        sylv.Processing.init();
        $('#graphcanvas').on('graph_init', function(e) {
          e.stopPropagation();
          visualizations.sigma();
        });
      } else {
        visualizations.processing();
      }

    });
    // Error handling.
    jqxhr.error(function() {
      alert(gettext("Oops! Something went wrong with the server. Please, reload the page."));
    });

    // Select box bindings
    var $visualization_select = $('#visualization-type');
    $visualization_select.children().first().attr('selected', 'selected');
    $visualization_select.change(function() {
      var type = $(this).find('option:selected').data('type');
      visualizations[type]();
    });
  });
})(sylv, jQuery, window, document);