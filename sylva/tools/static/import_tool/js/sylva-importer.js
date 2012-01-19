GraphEditor.progressBar.hide = function() {
  $('#'+GraphEditor.progressBarId).hide();
  GraphEditor._stopRefreshing = false;
  $('body').trigger($.Event('endFirstStep'));
  GraphEditor.refresh();
}

var graphSchema;

var Importer = {
  counter: 0,
  addNodeURL: undefined,

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

  addNode: function(nodeName, nodeData){
    var nodeType = nodeData.type;
    delete nodeData.position;
    delete nodeData.type;
    nodeData.nameLabel = nodeName;
    var properties = JSON.stringify(nodeData);

    $.ajax({
      url: Importer.addNodeURL,
      data: {
        type: nodeType,
        properties: properties
      },
      success: function(){
        Importer.counter++;
        $('#import-progress-text').text('Node ' + nodeName + ' added');
        $('#import-progress-bar').attr('value', Importer.counter);
      },
    });
  }
};
