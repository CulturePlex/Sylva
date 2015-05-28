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

        var onChoices = function(e) {
            var select = $(this),
                selectId = select.attr("id"),
                input = select.parent().siblings("td.choices").children("input[type='text']"),
                label = $("label[for='" + input.attr("id") + "']"),
                tagsInput = $("#" + input.attr("id") + "_tagsinput");
            if (select.val() === "c") {  // 'c' for Choices
                label.text(gettext("Values:"));
                if (tagsInput.length > 0) {
                    tagsInput.show();
                    tagsInput.importTags(input.val());
                    input.hide();
                } else {
                    input.tagsInput({
                        'height':'60px',
                        'width':'225px',
                        'interactive':true,
                        'defaultText': gettext('Add an option'),
                        'removeWithBackspace' : true,
                        'minChars' : 1,
                        'placeholderColor' : '#666666'
                    });
                }
            } else {
                label.text(gettext("Default value:"));
                tagsInput.hide();
                input.show();
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

        $("select[name$='datatype']").on("change", onChoices);
        $("select[name$='datatype']").change();
    });
})(jQuery);
