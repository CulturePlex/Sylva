(function ($) {
    init = function() {
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
        $(document).on("click", function(event){
            var target = $(event.target);
            if (target.parents("#dataBrowse").length === 0) {
                $("#dataBrowse").hide();
            }
        });
    };
    $(document).ready(init);
})(jQuery);
