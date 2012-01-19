GraphEditor.progressBar.hide = function() {
  $('#'+GraphEditor.progressBarId).hide();
  GraphEditor._stopRefreshing = false;
  $('body').trigger($.Event('endFirstStep'));
  GraphEditor.refresh();
}

var graphSchema;
//var sylvaSchema = {"nodeTypes":{"City":{},"Museum":{},"Artist":{},"Artwork":{}},"allowedEdges":{"City_located in_Museum":{"source":"City","label":"located in","target":"Museum"},"Artwork_kept in_Museum":{"source":"Artwork","label":"kept in","target":"Museum"},"Artwork_created by_Artist":{"source":"Artwork","label":"created by","target":"Artist"}}};

//var sylvaSchema = {"nodeTypes":{"City":{},"Artist":{},"Artwork":{}},"allowedEdges":{"City_located in_Museum":{"source":"City","label":"located in","target":"Museum"},"Artwork_kept in_Museum":{"source":"Artwork","label":"kept in","target":"Museum"},"Artwork_created by_Artist":{"source":"Artwork","label":"created by","target":"Artist"}}};

var Importer = {
  schemaIsCompatible: function(graphSchema, sylvaSchema){
    // Each nodetype in graphSchema exists in sylva schema
    var compatible = true;
    $.each(graphSchema.nodeTypes, function(index, value){
      if (!sylvaSchema.nodeTypes.hasOwnProperty(index)){
        Importer.error("Node", index);
        compatible = false;
        return false;
      }
    });
    if (!compatible){
      return false;
    }
    // Each allowedtype in graphSchema exists in graph schema
    $.each(graphSchema.allowedEdges, function(index, value){
      if (!sylvaSchema.allowedEdges.hasOwnProperty(index)){
        console.log(sylvaSchema.allowedEdges);
        console.log(index, " no esta");
        Importer.error("Edge", value);
        compatible = false;
        return false;
      }
      with (sylvaSchema.allowedEdges[index]){
        if (value.source != source || value.label != label || value.target != target){
          Importer.error("Edge", value);
          compatible = false;
          return false;
        }
      }
    });
    return compatible;
  },

  error: function(dataType, dataValue){
    dataValue = JSON.stringify(dataValue);
    var text = ("ERROR: " + dataType + " " + dataValue +
        " does not exist in your Sylva schema. " +
        "Please fix your schemas and try again");
    $('#second-step-info').text(text);
  },

  addNode: function(node){
    //TODO Node creation view
    console.log(node);
  }
};
