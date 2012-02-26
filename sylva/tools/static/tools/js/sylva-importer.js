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
  importController: '#import-controller',

  graphSchema: undefined,
  matching: {},

  loadFileStep: function() {
    $('#validation-controls').hide();
    $('#second-step').hide();
    $('#third-step').hide();
  },

  validateSchemasStep: function() {
    $('body').bind('fileLoaded', function(){
      $('#second-step').show();
      $('#validation-controls').show();

      GraphEditor.schemaToList('sylva-schema-nodes',
            'sylva-schema-edges',
            sylvaSchema);

      $('#check-schema-btn').click(function(){
        $('#check-schema-btn').unbind();
        // Load schema data with selected labels
        Importer.graphSchema = GraphEditor.loadSchema(
          $('#node-type-label').val(),
          $('#edge-type-label').val()
        );

        $('#check-schema-btn').text('Start matching process');
        $('#check-schema-btn').click(function(){
          $('#check-schema-btn').unbind();
          $('body').trigger($.Event('schemasAccepted'));
        });
      });
    });
  },

  nodeTypesMatchingStep: function() {
    $('body').bind('schemasAccepted', function(){
      $('#first-step').hide();
      Importer.validateNodes($(Importer.importController));
    });
  },

  relationshipTypesMatchingStep: function() {
    $('body').bind('nodesValidated', function(){
      Importer.validateRelationships($(Importer.importController));
    });

    $('body').bind('edgesValidated', function(){
      $('#second-step').hide();
      $('#validation-controls').hide();
      $('#third-step').show();

      var nodes = GraphEditor.getGraphNodesJSON();
      var edges = GraphEditor.getGraphEdgesJSON();
      Importer.addData(GraphEditor.getGraphNodesJSON(),
          GraphEditor.getGraphEdgesJSON(),
          '#import-progress-bar',
          '#import-progress-text');
    });
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
      if (value !== ""){
        if (value === '_nameLabel'){
         properties[index] = nodeName;
        } else {
          properties[index] = nodeData[value];
        }
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
      }
    });
  },

  addEdge: function(sourceName, edgeLabel, targetName, edgeData){
    var edgeType;
    $.each(Importer.matching.edgeTypes, function(index, item){
      if (item.label === edgeLabel) {
        edgeType = index;
        return false;
      }
    });

    var properties = {};

    $.each(Importer.matching.edgeAttributes[edgeType], function(index, value){
      if (value != ""){
        properties[index] = edgeData[value];
      }
    });

    $.ajax({
      url: Importer.addRelationshipURL,
      data: {
        type: Importer.matching.edgeTypes[edgeType].label,
        sourceId: Importer.nodes[sourceName]._id,
        targetId: Importer.nodes[targetName]._id,
        properties: JSON.stringify(properties)
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
        Importer.addEdge(value.source, value.type, value.target, value.properties);
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
    var elementDiv;


    // Draw nodeType matching selectors
    $.each(sylvaSchema.nodeTypes, function(item, value){
      selectId = item + '_matcher';
      elementDiv = $('<div>').addClass('import-type-matcher');
      elementDiv
        .append($('<label>')
          .attr('for', selectId)
            .append(item)
        );
      elementDiv
        .append(nodeMatcher.clone()
          .attr('id', selectId)
        );
      importController
        .append(elementDiv);
      
      // Type attributes management
      $.each(value, function(attribute, required){
        selectedAtttributeId = attribute + '_' + selectId;
        elementDiv = $('<div>').addClass('import-property-matcher');
        elementDiv
          .append($('<label>')
            .attr('for', selectedAtttributeId)
              .append(item + ':' + attribute));
        elementDiv
          .append($('<select>')
            .attr('id', selectedAtttributeId));
        importController
          .append(elementDiv);
        if (required) {
          $('label[for='+selectedAtttributeId+']')
            .css('color', 'red');
        }
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
        $.each(value, function(attribute, required){
          attSelector = '#' + attribute + '_' + item + '_matcher';
          selectedAttribute = $(attSelector).val();
          if (required && selectedAttribute === ""){
            alert("ERROR: " + item + " attribute is required: " + attribute);
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

    Importer.matching.edgeAttributeWidgets = {};

    var edgeText;
    importController.empty();
    var edgeAttributes;
    var relationshipMatcher = $('<select>').append($('<option>'));
    $.each(Importer.graphSchema.allowedEdges, function(item, value){
      edgeText = GraphEditor.edgeText(value.source, value.target, value.label);
      relationshipMatcher
        .append($('<option>')
          .attr('value', item)
            .append(edgeText));
      edgeAttributes = $('<select>').append($('<option>'));
      $.each(value.properties, function(attribute){
        edgeAttributes
          .append($('<option>')
            .attr('value', attribute)
              .append(attribute));
      });

      // Store edgeType attributes selectors
      Importer.matching.edgeAttributeWidgets[item] = edgeAttributes.clone();

    });


    var selectId;
    var elementDiv;

    // Draw allowedEdges matching selectors
    $.each(sylvaSchema.allowedEdges, function(i, value){
      var item = value.source + '_' + value.label + '_' + value.target;
      selectId = item.split(" ").join("") + '_matcher';
      edgeText = GraphEditor.edgeText(value.source, value.target, value.label);
      elementDiv = $('<div>').addClass('import-type-matcher');
      elementDiv
        .append($('<label>')
          .attr('for', selectId)
            .append(edgeText)
        );
      elementDiv
        .append(relationshipMatcher.clone()
          .attr('id', selectId)
        );
      importController.append(elementDiv);

      // Type attributes management
      $.each(value.properties, function(attribute, required){
        selectedAtttributeId = attribute + '_' + selectId;
        elementDiv = $('<div>').addClass('import-property-matcher');
        elementDiv
          .append($('<label>')
            .attr('for', selectedAtttributeId)
              .append(item + ':' + attribute));
        elementDiv
          .append($('<select>')
            .attr('id', selectedAtttributeId));
        importController
          .append(elementDiv);
        if (required) {
          $('label[for='+selectedAtttributeId+']')
            .css('color', 'red');
        }
      });

      // Bind change event to reload attributes selector
      $('#'+selectId).change(function(evt){
        var query = 'select[id$=_' + evt.target.id + ']';
        var widget = Importer.matching.edgeAttributeWidgets[evt.target.value];
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

    $('#check-schema-btn').text('Validate relationship types matching');
    $('#check-schema-btn').click(function(){
      var selectedValue, selectedLabel, selectedAttribute;
      var validates = true;
      Importer.matching["edgeTypes"] = [];
      Importer.matching["edgeAttributes"] = [];
      $.each(sylvaSchema.allowedEdges, function(i, value){
        var item = value.source + '_' + value.label + '_' + value.target;
        var itemId = item.split(" ").join("")+'_matcher';
        selectedValue = $('#'+itemId).val()
        if (selectedValue === ""){
          alert("ERROR: RelationshipType does not match: " + item);
          validates = false;
          return false;
        } else {
          selectedLabel = Importer.graphSchema.allowedEdges[item].source +
                            Importer.graphSchema.allowedEdges[item].label +
                            Importer.graphSchema.allowedEdges[item].target;
          Importer.matching.edgeTypes.push({
            label: value.label,
            source: value.source,
            target: value.target
          });
        }
        
        // Attributes
        var attributes = {};
        $.each(value.properties, function(attribute, required){
          attSelector = '#' + attribute + '_' + itemId;
          selectedAttribute = $(attSelector).val(); 
          if (required && selectedAttribute === ""){
            alert("ERROR: " + item + " attribute is required: " + attribute);
            validates = false;
            return false;
          } else {
            attributes[attribute] = selectedAttribute;
          }
        });
        Importer.matching.edgeAttributes.push(attributes);


      });
      if (validates) {
        $('#check-schema-btn').unbind();
        $('body').trigger($.Event('edgesValidated'));
      }
    });
  }



};
