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

diagram.stringValues = {
    'e' : gettext("equals"),
    'le': gettext("is less than or equal to"),
    'lt': gettext("is less than"),
    'gt': gettext("is greater than"),
    'ge': gettext("is greater than or equal to"),
    'b' : gettext("is between"),
    'ne': gettext("does not equal"),
    'v' : gettext("has some value"),
    'nv': gettext("has no value"),
    'c' : gettext("contains"),
    'nc': gettext("doesn't contain"),
    's' : gettext("starts with"),
    'en': gettext("ends with")
};


diagram.lookupsAllValues = [
    diagram.stringValues['e'],
    diagram.stringValues['le'],
    diagram.stringValues['lt'],
    diagram.stringValues['gt'],
    diagram.stringValues['ge'],
    diagram.stringValues['b'],
    diagram.stringValues['ne'],
    diagram.stringValues['v'],
    diagram.stringValues['nv']
];

diagram.lookupsSpecificValues = [
    diagram.stringValues['e'],
    diagram.stringValues['ne'],
    diagram.stringValues['v'],
    diagram.stringValues['nv']
];

diagram.lookupsTextValues = [
    diagram.stringValues['e'],
    diagram.stringValues['ne'],
    diagram.stringValues['v'],
    diagram.stringValues['nv'],
    diagram.stringValues['c'],
    diagram.stringValues['nc'],
    diagram.stringValues['s'],
    diagram.stringValues['en']
];

