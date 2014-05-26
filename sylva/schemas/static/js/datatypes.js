(function($) {
    init = function() {
        var options = {
            appendText: "(yyyy-mm-dd)",
            gotoCurrent: true,
            dateFormat: 'yy-mm-dd',
            changeYear: true,
            yearRange: "-3000:3000"
        };
        $('.date').datepicker(options);
        $('.time').timepicker({
            timeOnly: true,
            showSecond: true,
            timeFormat: 'HH:mm:ss',
            appendText: "(HH:mm:ss)",
        });
    };
    $(document).ready(init);
})(jQuery);
