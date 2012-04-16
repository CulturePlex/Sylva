(function ($) {
    init = function() {
        $("#nodeTypeNavigation").change(function(e) {
            location.href = $(this).val();
            return false;
        });
        $("#dataMenu").on("mouseover", function(e) {
            $("#dataBrowse").show();
        });
        $(document).on("click", function(event){
            var target = $(event.target);
            if (target.parents("#dataBrowse").length == 0) {
                $("#dataBrowse").hide();
            }
        });
    };
    $(document).ready(init);
})(jQuery);
//})(jQuery.noConflict());
