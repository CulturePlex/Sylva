/* Adapted from https://github.com/versae/qbe */

// Django i18n.
var gettext = window.gettext || String;

if (!diagram) {
    var diagram = {};
}
diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.CurrentRelations = {};
diagram.Counter = 0;
diagram.fieldCounter = 0;
diagram.nodetypesCounter = [];
diagram.colorsForLabels = [];

diagram.lookupsAllValues = [gettext("equals"),
                        gettext("is less than or equal to"),
                        gettext("is less than"),
                        gettext("is greater than"),
                        gettext("is greater than or equal to"),
                        gettext("is between"),
                        gettext("does not equal"),
                        gettext("has some value"),
                        gettext("has no value")];

diagram.lookupsSpecificValues = [gettext("equals"),
                        gettext("does not equal"),
                        gettext("has some value"),
                        gettext("has no value")];

diagram.lookupsTextValues = [gettext("equals"),
                        gettext("does not equal"),
                        gettext("has some value"),
                        gettext("has no value"),
                        gettext("contains"),
                        gettext("doesn't contain"),
                        gettext("starts with"),
                        gettext("ends with")];

diagram.lookupsValuesType = {   's': diagram.lookupsTextValues,
                                'b': diagram.lookupsSpecificValues,
                                'n': diagram.lookupsAllValues,
                                'x': diagram.lookupsTextValues,
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
         * - graphName
         * - modelName
         * - typeName
         */
        diagram.addBox = function (graphName, modelName, typeName) {
            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, fieldName, field, primaries, countFields, idFields, boxAllRel, optionAllRel, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation;
            primaries = [];
            model = diagram.Models[graphName][modelName];
            root = $("#"+ diagram.Container);
            diagram.Counter++;
            idBox = "diagramBox_"+ diagram.Counter +"_"+ modelName;
            idFields = "diagramFields_"+ modelName + "_" + diagram.Counter;
            idAllRels = "diagramAllRel_"+ modelName + "_" + diagram.Counter;
            idContainerBoxes = "diagramContainerBoxes_" + modelName + "_" + diagram.Counter;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                //"width": "200px"
                "width": "30%"
            });
            divBox.addClass("body");
            divTitle = diagram.addTitleDiv(graphName, model, typeName, modelName, idContainerBoxes, idBox);
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("select-rel");
            boxAllRel.css({
                "width": "46%",
                "padding": "0",
                "margin-left": "3%",
                "margin-top": "5%",
                "margin-bottom": "5%",
                "display": "inline"
            });
            for(var i = 0; i < model.relations.length; i++) {
                var relation = model.relations[i];
                var label = relation.label;
                var relationId = "div-option-rel-" + diagram.Counter + "-" + i;

                divAllRel = $("<DIV>");
                divAllRel.addClass("div-option-rel");
                divAllRel.attr("id", relationId);

                optionAllRel = $("<LI>");
                optionAllRel.addClass("option-rel");
                optionAllRel.html(label);

                // Link to add the relations
                addRelation = $("<A>");
                addRelation.addClass("add-relation");
                addRelation.css({});
                addRelation.attr('data-parentid', relationId);
                addRelation.html(gettext("add"));

                if(relation.source) {
                    addRelation.attr("data-source", relation.source);
                    if(!diagram.colorsForLabels[relation.source])
                        diagram.colorsForLabels[relation.source] = diagram.randomColor();
                } if(relation.target) {
                    addRelation.attr("data-target", relation.target);
                    if(!diagram.colorsForLabels[relation.target])
                        diagram.colorsForLabels[relation.target] = diagram.randomColor();
                }

                // Link to remove the relations
                removeRelation = $("<A>");
                removeRelation.addClass("remove-relation");
                removeRelation.css({
                    "margin-left": "10%"
                });
                removeRelation.attr('data-parentid', relationId);
                removeRelation.html(gettext("remove"));

                divAllRel.append(optionAllRel);
                divAllRel.append(addRelation);
                divAllRel.append(removeRelation);

                boxAllRel.append(divAllRel);
            }

            divAllowedRelationships = $("<DIV>");
            divAllowedRelationships.attr("id", idAllRels);
            divAllowedRelationships.append(boxAllRel);
            // We append the divs
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            countFields = 0;
            // Create the select for the properties
            divField = diagram.addFieldRow(graphName, modelName, idFields, typeName);
            divFields.append(divField);
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
            // Link to add a new row
            addField = $("<A>");
            addField.addClass("add-field-row");
            addField.css({
                "margin-left": "2%"
            });
            addField.attr("data-parentid", idFields);
            addField.attr("data-graph", graphName);
            addField.attr("data-model", modelName);
            // Icon
            addFieldIcon = $("<I>");
            addFieldIcon.addClass("icon-plus-sign");
            addField.append(addFieldIcon);
            divAddBox = $("<DIV>");
            divAddBox.append(divFields);
            divAddBox.append(addField);
            divAddBox.css({
                "border-bottom": "2px dashed #348E82"
            });
            divContainerBoxes = $("<DIV>");
            divContainerBoxes.attr("id", idContainerBoxes);
            divContainerBoxes.append(divAddBox);
            divContainerBoxes.append(divAllowedRelationships);
            divBox.append(divContainerBoxes);
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
                    jsPlumb.repaintEverything();
                }
            });
        };

        /**
         * Set all the neccesary to include in the title div
         * - graphName
         * - model
         * - typeName
         * - modelName
         * - idContainerBoxes
         * - idBox
         */
        diagram.addTitleDiv = function(graphName, model, typeName, modelName, idContainerBoxes, idBox) {
            var divTitle, selectNodetype, optionNodetype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete;
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.css({
                "padding-bottom": "3%"
            });
            // Select for the type
            selectNodetype = $("<SELECT>");
            selectNodetype.addClass("select-nodetype-" + typeName);
            selectNodetype.css({
                "width": "46%",
                "float": "left",
                "padding": "0",
                "margin-left": "3%"
            });
            optionNodetype = $("<OPTION>");
            optionNodetype.addClass("option-nodetype-" + typeName);
            optionNodetype.attr('id', model.name + diagram.nodetypesCounter[typeName]);
            optionNodetype.attr('value', model.name + diagram.nodetypesCounter[typeName]);
            optionNodetype.attr('selected', 'selected');
            optionNodetype.html(model.name + diagram.nodetypesCounter[typeName]);
            // This for loop is to to add the new option in the old boxes
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++)
            {
                $($('.select-nodetype-' + typeName)[i]).append(optionNodetype.clone(true));
                $($('.select-nodetype-' + typeName + ' #' + model.name + i)[i]).attr('selected', 'selected');
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.nodetypesCounter[typeName]; j++) {
                var value = model.name + j;
                selectNodetype.append("<option class='option-nodetype-" + typeName + "' id='" + value + "' value='" + value +"'>" + value + "</option>");
            }
            selectNodetype.append(optionNodetype);
            // Checkbox for select type
            checkboxType = $("<INPUT>");
            checkboxType.attr("type", "checkbox");
            checkboxType.css({
                "float": "left",
                "margin-top": "1%"
            });
            divTitle.append(checkboxType);
            diagram.setName(divTitle, model.name);
            divTitle.append(selectNodetype);
            anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ modelName);
            iconToggle = $("<I>");
            iconToggle.addClass("icon-minus-sign");
            iconToggle.css({
                "color": "white",
                "float": "right",
                "margin-right": "2%"
            });
            anchorShowHide.append(iconToggle);
            anchorShowHide.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\\."+ modelName).click();
                $('#' + idContainerBoxes).toggleClass("hidden");
                if (iconToggle.attr('class') == 'icon-minus-sign') {
                    iconToggle.removeClass('icon-minus-sign');
                    iconToggle.addClass('icon-plus-sign');
                } else {
                    iconToggle.removeClass('icon-plus-sign');
                    iconToggle.addClass('icon-minus-sign');
                }
                diagram.saveBoxPositions();
                jsPlumb.repaintEverything();
            });
            anchorDelete = $("<A>");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.attr("id", "inlineDeleteLink_"+ modelName);
            iconDelete = $("<I>");
            iconDelete.addClass("icon-remove-sign");
            iconDelete.css({
                "color": "white",
                "float": "right",
                "margin-right": "2%"
            });
            anchorDelete.append(iconDelete);
            anchorDelete.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\\."+ modelName).click();
                jsPlumb.detachAllConnections(idBox);
                jsPlumb.deleteEndpoint(idBox + "-source");
                jsPlumb.deleteEndpoint(idBox + "-target");
                $('#' + idBox).remove();
            });
            divTitle.append(anchorDelete);
            divTitle.append(anchorShowHide);

            return divTitle;
        }

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
         * Set the name fo the model box getting shorter and adding ellipsis
         */
        diagram.setName = function (div, name) {
            var html = "<span style='float: left; margin-left: 3%;'>" + name + " " + gettext("as") + " </span>";
            if (name.length > 5) {
                html = "<span style='float: left; margin-left: 3%;'>" + name.substr(0, 5) + "…" + " " + gettext("as") + " </span>";
            }
            div.append(html);
            return div;
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
                        if((modelName.localeCompare(typeName)) == 0) {
                            // Node type counter for the node type select field
                            if(diagram.nodetypesCounter[typeName] >= 0) {
                                diagram.nodetypesCounter[typeName]++;
                            } else {
                                diagram.nodetypesCounter[typeName] = 0;
                            }
                            diagram.addBox(graph, modelName, typeName);
                        }
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
            var model, lengthFields, fieldId, selectProperty, selectLookup, field, datatype, optionProperty, inputLookup, divField, divAndOr, selectAndOr, removeField, removeFieldIcon, checkboxProperty;
            model = diagram.Models[graphName][modelName];
            lengthFields = model.fields.length;
            diagram.fieldCounter++;
            fieldId = "field" + diagram.fieldCounter;
            // Select property
            selectProperty = $("<SELECT>");
            selectProperty.addClass("select-property");
            selectProperty.css({
                'width': '60%',
                'margin-left': '2%',
                'display': 'inline'
            });
            selectProperty.attr('data-fieldid', fieldId)
            // Select lookup
            selectLookup = $("<SELECT>");
            selectLookup.addClass("select-lookup");
            selectLookup.css({
                "width": "40%",
                "display": "inline",
                "margin-left": "10%"
            });
            // We get the values for the properties select and the values
            // for the lookups option in relation with the datatype
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = model.fields[fieldIndex];
                datatype = field.type;
                optionProperty = $("<OPTION>");
                optionProperty.addClass('option-property');
                optionProperty.attr('value', field.label);
                optionProperty.attr('data-datatype', field.type);
                if(field.choices)
                    optionProperty.attr('data-choices', field.choices);
                optionProperty.html(field.label);
                selectProperty.append(optionProperty);
            }
            divField = $("<DIV>");
            divField.addClass("field");
            divField.css({
                'display': 'inline-table',
                'margin-top': '5%'
            });
            divField.attr('id', fieldId);
            // Checkbox for select property
            checkboxProperty = $("<INPUT>");
            checkboxProperty.attr("type", "checkbox");
            checkboxProperty.css({
                "margin-left": "2%"
            });
            // If we have more than 1 field row, add and-or div
            if ($('#' + parentId).children().length > 0) {
                divAndOr = $("<DIV>");
                divAndOr.addClass("and-or-option");
                divAndOr.css({
                    "margin-bottom": "5%"
                });
                selectAndOr = $("<SELECT>");
                selectAndOr.addClass("select-and-or");
                selectAndOr.css({
                    "width": "35%"
                });
                selectAndOr.append("<option value='and'>And</option>");
                selectAndOr.append("<option value='or'>Or</option>");
                divAndOr.append(selectAndOr);
                divField.append(divAndOr);
                // Link to remove the lookup
                removeField = $("<A>");
                removeField.addClass("remove-field-row");
                removeField.css({
                    "margin-left": "2%",
                    "float": "right"
                });
                removeField.attr('data-fieldid', fieldId);
                removeField.attr('data-parentid', parentId);
                // Icon
                removeFieldIcon = $("<I>");
                removeFieldIcon.addClass("icon-minus-sign");
                removeField.append(removeFieldIcon);
                divField.append(removeField);
            }

            // We append the elements
            divField.append(checkboxProperty);
            divField.append(selectProperty);
            divField.append(selectLookup);

            return divField;
        };

        /**
         * Choose the options according to the datatype
         * - datatype
         */
        diagram.lookupOptions = function(datatype) {
            return diagram.lookupsValuesType[datatype];
        };

        /**
         * Returns a random color
         *
         */
        diagram.randomColor = function() {
            var letters = '0123456789ABCDEF'.split('');
            var color = '#';
            for (var i = 0; i < 6; i++ ) {
                color += letters[Math.round(Math.random() * 15)];
            }
            return color;
        };

        /**
         * Returns the options of a relationship
         *
         */
         diagram.getRelationshipOptions = function(type, label, color) {
            var relationshipOptions = null;

            if(type == 'source') {
                relationshipOptions = { endpoint: "Dot",
                                anchor: "RightMiddle",
                                isSource: true,
                                connectorStyle: { strokeStyle: '#AEAA78',
                                                  lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", { width:10, length:10, location:1, id:"arrow"}],
                                    [ "Label", {location:0.5,
                                                label:label,
                                                id:"label",
                                                cssClass:"connection"}]
                                ],
                                paintStyle: {
                                    strokeStyle: color,
                                    lineWidth: 3
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: color,
                                    lineWidth: 3
                                }
                              };
            } else if(type == 'target') {
                relationshipOptions = { endpoint: "Dot",
                                anchor: "LeftMiddle",
                                isTarget: true,
                                connectorStyle: { strokeStyle: '#AEAA78',
                                                  lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", { width:10, length:10, location:1, id:"arrow"}]
                                ],
                                paintStyle: {
                                    strokeStyle: color,
                                    lineWidth: 3
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: color,
                                    lineWidth: 3
                                }
                              };
            }
            return relationshipOptions;
         }
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
     * Add field row inside a box type
     */
    $("#diagramContainer").on('click', '.add-field-row', function() {
        var $this = $(this);
        var parentId = $this.data("parentid");
        var modelName = $this.data("model");
        var graphName = $this.data("graph");

        divField = diagram.addFieldRow(graphName, modelName, parentId);

        $("#" + parentId).append(divField);
        jsPlumb.repaintEverything();
    });

    /**
     * Remove field row inside a box type
     */
    $("#diagramContainer").on('click', '.remove-field-row', function() {
        var $this = $(this);
        var fieldId = $this.data("fieldid");
        var parentId = $this.data("parentid");

        // We check that the field box need to have one
        // field row at least
        if($('#' + parentId).children().length > 1) {
            $("#" + fieldId).remove();
        } else {
            alert("You need a field at least");
        }
        jsPlumb.repaintEverything();
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
        var choices = $('option:selected', this).data("choices");
        var arrayOptions = diagram.lookupOptions(datatype);

        // If already we have lookups, we remove them to avoid overwritting
        if($(selector).children()) {
            $(selector).children().remove();
        }

        for (var i = 0; i < arrayOptions.length; i++) {
            $(selector).append('<option value="' + arrayOptions[i] + '">' + arrayOptions[i] + '</option>');
            $(selector).attr("data-fieldid", fieldId);
        }

        // Here we ask if the datatype needs a special input
        var tagName = $this.next().next().prop("tagName");
        if(datatype == 'b') {
            // Boolean select
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var select = $("<SELECT>");
            select.css({
                "width": "35%",
                "display": "inline",
                "margin-left": "5%"
            });
            select.append('<option value="true">True</option>');
            select.append('<option value="false">False</option>');
        } else if(datatype == 'c') {
            // Choices select
            var choicesArray = choices.split(',');
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var select = $("<SELECT>");
            select.css({
                "width": "35%",
                "display": "inline",
                "margin-left": "5%"
            });
            for(var j = 0; j < choicesArray.length; j = j + 2) {
                select.append('<option value="' + choicesArray[j] +'">' + choicesArray[j] + '</option>');
            }
            $('#' + fieldId).append(select);
        } else if(datatype == 'w') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.css({
                "width": "20%",
                "margin-left": "5%"
            });
            inputLookup.datepicker();
            $('#' + fieldId).append(inputLookup);
        } else if(datatype == 'a') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.css({
                "width": "20%",
                "margin-left": "5%"
            });
            inputLookup.datepicker();
            $('#' + fieldId).append(inputLookup);
        } else if(datatype == 'e') {
            // Users select
        } else {
            // Initial input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.css({
                "width": "35%",
                "margin-left": "5%"
            });
            $('#' + fieldId).append(inputLookup);
        }
    });

    /**
     * Add a special input related to the lookup selected and the type
     * of the property
     */
    $("#diagramContainer").on('change', '.select-lookup', function() {
        var $this = $(this);
        var value = $this.val();
        // Here we get the datatype for the special inputs for booleans,
        // dates, etc.
        var tagName = $this.next().prop("tagName");
        var fieldId = $this.data("fieldid");
        var datatype = $('#' + fieldId + ' .select-property option:selected').data("datatype");
        var condition = datatype != 'b'
                        && datatype != 'c'
                        && datatype != 'w'
                        && datatype != 'a'
                        && datatype != 'e';
        if(condition) {
            if(value == "is between") {
                // two inputs - we check if we have introduced an input field
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input style=\"width: 10%; margin-left: 5%;\" />");
                $this.after("<input style=\"width: 10%; margin-left: 5%;\" />");
            } else if((value == "has some value") || (value == "has no value")) {
                // no inputs
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
            } else {
                // one input - we check if we have introduced an input field
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input style=\"width: 35%; margin-left: 5%;\" />");
            }
        } else {
            // In this branch, the type would be boolean, choices, date or user
        }
    });

    /**
     * Add the handler for drag and drop relationships
     */
    $("#diagramContainer").on('click', '.add-relation', function() {
        var $this = $(this);
        var elementId = $this.data("parentid");
        var source = $this.data("source");
        var target = $this.data("target");
        // We must check if is target or source and select an endpoint or another
        if(source) {
            var endpointUuid = elementId + "-source";
            var endpointSource = jsPlumb.addEndpoint(elementId, { uuid:endpointUuid, connector: "Flowchart", scope: source}, diagram.getRelationshipOptions('source', source, diagram.colorsForLabels[source]));
        }
        if(target) {
            var endpointUuid = elementId + "-target";
            if(!jsPlumb.getEndpoint(endpointUuid)) {
                var endpointTarget = jsPlumb.addEndpoint(elementId, { uuid:endpointUuid, connector: "Flowchart", scope: target },diagram.getRelationshipOptions('target', target, diagram.colorsForLabels[target]));
            }
        }
        jsPlumb.repaintEverything();
    });

    /**
     * Add the handler to remove the wire
     */
     $("#diagramContainer").on('click', '.remove-relation', function() {
        var $this = $(this);
        var elementId = $this.data("parentid");
        jsPlumb.deleteEndpoint(elementId + '-source');
        jsPlumb.repaintEverything();
    });

    $(document).ready(init);
})(jQuery);
