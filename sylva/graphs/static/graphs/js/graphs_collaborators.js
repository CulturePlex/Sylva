function setPermission(userID, objectStr, permissionStr) {
  $.ajax({url: sylva.urls.changePermission,
    data: {
      user_id: userID,
      object_str: objectStr,
      permission_str: permissionStr
    },
    error: function(error) {
      if (error["responseText"] == "owner") {
        var control = document.getElementById("chk_" + objectStr + "_" + permissionStr);
        control.checked = true;
      }
    },
  });
}

(function ($) {
  init = function() {
    $('.chzn-select').ajaxChosen(
      {
        type: 'GET',
        url: sylva.urls.graphAjaxCollaborators,
        dataType: 'json'
      },
      function (data) {
        var results = {};
        $.each(data, function (i, val) {
          results[i] = val;
        });
        return results;
      },
      {
        no_results_text: gettext("No results matched")
      }
    );
  };

  $(document).ready(init);
})(jQuery);
