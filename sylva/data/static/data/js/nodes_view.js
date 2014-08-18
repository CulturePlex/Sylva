(function($) {
  $(function() {
    $('#h2-relationships').on('change', function() {
      var option = $(this).val();
      if (option === 'all') {
        $('.all').show();
      } else if (option === 'incoming') {
        $('.outgoing').hide();
        $('.incoming').show();
      } else if (option === 'outgoing') {
        $('.incoming').hide();
        $('.outgoing').show();
      } else {
        $('.all').hide();
        $('#' + option).show();
      }
    });

    $('.relationship').on('click', function() {
      if ($(this).find('dl').html().trim() !== '') {
        $(this).find('.rel-properties').toggle();
      }
    });
  });
})(jQuery);
