// Foundation scripts.

// Function to calculate the best width to short the information
var calculateTextLength = function() {
  // We get the headers elements, but we remove the first (the element '#')
  var headers = $('th');
  // We need the minimun value for the limit of the shorter and the maximun
  // for the hover option
  var minimum = 1150; // The width of the table
  var maximum = 0;
  $.each(headers, function(index, elem) {
    // We check if the header is showed to take into account
    // when we hide some properties
    var isShowed = $(elem).css('display') != 'none';
    if(isShowed) {
      // We avoid the first element
      if (index != 0) {
        var elemWidth = $(elem).width();
        if(elemWidth < minimum) {
          minimum = elemWidth;
        }

        if(elemWidth > maximum) {
          maximum = elemWidth;
        }
      }
    }
  });

  // We change the values of shorten-text and shorten-text:hover
  $('.shorten-text').css({
    'max-width': minimum + 'px'
  });
  $('.shorten-text:hover').css({
    'max-width': maximum + 'px'
  });
};

/* The next two blocks add a 'in development' capability to the HTML Canvas
 * element: 'canvas.toBlob'.
 */

// From http://stackoverflow.com/a/16245768
window.base64ToBlob = function(b64Data, contentType, sliceSize) {
  contentType = contentType || '';
  sliceSize = sliceSize || 512;

  var byteCharacters = atob(b64Data);
  var byteArrays = [];

  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    var slice = byteCharacters.slice(offset, offset + sliceSize);

    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    var byteArray = new Uint8Array(byteNumbers);

    byteArrays.push(byteArray);
  }

  var blob = new Blob(byteArrays, {type: contentType});
  return blob;
};

if (!HTMLCanvasElement.prototype.toBlob) {
 Object.defineProperty(HTMLCanvasElement.prototype, 'toBlob', {
  value: function (callback, contentType, quality) {
    contentType = contentType || 'image/png';

    /*
    var base64Image = this.toDataURL(contentType, quality);
    base64Image = base64Image.split(',')[1];  // Removing 'data:image/png;base64,'
    var blob = base64ToBlob(base64Image, contentType);
    callback(blob);
    */

    // The previous comment in one line, for not creating garbage.
    callback(base64ToBlob(this.toDataURL(contentType, quality).split(',')[1], contentType));
  }
 });
}

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
    createCookieTour($);
  });


  // Nav menu buttons.
  function navMenu($) {
    // Var for control which menu is opened.
    var menuOpened = null;

    // Var for canceling de '(".no-menu").on("mouseover", ...' trigger.
    var timeoutId = null;

    $("#nodeTypeNavigation").change(function(e) {
      location.href = $(this).val();
      return false;
    });

    // A function that opens a menu depending of the selector of the button.
    var openMenu = function(selector) {
      closeMenu();
      menuOpened = $(selector);

      var angle = menuOpened.siblings().children().children();
      angle.removeClass('fa-angle-down');
      angle.addClass('fa-angle-up');

      menuOpened.show();
    };

    // A function that checks if a menu is opened and closes it.
    var closeMenu = function() {
      if (menuOpened != null) {
        var angle = menuOpened.siblings().children().children();
        angle.removeClass('fa-angle-up');
        angle.addClass('fa-angle-down');

        menuOpened.hide();
        menuOpened = null;
      }
    }

    // This always close the menu if the user exit the navigation bar.
    $("nav.menu").on("mouseleave", closeMenu);

    // This always close the menu if the user enter another button.
    $(".no-menu").on("mouseenter", function() {
      timeoutId = setTimeout(function() {
        closeMenu();
      }, 500);
    });

    $("#dataMenu").on("mouseenter", function() {
      openMenu("#dataBrowse");
    });

    /* This is a little trick to not close the dropdown if has been closed with
     * the '(".no-menu").on("mouseover", ...' trigger.
     */
    $("#dataBrowse").on("mouseenter", function() {
      clearTimeout(timeoutId);
      timeoutId = null;
    });

    $("#dataBrowse").on("mouseleave", closeMenu);

    $("#toolsMenu").on("mouseenter", function() {
      openMenu("#toolsBrowseId");
    });

    $("#toolsBrowseId").on("mouseleave", closeMenu);

    $(".dataOption.list").on("click", closeMenu);

    $(".dataOption.new").on("click", closeMenu);
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


  // Tour feature - declaration.
  function tour($) {
    if ($('#tour').length !== 0) {
      $('#toggleTour')
        .show()
        .on('click', activateTour);
      checkCookieTour();
    }
  }


  // Tour feature - activation.
  function activateTour() {
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
  }


  // Tour feature - cookie creation.
  function createCookieTour($) {
    if ($('title').text() == 'SylvaDB - Signup almost done!') {
      $.cookie.json = true;
      var tourIds = ['dashboard', 'nodes-editcreate', 'nodes-view', 'graphs-collaborators', 'graphs-create', 'graphs-view', 'schemas-edit', 'schemas-item-edit'];
      $.cookie('tour_ids', tourIds, { expires: 365, path: '/' });
    }
  }


  // Tour feature - cookie control.
  function checkCookieTour() {
    try {
      $.cookie.json = true;
      tourIds = $.cookie('tour_ids');
      if (typeof tourIds != 'undefined') {
        tourId = $('#tour').attr('data-tour-id');
        index = $.inArray(tourId, tourIds);
        if (index != -1) {
          tourIds.splice(index, 1);
          if (tourIds.length > 0) {
            $.cookie('tour_ids', tourIds, { expires: 365, path: '/' });
          } else {
            $.removeCookie('tour_ids', { path: '/' });
          }
          activateTour();
        }
      }
    } catch(e) {
      // Pass, this is because the reports in modals. They have them own
      // cookie variable.
    }
  }

  $(document).ready(function() {
    calculateTextLength();
  });

}(jQuery));
