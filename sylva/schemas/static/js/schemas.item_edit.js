;(function($) {

    "use strict";

    $(function() {

        $("#itemType table.itemtype-properties-table tbody.dynamic").append($("#advancedMode"));

        var showAdvancedMode = function($elements) {
            $elements.show();
            $(".itemtype-properties-table textarea").addClass("expand");
        };

        var hideAdvancedMode = function($elements) {
            $elements.hide();
            $(".itemtype-properties-table textarea").removeClass("expand");
        };

        var rowAdded = function(row) {
            var $hiddens = $(".formset .hidden");
            if ($hiddens.is(":visible")) {
                showAdvancedMode($hiddens);
            }
        };

        $("#itemType tbody tr.formset").formset({
            prefix: "properties",
            addCssClass: "addButton",
            addText: gettext("Add Property"),
            deleteText: gettext("Remove"),
            extraClasses: ["row1", "row2"],
            added: rowAdded
        });

        $("#advancedModeButton").click(function() {
            var $hiddens = $(".formset .hidden");

            if ($hiddens.is(":visible")) {
                hideAdvancedMode($hiddens);
                $(this).html(gettext("Advanced Mode"));
            } else {
                showAdvancedMode($hiddens);
                $(this).html(gettext("Regular Mode"));
            }
        });
    });
})(jQuery);
