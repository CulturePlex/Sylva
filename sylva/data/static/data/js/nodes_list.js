var retrieveRelationships = function(url, elementId){
  $.ajax({
    url: url,
    success: function(data){
      var label;
      var relationships = JSON.parse(data);
      var divs = [];
      $.each(relationships, function(direction, rels){
        html = $('<div>');
        html.addClass('relationships-box');
        if (rels != false){
          html.append($('<span>').text(''));
        }
        $.each(rels, function(index, item){
          if (direction == "outgoing") {
            label = item.label + ' ' + item.node_display;
          } else {
            label = item.node_display + ' ' + item.label;
          }
          html.append($('<span>')
              .append(label))
              .append(' <br/> ');
        });
        divs.push(html);
      });
      $('#'+elementId).parent().next()
        .replaceWith(divs[1])
        .addClass('is-loaded');
      $('#'+elementId)
        .replaceWith(divs[0])
        .addClass('is-loaded');
    },
    error: function(error){
      console.log("ERROR: ", error);
    }
  });
};

// Bind events to data toggle controls to start the auto fetching of relationships
$('.data-preview-toggle').on('click', function(){
  $.each($('.retrieve-relationships'), function(index){
    var element = $(this);
    // Fetch elements that are not already loaded and are visible
    if (!element.hasClass('is-loaded') && element.closest('div').css('display') == "block") {
      element.click();
    }
  });
});
