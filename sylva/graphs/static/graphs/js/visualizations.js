// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true, sylv:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function($, window, document, undefined) {

    var visualizations = {
        'processing': function() {
            sylv.Processing.init();
        },
        'sigma': function() {
            console.log('sigma');
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

})(jQuery, window, document);