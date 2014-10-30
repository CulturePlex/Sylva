(function ($) {
    var menuOpened = null;

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

    $('#save-button').on('click', function() {
      cssDisplayValue = $('#div-save-query').css('display');
      if(cssDisplayValue == "none") {
        $('.content-divider').css({
          "display": ""
        });
        $('.content2-second').css({
          "float": "left",
          "width": "740px",
          "padding-left": "30px"
        });
      } else {
        $('.content-divider').css({
          "display": "none"
        });
        $('.content2-second').css({
          "float": "none",
          "width": "1140px",
          "padding-left": "0px"
        });
      }
      $('#div-save-query').toggle();
    });

    $('#run-query').ready(function() {
      $runQuery = $('#run-query');
      $runQuery.prop('disabled', true);
      $runQuery.css({
        'color': '#9b9b9b',
        'background-color': '#f2f2f2'
      });
    });

})(jQuery);
