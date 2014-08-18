(function($) {
  $(function() {
    $('.collapse').on({
      show: function() {
        var $prev = $(this).prev();
        $prev.find('.fa-chevron-down').hide();
        $prev.find('.fa-chevron-up').show();
      },
      hide: function() {
        var $prev = $(this).prev();
        $prev.find('.fa-chevron-down').show();
        $prev.find('.fa-chevron-up').hide();
      }
    });
  });
}(jQuery));
