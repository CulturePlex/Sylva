// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, alert:true */

/****************************************************************************
 * Visualizations
 ****************************************************************************/

;(function(sylva, $, window, document, undefined) {

  var visualizations = {

    sigma: function() {
      sylva.Sigma.start();
    },

    leaflet: function() {
      sylva.Leaflet.init();
    }

  };

  // Flag to control if we are inside the analytics view while we are loading
  // the graph.
  var isAnalyticsMode = false;

  // DOM
  $(function() {

    $('#graph-node-types').hide();
    $('#sigma-wrapper').css({
      'width': $('#body').width(),
      'margin-top': '0px'
    });

    var msg = '';
    if (sylva.jsValues.isSchemaEmpty) {
      msg += gettext("Your Schema is empty.");
      msg += '<br>';
      msg += gettext("You need to define a Schema before adding data to your graph.");
    } else if (sylva.jsValues.isGraphEmpty) {
      msg += gettext("Your graph is empty.");
      msg += '<br>';
      msg += gettext("You haven't added any data to your graph yet.");
    }

    if (msg !== '') {
      // TODO: The next lines are for checking the import tools without enter in the Analytics Mode.
      // sylva.modals.init();
      // $('a[data-modal="import-schema"]').on('click', sylva.Sigma.callImportSchemaModal);
      // $('a[data-modal="import-data"]').on('click', sylva.Sigma.callImportDataModal);

      $('#sigma-container').html('<div class="graph-empty-message">' + msg + '</div>');
    } else {
      var spinnerOpts = {
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
        left: '550'           // Left position relative to parent in px
      };
      var spinnerTarget = document.getElementById('spinner');
      var spinner = new Spinner(spinnerOpts).spin(spinnerTarget);

      $('#sigma-container').append('<div id="graph-loading" class="graph-loading-wrapper" style="opacity: 0.5;">' +
                                     '<div id="graph-loading-message" class="graph-loading-inner" style="top: 170px;">' +
                                      gettext('loading...') +
                                     '</div>' +
                                   '</div>');
      $('#graph-controls .right').css('display', 'inline-block');

      // Graph rendering

      var jqxhr = $.getJSON(sylva.urls.viewGraphAjax, function(data) {
        $('#graph-loading').remove();
        spinner.stop();

        // Full graph
        sylva.graph = data.graph;

        // Other data
        sylva.nodetypes = data.nodetypes;
        sylva.reltypes = data.reltypes;
        sylva.nodeIds = data.nodeIds;
        sylva.size = data.size;
        sylva.collapsibles = data.collapsibles;
        sylva.positions = data.positions;
        sylva.searchLoadingImage = data.searchLoadingImage;
        sylva.queries = data.queries;

        $('#graph-support').hide();
        $('#graph-node-types').show();
        $('#sigma-wrapper').removeAttr('style');
        visualizations.sigma();

        try {
          initAnalytics(jQuery);
        } catch (error) {
          console.log('Sylva: Analytics are disabled.');
        }

        $('.sigma-control').not('.analytics-mode').css('display', 'inline-block');
        $('#sigma-node-size').css('display', 'inline-block');
        $('#sigma-graph-layout').css('display', 'inline-block');
        $('#sigma-edge-shape').css('display', 'inline-block');

        if(isAnalyticsMode) {
          // We remove the style of the elements
          $(body).removeAttr("style");
          $('#body').removeAttr("style");
          $('#canvas-box').removeAttr("style");
          $('#canvas-container').removeAttr("style");
          $('#full-window-column').removeAttr("style");
          $('#graph-loading').removeAttr("style");
          $('#graph-support').removeAttr("style");
          $('header').removeAttr("style");
          $('#sigma-wrapper').removeAttr("style");
          $('.spinner').removeAttr("style");

          // Show some elements
          $('#graph-controls').show();
          $('#canvas-box').css({
            "display": "none"
          });

          $('#sigma-go-analytics').click();
        }
      });

      // Error handling.
      jqxhr.error(function() {
        $('#graph-loading').remove();
        spinner.stop();

        $('#sigma-wrapper').width($('#body').width());

        var msg = gettext("Oops! Something went wrong with the server. Please, reload the page.");
        $('#sigma-container').html('<div class="graph-empty-message">' + msg + '</div>');
      });

    }

    // Handler to allow navigate to the full screen mode while the graph is
    // loading
    $('#sigma-go-analytics').on('click', function() {
      // We only fire this event if the graph isn't loaded yet
      if (sylva.graph === undefined) {
        isAnalyticsMode = true;
        $('#id_analytics').val('true');

        $('#sigma-go-analytics').hide();
        $('#graph-node-info').hide();
        $('nav.main li').hide();
        $('header.global > h2').hide();
        $('div.graph-item').hide();
        $('div#footer').hide();

        $('div.inside.clearfix').append($('nav.menu'));

        // Let's start with the needed operations
        $('.analytics-mode').show();

        // Showing map button, it's a special case :(
        if (sylva.spatialEnabled) {
          $('#sigma-go-map').removeClass('zoom-bottom-hide');
          $('#sigma-go-map').addClass('zoom-bottom-show');
        }

        $('#sigma-go-fullscreen').hide();
        $('#graph-labels').hide();
        $('#graph-layout').hide();
        $('#graph-rel-types').hide();
        $('#graph-controls').hide();
        $('#full-window-column').hide();

        $('html').css({
          "overflow-y": "hidden"
        });

        var width = document.documentElement.clientWidth;

        var fullWindowColumnWidth = width * 0.2;
        var borderWidth = fullWindowColumnWidth * 0.012;
        var canvasBoxWidth = width - fullWindowColumnWidth;

        // Collapsible settings for the analytics side
        $('.analytics-measure').accordion({
          collapsible: true,
          create: function(event, ui) {
            var box = $(event.target);
            var children = box.children();
            var header =  children.first();
            var body = $(children[1]);
            var span = header.children().first();

            // The next lines remove jQueryUI style from the boxes.
            box.removeClass('ui-widget ui-accordion');
            header.removeClass('ui-accordion-icons ' +
              'ui-accordion-header ui-helper-reset ui-state-default');
            body.removeClass('ui-accordion-content ui-widget-content');
            body.css('height', '');
            span.remove();
          },
          active: false,
          heightStyle: 'content'
        });

        /* Styles */

        $(body).css({
          "height": $(window).height(),
          "padding-top": "0px"
        });

        $('#body').css({
          'padding': 0,
          'width': $('#main').width()
        });

        $('#canvas-box').css({
          "width": canvasBoxWidth,
          "display": "inline"
        });

        $('#canvas-container').css({
          "width": canvasBoxWidth,
          "display": "inline"
        });

        $('#full-window-column').css({
          "display": "",
          "float": "right",
          "width": fullWindowColumnWidth,
          "height": $(body).height(),
          "pointer-events": "none",
          "opacity": "0.5",
          "background": "#CCC",
          "overflow-y": "hidden"
        });

        $('#graph-loading').css({
          "height": $(body).height(),
          "width": canvasBoxWidth,
          "margin-left": 0
        });

        $('#graph-support').css({
          "position": "fixed"
        });

        $('header').css({
          "padding-top": "0px",
          "padding-bottom": "1px"
        });

        $('.inside.clearfix').css({
          "width": $('#main').width()
        });

        $('.menu').css({
          "margin-top": "-31px"
        });

        $('#sigma-wrapper').css({
          "width": canvasBoxWidth,
          "margin-top": "0px",
          "float": "left"
        });

        $('.spinner').css({
          "left": "515px"
        });
      }

    });

    // Handler to allow navigate from the full screen mode while the graph is
    // loading
    $('#sigma-exit-analytics').on('click', function() {
      // We only fire this event if the graph isn't loaded yet
      if (sylva.graph === undefined) {
        isAnalyticsMode = false;
        $('#id_analytics').val('');

        // Let's start with the needed operations
        $('.analytics-mode').hide();

        // Hiding map buttons, it's a special case :(
        if (sylva.spatialEnabled) {
          $('#sigma-go-map').removeClass('zoom-bottom-show');
          $('#sigma-go-map').addClass('zoom-bottom-hide');
        }

        $('#sigma-go-analytics').show();
        $('#graph-node-info').show();
        $('nav.main li').show();
        $('header.global > h2').show();
        $('div.graph-item').show();
        $('div#footer').show();
        $('#graph-controls').show();

        $('header').prepend($('nav.menu'));

        /* Styles */

        $('html').removeAttr("style");
        $(body).removeAttr("style");
        $('#body').removeAttr("style");
        $('#canvas-box').removeAttr("style");
        $('#canvas-container').removeAttr("style");
        $('#full-window-column').removeAttr("style");
        $('#graph-loading').removeAttr("style");
        $('#graph-support').removeAttr("style");
        $('header').removeAttr("style");
        $('#sigma-wrapper').removeAttr("style");
        $('.spinner').removeAttr("style");
        $('.inside.clearfix').removeAttr("style");

        $('.menu').css({
          "margin-top": "0px"
        });

        $('#full-window-column').css({
          "display": "none"
        });

        $('#graph-loading').css({
          "height": "320px",
          "opacity": "0.5"
        });

        $('#sigma-wrapper').css({
          "width": "1150px",
          "margin-top": "0px"
        })

        $('.spinner').css({
          "position": "relative",
          "width": "0px",
          "z-index": "2000000000",
          "left": "580px",
          "top": "135px"
        });
      }

    });

    // This function is to fix all the elements in the dashboard screen
    $(document).ready(function(){
      $('.graph-item').css({
        'margin-top': '40px'
      });
    });
  });
})(sylva, jQuery, window, document);
