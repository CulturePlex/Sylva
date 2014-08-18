(function ($) {
  var init = function () {
    $("#id_query").keypress(function (e) {
      var query = $(this).val();
      if (e.which == 13) {
        $("#results").html("<span class='help'>" + gettext("Loading") + "...</span>");
        console.log(query);
        $.ajax({
          type: "POST",
          url: sylva.urls.operatorQueryResults,
          data: {"query": query},
          success: function (data) {
            $("#results").html("");
            for (var i = 0, j = data.length; i < j; i += 1) {
              var row = $("<div>");
              for (var k = 0, l = data[i].length; k < l; k += 1) {
                var cell = $("<span>");
                cell.text(data[i][k]);
                row.append(cell);
              }
              $("#results").append(row);
            }
          },
          error: function (e) {
            $("#results").html(gettext("No results found"));
          },
          dataType: "json"
        });
      }
    });
  }
  $(document).ready(init);
})(jQuery);
