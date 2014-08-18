(function($) {
$(function() {
  $('input[type=submit]').on('click', function(e) {
    $(this).val('{% trans "Unsubscribing..." %}');
  });
});
}(jQuery));
