(function ($) {

  $('.body-inside').css({
    "width": "570px"
  });

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

  $('#select-node').on('mouseover', function() {
    $('#node-options').css({
      "display": "block"
    });
  });

  $('#select-node').on('mouseout', function() {
    $('#node-options').css({
      "display": "none"
    });
  });

  $('#clear-button').on('click', function() {
    jsPlumb.detachEveryConnection();
    $('#diagram').empty();
  });

})(jQuery);
