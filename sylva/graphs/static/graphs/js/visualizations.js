// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var visualizations = {
    processing: function() {
      $('.pause').hide();
      $('#graph-container').hide().empty();
      $('#canvas-box').show();
      $('#element-info').html('Click any node to interact');
      $('.sigma-checkbox').hide();
      sylv.Processing.init();
    },
    sigma: function() {
      $('#canvas-box')
        .hide()
        .empty()
        .append('<canvas id="graphcanvas">Your browser does not support graph visualization</canvas>');
      $('#graph-container').show();
      $('#element-info').html('Click any node to interact');
      $('.pause').show();
      $('.sigma-checkbox').css('display', 'inline-block');
      sylv.Sigma.init();
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