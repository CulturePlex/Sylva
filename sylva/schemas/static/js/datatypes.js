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
        });
//        var type = $('<input type="date" />').attr('type');
//        if (type == 'text') { // No HTML5 support
//            var options = {
//                dateFormat: 'yy-mm-dd'
//            };
//            $('.date').datepicker(options);
//        } else {
//            $('.date').attr("type", "date");
//        };
    };
    $(document).ready(init);
})(jQuery);
