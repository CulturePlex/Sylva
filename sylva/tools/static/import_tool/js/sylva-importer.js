GraphEditor.progressBar.hide = function() {
  $('#'+GraphEditor.progressBarId).hide();
  GraphEditor._stopRefreshing = false;
  $('body').trigger($.Event('fileLoaded'));
  GraphEditor.refresh();
}

var Importer = {
  counter: 0,
  addNodeURL: undefined,
  addRelationshipURL: undefined,

  nodes: undefined,
  edges: undefined,
  progressBarId: undefined,
  progressTextId: undefined,

  graphSchema: undefined,
  matching: {},

  schemaIsCompatible: function(sylvaSchema){
    // Each nodetype in graphSchema exists in sylva schema
    var compatible = true;
    $.each(Importer.graphSchema.nodeTypes, function(index, value){
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
    $.each(Importer.graphSchema.allowedEdges, function(index, value){
      if (!sylvaSchema.allowedEdges.hasOwnProperty(index)){
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
    var nodeType = Importer.matching.nodeTypes[nodeData.type];
    var properties = {};
    $.each(Importer.matching.nodeAttributes[nodeType], function(index, value){
      if (value === '_nameLabel'){
        properties[index] = nodeName;
      } else {
        properties[index] = nodeData[value];
      }
    });
    var nodeKey = nodeName + '_' + nodeType;

    $.ajax({
      url: Importer.addNodeURL,
      data: {
        type: nodeType,
        properties: JSON.stringify(properties)
      },
      success: function(response){
        response = JSON.parse(response);
        Importer.counter++;
        $(Importer.progressTextId).text('Node ' + nodeName + ' added');
        $(Importer.progressBarId).attr('value', Importer.counter);
        nodeData._id = response.id;
        
        // If all the nodes are inserted then we can start with the edges
        if (Importer.counter == Object.keys(Importer.nodes).length){
          $('body').trigger($.Event('endNodeInsertion'));
        }
      },
    });
  },

  addEdge: function(sourceName, edgeLabel, targetName){
    $.ajax({
      url: Importer.addRelationshipURL,
      data: {
        type: Importer.matching.edgeTypes[edgeLabel],
        sourceId: Importer.nodes[sourceName]._id,
        targetId: Importer.nodes[targetName]._id
      },
      success: function(response){
        response = JSON.parse(response);
        Importer.counter++;
        var relationshipText = GraphEditor.edgeText(sourceName, edgeLabel, targetName);
        $(Importer.progressTextId).text('Relationship ' + relationshipText + ' created.');
        $(Importer.progressBarId).attr('value', Importer.counter);
        if (Importer.counterMax === Importer.counter){
          $('body').trigger($.Event('importFinished'));
        }
      }
    });
  },

  addData: function(_nodes, _edges, _progressBarId, _progressTextId){
    Importer.nodes = _nodes;
    Importer.edges = _edges;
    Importer.progressBarId = _progressBarId;
    Importer.progressTextId = _progressTextId;
    
    // Progress bar initialization
    Importer.counterMax = Object.keys(Importer.nodes).length + Importer.edges.length;
    $(Importer.progressBarId).attr('max', Importer.counterMax);
        ;

    // Nodes import
    $.each(Importer.nodes, function(index, value){
      Importer.addNode(index, value);
    });

    // Edges import when nodes are done
    $('body').bind('endNodeInsertion', function() {
      $.each(Importer.edges, function(index, value){
        Importer.addEdge(value.source, value.type, value.target);
      });
    });
    
    // Final message
    $('body').bind('importFinished', function(){
      $(Importer.progressTextId).text("Import process finished. Added " +
            Importer.counter + " elements.");
    });
  },

  validateNodes: function(importController){
    
    Importer.matching.nodeAttributeWidgets = {};
    
    importController.empty();
    var nodeAttributes;
    var nodeMatcher = $('<select>').append($('<option>'));
    $.each(Importer.graphSchema.nodeTypes, function(item, value){
      nodeMatcher
        .append($('<option>')
          .attr('value', item)
            .append(item));
      nodeAttributes = $('<select>').append($('<option>'));
      $.each(value, function(attribute){
        nodeAttributes
          .append($('<option>')
            .attr('value', attribute)
              .append(attribute));
      });
      
      // Store nodeType attributes selectors
      Importer.matching.nodeAttributeWidgets[item] = nodeAttributes.clone();
   
    });

    var selectId;
    var selectedAtttributeId;


    // Draw nodeType matching selectors
    $.each(sylvaSchema.nodeTypes, function(item, value){
      selectId = item + '_matcher';
      importController
        .append($('<label>')
          .attr('for', selectId)
            .append(item)
        );
      importController
        .append(nodeMatcher.clone()
          .attr('id', selectId)
        );
      
      // Type attributes management
      $.each(value, function(attribute){
        selectedAtttributeId = attribute + '_' + selectId;
        importController
          .append($('<label>')
            .attr('for', selectedAtttributeId)
              .append(item + ':' + attribute));
        importController
          .append($('<select>')
            .attr('id', selectedAtttributeId));
      });

      // Bind change event to reload attributes selector
      $('#'+selectId).change(function(evt){
        var query = 'select[id$=_' + evt.target.id + ']';
        var widget = Importer.matching.nodeAttributeWidgets[evt.target.value];
        $(query).html(widget.html());
      });

      // Autoselect value if matches the label
      var oldVal = $('#'+selectId).val();
      $('#'+selectId).val(item);
      var newVal = $('#'+selectId).val();
      if (newVal !== oldVal){
        $('#'+selectId).trigger('change');
      }

    });

    $('#check-schema-btn').text('Validate node types matching');
    $('#check-schema-btn').click(function(){
      var selectedValue, selectedAttribute, attSelector;
      var validates = true;
      Importer.matching["nodeTypes"] = {};
      Importer.matching["nodeAttributes"] = {};
      $.each(sylvaSchema.nodeTypes, function(item, value){
        selectedValue = $('#'+item+'_matcher').val();
        if (selectedValue === ""){
          alert("ERROR: NodeType does not match: " + item);
          validates = false;
          return false;
        } else {
          Importer.matching.nodeTypes[item] = selectedValue;
        }

        // Attributes
        Importer.matching.nodeAttributes[item] = {};
        $.each(value, function(attribute){
          attSelector = '#' + attribute + '_' + item + '_matcher';
          selectedAttribute = $(attSelector).val();
          if (selectedAttribute === ""){
            alert("ERROR: NodeType attribute does not match: " + attribute);
            validates = false;
            return false;
          } else {
            Importer.matching.nodeAttributes[item][attribute] = selectedAttribute;
          }
        });

      });
      if (validates) {
        $('#check-schema-btn').unbind();
        $('body').trigger($.Event('nodesValidated'));
      }
    });
  },

  validateRelationships: function(importController){
    var edgeText;
    importController.empty();
    var relationshipMatcher = $('<select>').append($('<option>'));
    $.each(Importer.graphSchema.allowedEdges, function(item, value){
      edgeText = GraphEditor.edgeText(value.source, value.target, value.label);
      relationshipMatcher
        .append($('<option>')
          .attr('value', item)
            .append(edgeText));
    });

    var selectId;
    $.each(sylvaSchema.allowedEdges, function(item, value){
      selectId = item.split(" ").join("") + '_matcher';
      edgeText = GraphEditor.edgeText(value.source, value.target, value.label);
      importController
        .append($('<label>')
          .attr('for', selectId)
            .append(edgeText)
        );
      importController
        .append(relationshipMatcher.clone()
          .attr('id', selectId)
        );
    });

    $('#check-schema-btn').text('Validate relationship types matching');
    $('#check-schema-btn').click(function(){
      var selectedValue, selectedLabel;
      var validates = true;
      Importer.matching["edgeTypes"] = {};
      $.each(sylvaSchema.allowedEdges, function(item, value){
        selectedValue = $('#'+item.split(" ").join("")+'_matcher').val()
        if (selectedValue === ""){
          alert("ERROR: RelationshipType does not match: " + item);
          validates = false;
          return false;
        } else {
          selectedLabel = Importer.graphSchema.allowedEdges[item].label;
          Importer.matching.edgeTypes[selectedLabel] = value.label;
        }
      });
      if (validates) {
        $('#check-schema-btn').unbind();
        $('body').trigger($.Event('edgesValidated'));
      }
    });
  }



};
