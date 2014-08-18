var toggleColumn = function(selectId) {
  var value = $('#' + selectId).val();
  var columnClass = selectId.replace('toggle_', '') + '_' + value;
  $('.' + columnClass).toggle();
  $('#' + selectId).val(0);
};
