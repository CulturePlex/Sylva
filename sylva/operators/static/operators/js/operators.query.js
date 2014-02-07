/* Adapted from https://github.com/versae/qbe */
if (!diagram) {
    var diagram = {};
}
diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.CurrentRelations = {};
diagram.Counter = 0;
diagram.fieldCounter = 0;

diagram.lookupsAllValues = ["equals",
                        "is less than or equal to",
                        "is less than",
                        "is greater than",
                        "is greater than or equal to",
                        "is between",
                        "does not equal",
                        "has some value",
                        "has no value"];

diagram.lookupsSpecificValues = ["equals",
                        "does not equal",
                        "has some value",
                        "has no value"];

diagram.lookupsValuesType = {   's': diagram.lookupsSpecificValues,
                                'b': diagram.lookupsSpecificValues,
                                'n': diagram.lookupsAllValues,
                                'x': diagram.lookupsSpecificValues,
                                'd': diagram.lookupsAllValues,
                                't': diagram.lookupsAllValues,
                                'c': diagram.lookupsSpecificValues,
                                'f': diagram.lookupsAllValues,
                                'r': diagram.lookupsSpecificValues,
                                'w': diagram.lookupsAllValues,
                                'a': diagram.lookupsAllValues,
                                'i': diagram.lookupsAllValues,
                                'o': diagram.lookupsAllValues,
                                'e': diagram.lookupsSpecificValues
                            };

