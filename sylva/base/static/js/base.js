// Foundation scripts.

;(function($) {

  // CSRF protection for all AJAX requests.
  $.ajaxSetup({
    crossDomain: false,  // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {

      var getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };

      var csrfSafeMethod = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      };

      if (!csrfSafeMethod(settings.type)) {
        var csrftoken = getCookie('csrftoken');
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });


  // DOM ready handlers.
  $(function() {
    navMenu($);
    notifications($);
    tour($);
  });


  // Nav menu buttons.
  function navMenu($) {
    $("#nodeTypeNavigation").change(function(e) {
      location.href = $(this).val();
      return false;
    });

    $("#dataMenu").on("mouseenter", function(e) {
      $("#dataBrowse").show();
    });

    $("#dataBrowse").on("mouseleave", function(e) {
      $(this).hide();
    });

    $("#toolsMenu").on("mouseenter", function(e) {
      $("#toolsBrowseId").show();
    });

    $("#toolsBrowseId").on("mouseleave", function(e) {
      $(this).hide();
    });
  }


  // User notifications.
  function notifications($) {
    setTimeout(function() {
      $('header .success')
        .first()
        .parent()
        .fadeOut(1000, function() {
          $(this).remove();
        });
    }, 5000);
  }


  // Tour feature.
  function tour($) {
    if ($('#tour').length !== 0) {
      $('#toggleTour')
        .show()
        .on('click', function() {
          var $el = $(this);

          var deactive = function() {
            $el.removeClass('active');
          };

          if ($el.hasClass('active')) {
            deactive();
            $('.joyride-close-tip').click();
          } else {
            $el.addClass('active');
            $('#tour').joyride({
              postRideCallback: deactive
            });
          }
        });
    }
  }

}(jQuery));