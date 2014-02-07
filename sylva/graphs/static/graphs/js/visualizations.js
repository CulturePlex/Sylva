// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylva, $, window, document, undefined) {

  var visualizations = {

    sigma: function() {
      $('#sigma-wrapper').show();
      $('.pause').show();
      $('#element-info').html('Click any node to interact');
      $('.sigma-checkbox').css('display', 'inline-block');
      sylva.Sigma.start();
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

    $('#sigma-container').append('<div id="graph-loading" class="graph-loading-wrapper" style="opacity: 0.5;">' +
                                   '<div id="graph-loading-message" class="graph-loading-inner" style="top: 170px;">' +
                                    gettext('loading...') +
                                   '</div>' +
                                 '</div>');

    // Graph rendering
    var jqxhr = $.getJSON(sylva.view_graph_ajax_url, function(data) {
      $('#graph-loading').remove();
      spinner.stop();

      // full graph (Sigma.js and others)
      sylva.nodes = data.nodes;
      sylva.edges = data.edges;

      sylva.nodetypes = data.nodetypes;
      sylva.size = data.size;

      visualizations.sigma();

      var msg = '';
      if (sylva.is_schema_empty) {
        msg += gettext("Your Schema is empty.");
        msg += '<br>';
        msg += gettext("You need to define a Schema before adding data to your graph.");
      } else if (sylva.is_graph_empty) {
        msg += gettext("Your graph is empty.");
        msg += '<br>';
        msg += gettext("You haven't added any data to your graph yet.");
      }

      if (msg !== '') {
        $('#graphcanvas').hide();
        $('#sigma-wrapper').show();
        $('#sigma-container').html('<div class="graph-empty-message">' + msg + '</div>');
      }

    });

    // Error handling.
    jqxhr.error(function() {
      alert(gettext("Oops! Something went wrong with the server. Please, reload the page."));
    });

  });
})(sylva, jQuery, window, document);
