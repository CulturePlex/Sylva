(function ($) {
    var menuOpened = null;
    var accordionState = "disabled";

    // A function that opens a menu depending of the selector of the button.
    var openMenu = function(selector) {
      closeMenu();
      menuOpened = $(selector);

      var angle = menuOpened.siblings().children()[1];
      $(angle).removeClass('fa-angle-down');
      $(angle).addClass('fa-angle-up');

      menuOpened.show();
    };

    // A function that checks if a menu is opened and closes it.
    var closeMenu = function() {
      if (menuOpened != null) {
        var angle = menuOpened.siblings().children()[1];
        $(angle).removeClass('fa-angle-up');
        $(angle).addClass('fa-angle-down');

        menuOpened.hide();
        menuOpened = null;
      }
    };

  $('#builder-query').on('click', function() {
    $('#query-builder-results').hide();
    $('#query-builder-query').show();
    $('#results').hide();
  });

  $('#builder-results').on('click', function() {
    $('#query-builder-query').hide();
    $('#query-builder-results').show();
    $('#results').show();
  });

  $('#select-node-type').on("mouseover", function() {
      openMenu("#node-types");
  });

  $("#node-types").on("mouseleave", closeMenu);


  $('#clear-button').on('click', function() {
    jsPlumb.detachEveryConnection();
    $('#diagram').empty();
    // We remove the endpoints in the previous level (because JsPlumb update)
    elems = $('#diagramContainer').children();
    $.each(elems, function(index, elem) {
        var elemClass = $(elem).attr('class');
        if(elemClass != undefined) {
            var filter = new RegExp("_jsPlumb.");
            if(elemClass.match(filter)) {
              $(elem).remove();
            }
        }
    });
  });


  $('.accordion-save-query').accordion({
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
    activate: function(event) {
      if(accordionState == "disabled") {
        $('.content-divider').css({
          "display": ""
        });
        $('.content2-second').css({
          "float": "left",
          "width": "740px",
          "padding-left": "30px"
        });
        $('#diagramContainer').css({
          "margin-top": "32px"
        });
        accordionState = "enabled";
      } else if(accordionState == "enabled") {
        $('.content-divider').css({
          "display": "none"
        });
        $('.content2-second').css({
          "float": "none",
          "width": "1140px",
          "padding-left": "0px"
        });
        $('#diagramContainer').css({
          "margin-top": "0px"
        });
        accordionState = "disabled";
      }
    },
    active: false,
    heightStyle: 'content'
  });

})(jQuery);
