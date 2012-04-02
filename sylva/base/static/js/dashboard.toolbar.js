(function ($) {
    init = function() {
        $("#nodeTypeNavigation").change(function(e) {
            location.href = $(this).val();
            return false;
        });
    };
    $(document).ready(init);
})(jQuery);
//})(jQuery.noConflict());
