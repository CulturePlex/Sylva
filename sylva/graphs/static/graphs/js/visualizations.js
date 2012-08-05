// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var visualizations = {
    processing: function() {
      if (sylv.Sigma.exists()) {
        sylv.Sigma.stop();
      }
      $('#graph-container').hide();
      $('.sigma-checkbox').hide();
      $('.pause').hide();
      $('#canvas-box').show();
      $('#element-info').html('Click any node to interact');

      sylv.Processing.init();
    },
    sigma: function() {
      $('#canvas-box')
        .hide()
        .empty()
        .append('<canvas id="graphcanvas">Your browser does not support graph visualization</canvas>');
      $('#graph-container').show();
      $('.pause').show();
      $('#element-info').html('Click any node to interact');
      $('.sigma-checkbox').css('display', 'inline-block');

      if (sylv.Sigma.exists()) {
        sylv.Sigma.start();
      } else {
        sylv.Sigma.init();
      }
    }
  };

  // DOM
  $(function() {
    // run Processing as default
    visualizations.processing();

    $('#visualization-type').change(function() {
      var type = $(this).find('option:selected').data('type');
      visualizations[type]();
    });

  });

})(sylv, jQuery, window, document);