(function($) {
    /**
      * AJAX Setup for CSRF Django token
      */
    $.ajaxSetup({
         beforeSend: function(xhr, settings) {
             function getCookie(name) {
                 var cookieValue = null;
                 if (document.cookie && document.cookie != '') {
                     var cookies = document.cookie.split(';');
                     for (var i = 0; i < cookies.length; i++) {
                         var cookie = jQuery.trim(cookies[i]);
                         // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
             }
             if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                 // Only send the token to relative URLs i.e. locally.
                 xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
             }
         }
    });

    init = function() {
        diagram.Defaults = {};
        diagram.Defaults["single"] = {
            label: null,
            paintStyle: {
                strokeStyle: '#AEAA78',
                lineWidth: 2
            },
            backgroundPaintStyle: {
                lineWidth: 4,
                strokeStyle: '#AEAA78'
            },
            overlays: function(labelOptions) {
                return [
                    ["Label", labelOptions],
                    ["PlainArrow", {
                        foldback: 0,
                        fillStyle: '#348E82',
                        strokeStyle: '#348E82',
                        location: 0.99,
                        width: 10,
                        length: 10}
                    ]
                ];
            }
        };
        diagram.Defaults["double"] = {
            label: null,
            cssClass: "connection",
            paintStyle: {
                strokeStyle: '#DB9292',
                lineWidth: 2
            },
            backgroundPaintStyle: {
                lineWidth: 4,
                strokeStyle: '#C55454'
            },
            overlays: function(labelOptions) {
                return [
                    ["Label", labelOptions],
                    ["PlainArrow", {
                        foldback: 0,
                        fillStyle: '#DB9292',
                        strokeStyle: '#C55454',
                        location: 0.75,
                        width: 10,
                        length: 10}
                    ], ["PlainArrow", {
                        foldback: 0,
                        fillStyle: '#DB9292',
                        strokeStyle: '#C55454',
                        location: 0.25,
                        width: 10,
                        length: 10}
                    ]
                ];
            }
        }

        jsPlumb.Defaults.DragOptions = {cursor: 'pointer', zIndex: 2000};
        jsPlumb.Defaults.Container = diagram.Container;

        /**
         * Adds a new model box with its fields
         */
        diagram.addBox = function (graphName, modelName) {
            var model, root, divBox, divTitle, fieldName, field, divField, divFields, divManies, primaries, countFields, anchorDelete;
            primaries = [];
            model = diagram.Models[graphName][modelName];
            root = $("#"+ diagram.Container);
            diagram.Counter++;
            divBox = $("<DIV>");
            divBox.attr("id", "diagramBox_"+ diagram.Counter +"_"+ modelName);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "200px"
            });
            divBox.addClass("body");
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            // Checkbox for select property
            //checkboxType = $("<INPUT>");
            //checkboxType.attr("type", "checkbox");
            //divTitle.append(checkboxType);
            diagram.setLabel(divTitle, model.name, false);
            anchorDelete = $("<A>");
            anchorDelete.html("x");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.attr("id", "inlineDeleteLink_"+ modelName);
            anchorDelete.addClass("inline-deletelink");
            anchorDelete.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\\."+ modelName).click();
                divFields.toggleClass("hidden");
                anchorDelete.toggleClass("inline-morelink");
                anchorDelete.toggleClass("inline-deletelink");
                diagram.saveBoxPositions();
                jsPlumb.repaintEverything();
            });
            divTitle.append(anchorDelete);
            idFields = "diagramFields_"+ modelName + "_" + diagram.Counter;
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            countFields = 0;
            // Create the select for the properties
            // TODO - INITIALIZE
            divField = diagram.addFieldRow(graphName, modelName, idFields);
            divFields.append(divField);
            // TODO - END
            if (countFields < 5 && countFields > 0) {
                divFields.addClass("noOverflow");
            } else if (countFields > 0) {
                divFields.addClass("fieldsContainer");
                /*
                // Uncomment to change the size of the div containing the regular
                // fields no mouse over/out
                divFields.mouseover(function() {
                    $(this).removeClass("fieldsContainer");
                });
                divFields.mouseout(function() {
                    $(this).addClass("fieldsContainer");
                });
                jsPlumb.repaint(["diagramBox_"+ modelName]);
                */
            }
            if (divManies) {
                divBox.append(divManies);
            }
            divBox.append(divFields);
            for(divField in primaries) {
                divBox.prepend(primaries[divField]);
            }
            divBox.prepend(divTitle);
            root.append(divBox);
            jsPlumb.draggable("diagramBox_"+ diagram.Counter +"_"+ modelName, {
                handle: ".title",
                grid: [10, 10],
                stop: function (event, ui) {
                    var $this, position, left, top;
                    $this = $(this);
                    position = $this.position()
                    left = position.left;
                    if (position.left < 0) {
                        left = "0px";
                    }
                    if (position.top < 0) {
                        top = "0px";
                    }
                    $this.animate({left: left, top: top}, "fast", function() {
                        jsPlumb.repaint(["diagramBox_"+ diagram.Counter +"_"+ modelName]);
                    });
                    diagram.saveBoxPositions();
                }
            });
        };

        /**
         * Set the label fo the fields getting shorter and adding ellipsis
         */
        diagram.setLabel = function (div, label, primary) {
            div.html(label);
            if (label.length > 18) {
                if (primary) {
                    div.html(label.substr(0, 18) +"…");
                } else if (label.length > 21) {
                    div.html(label.substr(0, 21) +"…");
                }
                div.attr("title", label);
                div.attr("alt", label);
            }
            return div;
        };

        /**
         * Adds a model to the layer
         */
        diagram.addModel = function (graphName, modelName) {
            var appModel, model, target1, target2;
            model = diagram.Models[graphName][modelName];
            appModel = graphName +"."+ modelName;
            if (diagram.CurrentModels.indexOf(appModel) < 0) {
                diagram.CurrentModels.push(appModel);
                if (model.is_auto) {
                    target1 = model.relations[0].target;
                    target2 = model.relations[1].target;
                    diagram.addModel(target1.name, target1.model);
                    diagram.addModel(target2.name, target2.model);
                } else {
                    diagram.addBox(graphName, modelName);
                }
                diagram.addRelations(graphName, modelName);
            }
        };

        /*
         * Removes a model from the layer
         */
        diagram.removeModel = function(graphName, modelName) {
            var appModel = graphName +"."+ modelName;
            var pos = diagram.CurrentModels.indexOf(appModel);
            if (pos >= 0) {
                diagram.CurrentModels.splice(pos, 1);
                var model = diagram.Models[graphName][modelName];
                diagram.removeBox(graphName, modelName)
                diagram.removeRelations(graphName, modelName);
            }
        };

        /**
         * Iterate for outgoing relations from modelName to the CurrentModels
         * - graphName.
         * - modelName.
         */
        diagram.addRelations = function(graphName, modelName) {
            var sourceId, targetId, model, lengthRelations, relationIndex, relation;
            model = diagram.Models[graphName][modelName];
            lengthRelations = model.relations.length;
            for(var relationIndex = 0; relationIndex < lengthRelations; relationIndex++) {
                relation = model.relations[relationIndex];
                if ((diagram.CurrentModels.indexOf(graphName +"."+ relation.source) >= 0)
                    && (diagram.CurrentModels.indexOf(graphName +"."+ relation.target) >= 0)) {
                    sourceId = "diagramBox_"+ relation.source;
                    if (relation.source === relation.target) {
                        // Reflexive relationships
                        targetId = "inlineDeleteLink_"+ relation.target;
                    } else {
                        targetId = "diagramBox_"+ relation.target;
                    }
                    diagram.addRelation(sourceId, targetId, relation.label);
                }
            }
        }

        /**
         * Create a relation between a element with id sourceId and targetId
         * - sourceId.
         * - targetId.
         * - label.
         * - relStyle.
         */
        diagram.addRelation = function(sourceId, targetId, label, relStyle) {
            var connection, connectionKey, currentLabel;
            // var mediumHeight;
            // mediumHeight = sourceField.css("height");
            // mediumHeight = parseInt(mediumHeight.substr(0, mediumHeight.length - 2)) / 2;
            connectionKey = sourceId +"~"+ targetId;
            if (!(connectionKey in diagram.CurrentRelations)) {
                if (!relStyle || (relStyle !== "single" && relStyle !== "double")) {
                    relStyle = "single"
                }
                connection = jsPlumb.connect({
                    scope: "diagramBox",
                    source: sourceId,
                    target: targetId,
                    detachable:false,
                    connector:"Flowchart",
                    paintStyle: diagram.Defaults[relStyle].paintStyle,
                    backgroundPaintStyle: diagram.Defaults[relStyle].backgroundPaintStyle,
                    overlays: diagram.Defaults[relStyle].overlays({
                        label: label,
                        cssClass: "connection",
                        id: connectionKey
                    }),
                    endpoint: "Blank",
                    anchor:"Continuous"
                });
                diagram.CurrentRelations[connectionKey] = connection;
            } else {
                connection = diagram.CurrentRelations[connectionKey].getOverlay(connectionKey);
                currentLabel = connection.getLabel();
                connection.setLabel(currentLabel + "<br/>"+ label);
            }
        }

       /**
         * Save the positions of the all the boxes in a serialized way into a
         * input type hidden
         */
        diagram.saveBoxPositions = function () {
            var positions, positionsString, left, top, splits, appModel, modelName;
            positions = [];
            for(var i=0; i<diagram.CurrentModels.length; i++) {
                appModel = diagram.CurrentModels[i];
                splits = appModel.split(".");
                modelName = splits[1];
                left = $("#diagramBox_"+ modelName).css("left");
                top = $("#diagramBox_"+ modelName).css("top");
                status = $("#diagramBox_"+ modelName +" > div > a").hasClass("inline-deletelink");
                positions.push({
                    modelName: modelName,
                    left: left,
                    top: top,
                    status: status
                });
            }
            positionsString = JSON.stringify(positions);
        };

        /**
         * Load the node type from the schema
         * - typeName
         */
        diagram.loadBox = function(typeName) {
            var graph, models, modelName, position, positionºs, titleAnchor;
            if (diagram.Models) {
                for(graph in diagram.Models) {
                    models = diagram.Models[graph];
                    for(modelName in models) {
                        if((modelName.localeCompare(typeName)) == 0)
                            diagram.addBox(graph, modelName);
                    }
                }
            }
            positions = JSON.parse($("#id_diagram_positions").val());
            for(var i=0; i<positions.length; i++) {
                position = positions[i]
                $("#diagramBox_"+ position.modelName).css({
                    left: position.left,
                    top: position.top
                });
                if (!JSON.parse(position.status)) {
                    titleAnchor = $("#diagramBox_"+ position.modelName +" > div > a");
                    titleAnchor.removeClass("inline-deletelink");
                    titleAnchor.addClass("inline-morelink");
                    $("#diagramFields_"+ position.modelName).toggleClass("hidden");
                }
            }
            jsPlumb.repaintEverything();
        };

        /**
        * Add a new row for a field in a box
        * - graphName
        * - modelName
        * - parentId
        */

        diagram.addFieldRow = function(graphName, modelName, parentId) {
            model = diagram.Models[graphName][modelName];
            lengthFields = model.fields.length;
            diagram.fieldCounter++;
            var fieldId = "field" + diagram.fieldCounter;
            // Select property
            selectProperty = $("<SELECT>");
            selectProperty.addClass("select-property");
            selectProperty.css({
                'width': '45%',
                'padding': '0'
            });
            selectProperty.attr('data-fieldid', fieldId)
            // Select lookup
            selectLookup = $("<SELECT>");
            selectLookup.addClass("select-lookup");
            selectLookup.css({
                "width": "25%",
                "display": "inline",
                "margin-left": "3%"
            });
            // We get the values for the properties select and the values
            // for the lookups option in relation with the datatype
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = model.fields[fieldIndex];
                datatype = field.type;
                optionProperty = $("<OPTION>");
                optionProperty.addClass('option-property');
                optionProperty.attr('value', field.name);
                optionProperty.attr('data-datatype', field.type);
                optionProperty.html(field.name);
                selectProperty.append(optionProperty);
            }
            // Initial input
            inputLookup = $("<INPUT>");
            inputLookup.css({
                "width": "20%",
                "margin-left": "5%"
            });
            // Link to remove the lookup
            removeField = $("<A>");
            removeField.addClass("remove-field-row");
            removeField.css({
                "margin-left": "2%"
            });
            removeField.attr('data-fieldid', fieldId)
            // Icon
            removeFieldIcon = $("<I>");
            removeFieldIcon.addClass("icon-minus-sign");
            // Link to add the lookup
            addField = $("<A>");
            addField.addClass("add-field-row");
            addField.css({
                "margin-left": "2%"
            });
            addField.attr("data-parentid", parentId);
            addField.attr("data-graph", graphName);
            addField.attr("data-model", modelName);
            // Icon
            addFieldIcon = $("<I>");
            addFieldIcon.addClass("icon-plus-sign");
            divField = $("<DIV>");
            divField.addClass("field");
            divField.css({
                'display': 'inline-table',
                'margin-top': '5%',
                'margin-bottom': '5%'
            });
            divField.attr('id', fieldId);
            // We append the elements
            removeField.append(removeFieldIcon);
            addField.append(addFieldIcon);
            divField.append(selectProperty);
            divField.append(selectLookup);
            divField.append(inputLookup);
            divField.append(removeField);
            divField.append(addField);

            return divField;
        };

        /**
        * Choose the options according to the datatype
        * - datatype
        */
        diagram.lookupOptions = function(datatype) {
            return diagram.lookupsValuesType[datatype];
        };
    };

    /**
     * Interactions functions
     */

     /**
      * Add box type to the diagram
      */

    $('.add-box').on('click', function() {
        var $this = $(this);
        var nodeType = $this.data("type");
        diagram.loadBox(nodeType);
    });

    /**
      * Add lookup inside a box type
      */

    $("#diagramContainer").on('click', '.add-field-row', function() {
        var $this = $(this);
        var parentId = $this.data("parentid");
        var modelName = $this.data("model");
        var graphName = $this.data("graph");

        divField = diagram.addFieldRow(graphName, modelName, parentId);
        $("#" + parentId).append(divField);
    });

    /**
      * Remove lookup inside a box type
      */

    $("#diagramContainer").on('click', '.remove-field-row', function() {
        var $this = $(this);
        var fieldId = $this.data("fieldid");
        $("#" + fieldId).remove();
    });

    /**
      * Add the values of the select lookup in relation with the property
      * selected
      */

    $("#diagramContainer").on('click', '.select-property', function() {
        var $this = $(this);
        var fieldId = $this.data("fieldid");
        var selector = "#" + fieldId + " .select-lookup";
        var datatype = $('option:selected', this).data("datatype");
        arrayOptions = diagram.lookupOptions(datatype);

        // If already we have lookups, we remove them to avoid overwritting
        if($(selector).children()) {
            $(selector).children().remove();
        }

        for (var i = 0; i < arrayOptions.length; i++) {
            $(selector).append('<option value="' + arrayOptions[i] + '">' + arrayOptions[i] + '</option>');
        }
    });

    $(document).ready(init);
})(jQuery);