diagram.lookupsValuesType = {
    's': diagram.lookupsTextValues,
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

        jsPlumb.Defaults.DragOptions = {cursor: 'pointer', zIndex: 2000};
        jsPlumb.Defaults.Container = diagram.Container;

        /**
         * Adds a new model box with its fields
         * - graphName
         * - modelName
         * - typeName
         */
        diagram.addBox = function (graphName, modelName, typeName) {
            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, fieldName, field, primaries, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, handlerAnchor;
            var relationsIds = [];
            primaries = [];
            model = diagram.Models[graphName][modelName];
            root = $("#"+ diagram.Container);
            diagram.Counter++;
            idBox = "diagramBox-" + diagram.Counter +"-"+ modelName;
            idTopBox = "diagramTopBox-" + diagram.Counter + "-" + modelName;
            idFields = "diagramFields-" + diagram.Counter + "-" + modelName;
            idAllRels = "diagramAllRel-" + diagram.Counter + "-" + modelName;
            idContainerBoxes = "diagramContainerBoxes-" + diagram.Counter + "-" + modelName;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "245px"
                //"width": "33%"
            });
            divBox.addClass("body");
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("select-rel");

            var relationsLength = model.relations.length;
            for(var i = 0; i < relationsLength; i++) {
                var relation = model.relations[i];
                var label = relation.label;
                var name = relation.name;
                var relationId = idBox + "-" + label;

                // We store the relations ids to remove when we need it
                relationsIds.push(relationId);

                divAllRel = $("<DIV>");
                divAllRel.addClass("div-list-rel");
                divAllRel.css({
                    "display": "table-row"
                });
                divAllRel.attr("id", relationId);

                listRelElement = $("<LI>");
                listRelElement.addClass("list-rel");
                listRelElement.css({
                    "list-style": "none",
                    "color": "#99999D",
                    "height": "20px",
                    "font-size": "12px",
                    "padding": "2px 5px 2px 5px",
                    "display": "table-cell"
                });
                listRelElement.html(name);

                // Link to add the relations
                addRelation = $("<A>");
                addRelation.addClass("add-relation");
                addRelation.attr('data-parentid', idBox);
                addRelation.attr('data-patternid', relationId);
                addRelation.attr('data-relsid', idAllRels);
                addRelation.attr('data-label', label);
                addRelation.attr('data-modelname', modelName);
                addRelation.attr('data-relnumber', i);

                if(relation.source) {
                    addRelation.attr("data-source", relation.source);
                    if(!diagram.colorsForLabels[relation.source])
                        diagram.colorsForLabels[relation.source] = diagram.randomColor();
                } if(relation.target) {
                    addRelation.attr("data-target", relation.target);
                    if(!diagram.colorsForLabels[relation.target])
                        diagram.colorsForLabels[relation.target] = diagram.randomColor();
                }

                // Add relation icon
                addRelationIcon = $("<I>");
                addRelationIcon.addClass("icon-plus-sign");
                addRelationIcon.css({
                    "margin-left": "162px"
                });
                addRelation.append(addRelationIcon);

                // Link to remove the relations
                removeRelation = $("<A>");
                removeRelation.addClass("remove-relation");
                removeRelation.attr('data-parentid', relationId);
                removeRelation.attr('data-label', label);

                // Remove relation icon
                removeRelationIcon = $("<I>");
                removeRelationIcon.addClass("icon-minus-sign");
                removeRelationIcon.css({
                    "margin-left": "9px"
                });
                removeRelation.append(removeRelationIcon);

                divAllRel.append(listRelElement);
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
            divTitle = diagram.addTitleDiv(graphName, model, typeName, modelName, idTopBox, idBox, relationsIds);
            // Create the select for the properties
            var boxalias = divTitle.data('boxalias');
            divField = diagram.addFieldRow(graphName, modelName, idFields, typeName, boxalias, relationsIds);
            divFields.append(divField);
            if (countFields < 5 && countFields > 0) {
                divFields.addClass("noOverflow");
            } else if (countFields > 0) {
                divFields.addClass("fieldsContainer");
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
            addField.attr("data-boxalias", boxalias);
            addField.attr("data-idbox", idBox);
            addField.attr("data-idallrels", idAllRels);
            addField.attr("data-relationsids", relationsIds);
            // Icon
            addFieldIcon = $("<I>");
            addFieldIcon.addClass("icon-plus-sign");
            addFieldIcon.css({
                "float": "right",
                "margin-right": "4px"
            });
            addField.append(addFieldIcon);
            divAddBox = $("<DIV>");
            divAddBox.attr("id", idTopBox);
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
            jsPlumb.draggable("diagramBox-"+ diagram.Counter +"-"+ modelName, {
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
                        jsPlumb.repaint(["diagramBox-"+ diagram.Counter +"-"+ modelName]);
                    });
                    diagram.saveBoxPositions();
                    jsPlumb.repaintEverything();
                }
            });
        };

        /**
         * Set all the neccesary to create the title div
         * - graphName
         * - model
         * - typeName
         * - modelName
         * - idTopBox
         * - idBox
         * - relationsIds
         */
        diagram.addTitleDiv = function(graphName, model, typeName, modelName, idTopBox, idBox, relationsIds) {
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
            optionNodetype.attr('data-modelid', model.id);
            optionNodetype.attr('value', model.name + diagram.nodetypesCounter[typeName]);
            optionNodetype.attr('selected', 'selected');
            optionNodetype.html(model.name + diagram.nodetypesCounter[typeName]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++)
            {
                $($('.select-nodetype-' + typeName)[i]).append(optionNodetype.clone(true));
                $($('.select-nodetype-' + typeName + ' #' + model.name + i)[i]).attr('selected', 'selected');
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.nodetypesCounter[typeName]; j++) {
                var value = model.name + j;
                selectNodetype.append("<option class='option-nodetype-" + typeName + "' id='" + value + "' data-modelid='" + model.id + "' value='" + value +"'>" + value + "</option>");
            }
            selectNodetype.append(optionNodetype);
            // Checkbox for select type
            checkboxType = $("<INPUT>");
            checkboxType.attr("id", "checkbox-" + idBox);
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
                $('#' + idTopBox).toggleClass("hidden");
                if (iconToggle.attr('class') == 'icon-minus-sign') {
                    iconToggle.removeClass('icon-minus-sign');
                    iconToggle.addClass('icon-plus-sign');

                    /*for(var i = 0; i < relationsIds.length; i++) {
                        jsPlumb.toggle(relationsIds[i]);
                    }*/
                } else {
                    iconToggle.removeClass('icon-plus-sign');
                    iconToggle.addClass('icon-minus-sign');

                    /*for(var i = 0; i < relationsIds.length; i++) {
                        jsPlumb.toggle(relationsIds[i]);
                    }*/
                }
                jsPlumb.repaintEverything();
                diagram.saveBoxPositions();
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
                for(var i = 0; i < relationsIds.length; i++) {
                    jsPlumb.deleteEndpoint(relationsIds[i] + "-source");
                    jsPlumb.deleteEndpoint(relationsIds[i] + "-target");
                }

                $('#' + idBox).remove();
            });
            divTitle.append(anchorDelete);
            divTitle.append(anchorShowHide);

            divTitle.attr("data-boxalias", model.name + diagram.nodetypesCounter[typeName]);

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
                    sourceId = "diagramBox-"+ relation.source;
                    if (relation.source === relation.target) {
                        // Reflexive relationships
                        targetId = "inlineDeleteLink_"+ relation.target;
                    } else {
                        targetId = "diagramBox-"+ relation.target;
                    }
                    diagram.addRelation(sourceId, targetId, relation.label);
                }
            }
        }

        /**
         * Create a relation between a pattern with id sourceId and targetId
         * - sourceId.
         * - targetId.
         * - label.
         * - relStyle.
         */
        diagram.addRelation = function(sourceId, targetId, label, relStyle) {
            var connection, connectionKey, currentLabel;
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
                left = $("#diagramBox-"+ modelName).css("left");
                top = $("#diagramBox-"+ modelName).css("top");
                status = $("#diagramBox-"+ modelName +" > div > a").hasClass("inline-deletelink");
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
                $("#diagramBox-"+ position.modelName).css({
                    left: position.left,
                    top: position.top
                });
                if (!JSON.parse(position.status)) {
                    titleAnchor = $("#diagramBox-"+ position.modelName +" > div > a");
                    titleAnchor.removeClass("inline-deletelink");
                    titleAnchor.addClass("inline-morelink");
                    $("#diagramFields-"+ position.modelName).toggleClass("hidden");
                }
            }
            jsPlumb.repaintEverything();
        };

        /**
         * Add a new row for a field in a box
         * - graphName
         * - modelName
         * - parentId
         * - typeName
         * - boxalias
         * - relationsIds
         */
        diagram.addFieldRow = function(graphName, modelName, parentId, typeName, boxalias, relationsIds) {
            var model, lengthFields, fieldId, selectProperty, selectLookup, field, datatype, optionProperty, inputLookup, divField, divAndOr, selectAndOr, removeField, removeFieldIcon, checkboxProperty;
            model = diagram.Models[graphName][modelName];
            lengthFields = model.fields.length;
            diagram.fieldCounter++;
            fieldId = "field" + diagram.fieldCounter;
            // Select property
            selectProperty = $("<SELECT>");
            selectProperty.addClass("select-property");
            selectProperty.css({
                "width": "110px",
                "padding": "0",
                "margin-left": "2%",
                "display": "inline"
            });
            selectProperty.attr('data-fieldid', fieldId)
            selectProperty.attr('data-boxalias', boxalias);
            // Select lookup
            selectLookup = $("<SELECT>");
            selectLookup.addClass("select-lookup");
            selectLookup.css({
                "width": "80px",
                "padding": "0",
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
                "display": "inline-table",
                "margin-top": "4%"
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
                    "width": "50px",
                    "padding": "0",
                    "margin-left": "2%"
                });
                selectAndOr.append("<option class='option-and-or' value='and'>" + gettext("And") + "</option>");
                selectAndOr.append("<option class='option-and-or' value='or'>" + gettext("Or") + "</option>");
                divAndOr.append(selectAndOr);
                divField.append(divAndOr);
                // Link to remove the lookup
                removeField = $("<A>");
                removeField.addClass("remove-field-row");
                removeField.attr('data-fieldid', fieldId);
                removeField.attr('data-parentid', parentId);
                removeField.attr('data-relationsid', relationsIds);
                // Icon
                removeFieldIcon = $("<I>");
                removeFieldIcon.addClass("icon-minus-sign");
                removeFieldIcon.css({
                    "float": "right"
                });
                removeField.append(removeFieldIcon);
                divField.append(removeField);
            }

            // We append the patterns
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
         * Calculate the anchor for an endpoint pattern.
         * The height used for the relations divs are
         * 24 px each
         * - parentId
         * - relsId
         * - relNumber
         */
         diagram.calculateAnchor = function(parentId, relsId, relNumber) {
            var proportion = $('#' + relsId).css('height').replace(/[^-\d\.]/g, '') / $('#' + parentId).css('height').replace(/[^-\d\.]/g, '')
            var percentage = (1 - proportion) + 0.05;
            var result = percentage + (relNumber * 0.15);

            return result;
         };

        /**
         * Returns the options of a relationship
         * - type
         * - label
         * - color
         * - anchor
         */
         diagram.getRelationshipOptions = function(type, label, color, anchor) {
            var relationshipOptions = null;

            if(type == 'source') {
                relationshipOptions = { endpoint: ["Dot", {radius: 7}],
                                anchor: [1, anchor, -1, 0],
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
                                    strokeStyle: '#348E82'
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: '#348E82',
                                    lineWidth: 3
                                }
                              };
            } else if(type == 'target') {
                relationshipOptions = { endpoint: ["Dot", {radius: 7}],
                                anchor: [0, anchor, -1, 0],
                                isTarget: true,
                                connectorStyle: { strokeStyle: '#AEAA78',
                                                  lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", { width:10, length:10, location:1, id:"arrow"}]
                                ],
                                paintStyle: {
                                    strokeStyle: '#348E82'
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: '#348E82',
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
        var boxalias = $this.data("boxalias");
        var idBox = $this.data("idbox");
        var idAllRels = $this.data("idallrels");
        var relationsIds = $this.data("relationsids");

        divField = diagram.addFieldRow(graphName, modelName, parentId, boxalias, relationsIds);

        $("#" + parentId).append(divField);

        for(var i = 0; i < relationsIds.length; i++) {
            // The idea is get the relations id to recalculate anchors
            // for the endpoints, but we get a weird error with the
            // variable relationsIds
            var anchor = diagram.calculateAnchor(idBox, idAllRels, i);
        }

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
            $(selector).append('<option class="lookup-option" value="' + arrayOptions[i] + '">' + arrayOptions[i] + '</option>');
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
            select.addClass("lookup-value");
            select.css({
                "width": "75px",
                "display": "inline",
                "margin-left": "5%",
                "padding": "0"
            });
            select.append('<option class="lookup-value" value="true">True</option>');
            select.append('<option class="lookup-value" value="false">False</option>');
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
            select.addClass("lookup-value");
            select.css({
                "width": "75px",
                "display": "inline",
                "margin-left": "5%",
                "padding": 0
            });
            for(var j = 0; j < choicesArray.length; j = j + 2) {
                select.append('<option class="lookup-value" value="' + choicesArray[j] +'">' + choicesArray[j] + '</option>');
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
            var inputLookupDate = $("<INPUT>");
            inputLookupDate.addClass("lookup-value date");
            /*inputLookupDate.css({
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });*/
            inputLookupDate.datepicker();
            var inputLookupTime = $("<INPUT>");
            inputLookupTime.addClass("lookup-value");
            inputLookupTime.css({
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookupTime.timepicker();
            $('#' + fieldId).append(inputLookupDate);
            $('#' + fieldId).append(inputLookupTime);
        } else if(datatype == 'a') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookupDate = $("<INPUT>");
            inputLookupDate.addClass("lookup-value");
            inputLookupDate.css({
                "width": "35px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookupDate.datepicker();
            var inputLookupTime = $("<INPUT>");
            inputLookupTime.addClass("lookup-value");
            inputLookupTime.css({
                "width": "35px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookupTime.timepicker();
            $('#' + fieldId).append(inputLookupDate);
            $('#' + fieldId).append(inputLookupTime);
        } else if(datatype == 'e') {
            // Users select
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var select = $("<SELECT>");
            select.addClass("chosen-select");
            select.attr("data-placeholder", "choose a value...");
            /*select.css({
                "width": "35%",
                "display": "inline",
                "margin-left": "5%",
                "padding": 0
            });*/

            /*select.append("<option value='pepe'>pepe</option>");
            select.append("<option value='joselito'>joselito</option>");
            select.append("<option value='manolo'>manolo</option>");*/

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
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookup.datepicker();
            $('#' + fieldId).append(inputLookup);
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
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            $('#' + fieldId).append(inputLookup);
        }

        if(datatype == 'e') {
            $('.chosen-select').ajaxChosen({
            type: 'GET',
                url: 'http://localhost:8000/operators/jj/query/collaborators/',
                dataType: 'json'
            }, function (data) {
                var results = {};
                $.each(data, function (i, val) {
                    results[i] = val;
                });
                return results;
            }, {no_results_text: "No results matched"});
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
                $this.after("<input style=\"width: 35px; margin-left: 5%; margin-top:3%;\" />");
                $this.after("<input style=\"width: 35px; margin-left: 5%; margin-top:3%;\" />");
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
                $this.after("<input style=\"width: 75px; margin-left: 5%; margin-top: 3%;\" />");
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
        var parentId = $this.data("parentid");
        var patternId = $this.data("patternid");
        var allRelsId = $this.data("relsid");
        var label = $this.data("label");
        var modelName = $this.data("modelname");
        var relNumber = $this.data("relnumber");
        var source = $this.data("source");
        var target = $this.data("target");

        var anchor = diagram.calculateAnchor(parentId, allRelsId, relNumber);

        if(source == target) {
            var uuidSource = patternId + "-source";
            //var scopeSource = source + "-" + label;
            var uuidTarget = patternId + "-target";
            //var scopeTarget = target + "-" + label;
            if(!jsPlumb.getEndpoint(uuidSource)) {
                var endpointSource = jsPlumb.addEndpoint(parentId, { uuid:uuidSource, connector: "Flowchart"},diagram.getRelationshipOptions('source', label, diagram.colorsForLabels[source], anchor));
            }
            if(!jsPlumb.getEndpoint(uuidTarget)) {
                anchor = 0;
                var endpointTarget = jsPlumb.addEndpoint(parentId, { uuid:uuidTarget, connector: "Flowchart"},diagram.getRelationshipOptions('target', label, diagram.colorsForLabels[target], anchor));
            }
        } else {
            if(source == modelName) {
                var uuidSource = patternId + "-source";
                //var scopeSource = source + "-" + label;
                if(!jsPlumb.getEndpoint(uuidSource)) {
                    var endpointSource = jsPlumb.addEndpoint(parentId, { uuid:uuidSource, connector: "Flowchart"},diagram.getRelationshipOptions('source', label, diagram.colorsForLabels[source], anchor));
                }
            } else if(target == modelName) {
                var uuidTarget = patternId + "-target";
                //var scopeTarget = source + "-" + label;
                if(!jsPlumb.getEndpoint(uuidTarget)) {
                    anchor = 0;
                    var endpointTarget = jsPlumb.addEndpoint(parentId, { uuid:uuidTarget, connector: "Flowchart"},diagram.getRelationshipOptions('target', label, diagram.colorsForLabels[target], anchor));
                }
            }
        }
        jsPlumb.repaintEverything();
    });

    /**
     * Add the handler to remove the wire
     */
     $("#diagramContainer").on('click', '.remove-relation', function() {
        var $this = $(this);
        var patternId = $this.data("parentid");
        var label = $this.data("label");
        jsPlumb.deleteEndpoint(patternId + '-source');
        jsPlumb.deleteEndpoint(patternId + '-target');
        jsPlumb.repaintEverything();
    });

    /**
     * Handler for create the JSON file
     */
    $(document).on('click', '#run-button', function() {
        var result = "";
        var propertiesChecked = {};
        // Conditions
        var conditions = "{'conditions': [";
        var properties = $('.select-property');
        $.each(properties, function(index, property){
            var alias = $(property).data('boxalias');
            var condition = "(\'" + $(property).next().val() + "\'," + " (\'property\', " + "\'" + alias + "\'," + "\'" + $(property).val() + "\'), " + "\'" + $(property).next().next().val() + "\'),";
            // We store the checked properties
            propertiesChecked[alias] = new Array();
            if($(property).prev().attr('checked')) {
                propertiesChecked[alias].push($(property).val());
            }
            conditions = conditions + condition;
        });
        conditions = conditions + '],';
        result = result + conditions + '\n';

        // Origin
        var origins = "'origins': [";
        var elements = $('option').filter(function(){ return $(this).attr("class").match(/option-nodetype./);});
        $.each(elements, function(index, element) {
            // We check the type with regex, by now always are nodes
            var origin = "{'alias': \'" + $(element).val() + "\'," + " 'type': 'node'," + " 'type_id': " + $(element).data('modelid') + '},';
            origins = origins + origin;
        });
        origins = origins + '],';
        result = result + origins + '\n';

        // Patterns
        var patterns = "'patterns': [";
        var elements = $('option').filter(function(){ return $(this).attr("class").match(/option-nodetype./);});
        $.each(elements, function(index, element) {
            // We check the type with regex, by now always are nodes
            //var pattern = $(element).val() + "," + 'node' + ',' + $(element).data('modelid');
        });
        patterns = patterns + '],';
        result = result + patterns + '\n';

        // Result
        var results = "'results': [";
        var elements = $('option').filter(function(){ return $(this).attr("class").match(/option-nodetype./);});
        $.each(elements, function(index, element) {
            var properties = propertiesChecked[element.value];
            var value = "{'alias': \'" + $(element).val() + "\'," + " 'properties': [";
            $.each(properties, function(index, property) {
                var val = "\'" + property + "\', ";
                value = value + val;
            });
            results = results + value;
        });
        results = results + ']}';
        result = result + results;

        alert(result);
    });

    $(document).ready(init);
})(jQuery);
