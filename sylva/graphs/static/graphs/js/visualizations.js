// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var visualizations = {
    processing: function() {
      $('#graph-container').hide();
      $('#canvas-box').show();
      sylv.Processing.init();
    },
    sigma: function() {
      $('#canvas-box').hide();
      $('#graph-container').empty().show();
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