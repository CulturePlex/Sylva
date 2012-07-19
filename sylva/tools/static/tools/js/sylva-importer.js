GraphEditor.progressBar.hide = function() {
  $('#'+GraphEditor.progressBarId).hide();
  GraphEditor._stopRefreshing = false;
  $('body').trigger($.Event('fileLoaded'));
  GraphEditor.refresh();
}

function slugify(text) {
    text = text.replace(/[^-a-zA-Z0-9,&\s]+/ig, '');
    //text = text.replace(/-/gi, "_");
    text = text.replace(/\s/gi, "-");
    return text;
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

  doneWithFiles: function() {
    $('body').trigger($.Event('fileLoaded'));
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
      if (item.label[0] === edgeLabel) {
        edgeType = index;
        return false;
      }
    });

    if (edgeType !== undefined) {
        var properties = {};

        $.each(Importer.matching.edgeAttributes[edgeType], function(index, value){
          if (value != ""){
            properties[index] = edgeData[value];
          }
        });

        $.ajax({
          url: Importer.addRelationshipURL,
          data: {
            type: Importer.matching.edgeTypes[edgeType].label[1],
            sourceId: Importer.nodes[sourceName]._id,
            targetId: Importer.nodes[targetName]._id,
            properties: JSON.stringify(properties)
          },
          success: function(response){
            response = JSON.parse(response);
            Importer.counter++;
            var relationshipText = GraphEditor.edgeText(sourceName, edgeLabel, targetName);
            $(Importer.progressTextId).html('Relationship ' + relationshipText + ' created.');
            $(Importer.progressBarId).attr('value', Importer.counter);
            if (Importer.counterMax === Importer.counter){
              $('body').trigger($.Event('importFinished'));
            }
          }
        });
    }
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
      selectId = slugify(item) + '_matcher';
      elementDiv = $('<div>').addClass('import-type-matcher');
      elementDiv
        .append($('<label>')
          .attr('for', selectId)
            .append(item)
        );
      elementDiv
        .append(nodeMatcher.clone()
          .attr('id', selectId)
          .val(item)  // set default value
        );
      importController
        .append(elementDiv);

      // Type attributes management
      $.each(value, function(attribute, att_properties){
        selectedAtttributeId = slugify(attribute) + '_' + selectId;
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
        if (att_properties.required) {
          $('label[for='+selectedAtttributeId+']')
            .css('color', 'red');
        }
      });

      var query = 'select[id$=_' + selectId + ']';  // id with ending "_{selectId}"
      var widget = Importer.matching.nodeAttributeWidgets[item];
      var $selects = $(query).html(widget.html());  // append <option> elements to each <select>

      // set default value for node attributes' form select
      for (var i = 0, l = $selects.length; i < l; i++) {
        var selectVal = $('label[for=' + $selects[i].id + ']').first().text().split(':');
        $selects[i].value = ('(' + selectVal[0] + ') ' + selectVal[1]);
      }

    });

    $('#check-schema-btn').text('Validate node types matching');
    $('#check-schema-btn').click(function(){
      var selectedValue, selectedAttribute, attSelector;
      var validates = true;
      Importer.matching["nodeTypes"] = {};
      Importer.matching["nodeAttributes"] = {};
      $.each(sylvaSchema.nodeTypes, function(item, value){
        selectedValue = $('#'+slugify(item)+'_matcher').val();
        if (selectedValue === ""){
          alert("ERROR: NodeType does not match: " + item);
          validates = false;
          return false;
        } else {
          Importer.matching.nodeTypes[item] = selectedValue;
        }

        // Attributes
        Importer.matching.nodeAttributes[item] = {};
        $.each(value, function(attribute, att_properties){
          attSelector = '#' + slugify(attribute) + '_' + slugify(item) + '_matcher';
          selectedAttribute = $(attSelector).val();
          if (att_properties.required && selectedAttribute === ""){
            // Do we need to fill all the types?
            // alert("ERROR: " + item + " attribute is required: " + attribute);
            // validates = false;
            // return false;
            return true;
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
    Importer.matching.edgeSlugs = {};

    var edgeText;
    importController.empty();
    var edgeAttributes;
    var relationshipMatcher = $('<select>').append($('<option>'));
    $.each(Importer.graphSchema.allowedEdges, function(item, value){
      edgeText = GraphEditor.edgeText(value.source, value.target, value.label);
      var slug = value.source + '_' + value.label + '_' + value.target;
      Importer.matching.edgeSlugs[slug] = item;
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
      $.each(value.properties, function(attribute, att_properties){
        selectedAtttributeId = slugify(attribute) + '_' + selectId;
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
        if (att_properties.required) {
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
      if (Importer.matching.edgeSlugs.hasOwnProperty(item)) {
         var oldVal = $('#'+selectId).val();
          $('#'+selectId).val(Importer.matching.edgeSlugs[item]);
          var newVal = $('#'+selectId).val();
          if (newVal !== oldVal){
            $('#'+selectId).trigger('change');
          }
      }

    });

    $('#check-schema-btn').text('Validate relationship types matching');
    $('#check-schema-btn').click(function(){
      var selectedValue, selectedAttribute;
      var validates = true;
      Importer.matching["edgeTypes"] = [];
      Importer.matching["edgeAttributes"] = [];
      $.each(sylvaSchema.allowedEdges, function(i, value){
        var item = value.source + '_' + value.label + '_' + value.target;
        var itemId = item.split(" ").join("")+'_matcher';
        selectedValue = $('#'+itemId).val()
        if (selectedValue === ""){
          // Do we need to fill all the types?
          // alert("ERROR: RelationshipType does not match: " + item);
          // validates = false;
          // return false;
          return true;
        } else {
          /*selectedLabel = Importer.graphSchema.allowedEdges[item].source +
                            Importer.graphSchema.allowedEdges[item].label +
                            Importer.graphSchema.allowedEdges[item].target;
                            */
          var graphItem = Importer.graphSchema.allowedEdges[selectedValue];
          Importer.matching.edgeTypes.push({
            label: [graphItem.label, value.label],
            source: [graphItem.source, value.source],
            target: [graphItem.target, value.target]
          });
        }

        // Attributes
        var attributes = {};
        $.each(value.properties, function(attribute, att_properties){
          attSelector = '#' + slugify(attribute) + '_' + itemId;
          selectedAttribute = $(attSelector).val();
          if (att_properties.required && selectedAttribute === ""){
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
