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
diagram.fieldRelsCounter = 0;
diagram.nodetypesCounter = [];
diagram.reltypesCounter = [];
diagram.fieldsForRels = {};

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
                var relationId = idBox;

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
                addRelation.attr('data-label', label);
                diagram.fieldsForRels[label] = relation.fields;

                if(relation.source) {
                    addRelation.attr("data-source", relation.source);
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
                removeRelation.attr('data-parentid', idBox);
                removeRelation.attr('data-patternid', relationId);
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
            // We add the target relationship handler
            var uuidTarget = idBox + "-target";
            if(!jsPlumb.getEndpoint(uuidTarget)) {
                var endpointTarget = jsPlumb.addEndpoint(idBox, { uuid:uuidTarget, connector: "Flowchart"},diagram.getRelationshipOptions('target', 0));
            }
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
         * Add a box for the relation
         * - label
         */
        diagram.addRelationBox = function(label) {
            // %%%%%%%%%%%%%%%%%%%%%%
            // %%%% Title part
            // %%%%%%%%%%%%%%%%%%%%%%

            var divTitle, selectReltype, optionReltype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete;

            if(diagram.reltypesCounter[label] >= 0) {
                diagram.reltypesCounter[label]++;
            } else {
                diagram.reltypesCounter[label] = 0;
            }

            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.css({
                "padding-bottom": "3%"
            });
            // Select for the type
            selectReltype = $("<SELECT>");
            selectReltype.addClass("select-reltype-" + label);
            selectReltype.css({
                "width": "46%",
                "float": "left",
                "padding": "0",
                "margin-left": "15%"
            });
            optionReltype = $("<OPTION>");
            optionReltype.addClass("option-reltype-" + label);
            optionReltype.attr('id', label + diagram.reltypesCounter[label]);
            optionReltype.attr('value', label + diagram.reltypesCounter[label]);
            optionReltype.html(label + diagram.reltypesCounter[label]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.reltypesCounter[label]; i++)
            {
                $($('.select-reltype-' + label)[i]).append(optionReltype.clone(true));
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.reltypesCounter[label]; j++) {
                var value = label + j;
                selectReltype.append("<option class='option-reltype-" + label + "' id='" + value + "' value='" + value +"' selected=''>" + value + "</option>");
            }
            selectReltype.append(optionReltype);
            // Checkbox for select type
            checkboxType = $("<INPUT>");
            checkboxType.attr("id", "checkbox");
            checkboxType.attr("type", "checkbox");
            checkboxType.css({
                "float": "left",
                "margin-top": "1%"
            });
            divTitle.append(checkboxType);
            divTitle.append(selectReltype);

            // %%%%%%%%%%%%%%%%%%%%%%
            // %%%% Box part
            // %%%%%%%%%%%%%%%%%%%%%%

            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, fieldName, field, primaries, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, handlerAnchor;
            var relationsIds = [];
            primaries = [];
            root = $("#"+ diagram.Container);
            //diagram.Counter++;
            idBox = "diagramBoxRel-" + diagram.Counter + "-" + label;
            idTopBox = "diagramTopBoxRel-" + diagram.Counter + "-" + label;
            idFields = "diagramFieldsRel-" + diagram.Counter + "-" + label;
            idAllRels = "diagramAllRelRel-" + diagram.Counter + "-" + label;
            idContainerBoxes = "diagramContainerBoxesRel-" + diagram.Counter + "-" + label;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "160px",
                "background-color": "white",
                "border": "2px solid #348E82"
                //"width": "33%"
            });
            divBox.addClass("body");
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("select-rel");
            // We append the divs
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            countFields = 0;
            // Create the select for the properties
            divField = $("<SPAN>");
            //divField.html("ole ole");
            divField = diagram.addFieldRelRow(label, idFields);
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
            addField.addClass("add-field-row-rel");
            addField.css({
                "margin-left": "2%"
            });
            addField.attr('data-parentid', idFields);
            addField.attr('data-label', label);
            // Icon
            addFieldIcon = $("<I>");
            addFieldIcon.addClass("icon-plus-sign");
            addFieldIcon.css({
                "float": "right",
                "margin-right": "4px"
            });
            addField.append(addFieldIcon);
            divAddBox = $("<DIV>");
            divAddBox.append(divFields);
            divAddBox.append(addField);
            divContainerBoxes = $("<DIV>");
            divContainerBoxes.attr("id", idContainerBoxes);
            divContainerBoxes.append(divAddBox);
            divContainerBoxes.append(divAllowedRelationships);
            divBox.append(divContainerBoxes);
            for(divField in primaries) {
                divBox.prepend(primaries[divField]);
            }
            divBox.prepend(divTitle);

            jsPlumb.draggable("diagramBoxRel-"+ diagram.Counter +"-"+ label, {
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
                        jsPlumb.repaint(["diagramBoxRel-"+ diagram.Counter +"-"+ label]);
                    });
                    diagram.saveBoxPositions();
                    jsPlumb.repaintEverything();
                }
            });

            return divBox;
        }

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
            divTitle.attr('data-modelid', model.id);
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
            //optionNodetype.attr('selected', 'selected');
            optionNodetype.html(model.name + diagram.nodetypesCounter[typeName]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++)
            {
                $($('.select-nodetype-' + typeName)[i]).append(optionNodetype.clone(true));
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.nodetypesCounter[typeName]; j++) {
                var value = model.name + j;
                selectNodetype.append("<option class='option-nodetype-" + typeName + "' id='" + value + "' data-modelid='" + model.id + "' value='" + value +"' selected=''>" + value + "</option>");
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
                } else {
                    iconToggle.removeClass('icon-plus-sign');
                    iconToggle.addClass('icon-minus-sign');
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
                jsPlumb.deleteEndpoint(idBox + "-source");
                jsPlumb.deleteEndpoint(idBox + "-target");

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
            var modelNameValue = "";
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
                            modelNameValue = models[modelName].name;
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
            return modelNameValue;
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
         * Add a new row for a field in a rel box
         * - label
         * - idFields
         */
        diagram.addFieldRelRow = function(label, idFields) {
            var model, lengthFields, fieldId, selectProperty, selectLookup, field, datatype, optionProperty, inputLookup, divField, divAndOr, selectAndOr, removeField, removeFieldIcon, checkboxProperty;
            var fields = diagram.fieldsForRels[label];
            lengthFields = fields.length;
            diagram.fieldRelsCounter++;
            fieldId = "field-" + diagram.fieldRelsCounter + "-" + label;
            // Select property
            selectProperty = $("<SELECT>");
            selectProperty.addClass("select-property");
            selectProperty.css({
                "width": "70px",
                "padding": "0",
                "margin-left": "2%",
                "display": "inline"
            });
            selectProperty.attr('data-fieldid', fieldId)
            // Select lookup
            selectLookup = $("<SELECT>");
            selectLookup.addClass("select-lookup");
            selectLookup.css({
                "width": "62px",
                "padding": "0",
                "display": "inline",
                "margin-left": "10%"
            });
            // We get the values for the properties select and the values
            // for the lookups option in relation with the datatype
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = fields[fieldIndex];
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
            if ($('#' + idFields).children().length > 0) {
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
                removeField.addClass("remove-field-row-rel");
                removeField.attr('data-fieldid', fieldId);
                removeField.attr('data-parentid', idFields);
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
         * - anchor
         */
         diagram.getRelationshipOptions = function(type, label, anchor) {
            var relationshipOptions = null;

            if(type == 'source') {
                relationshipOptions = { endpoint: ["Dot", {radius: 7}],
                                anchor: "BottomCenter",
                                isSource: true,
                                connectorStyle: {
                                    strokeStyle: '#AEAA78',
                                    lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", {
                                        width:10,
                                        length:10,
                                        location:1,
                                        id:"arrow"}],
                                    /*[ "Label", {
                                        location:0.5,
                                        label:label,
                                        id:"label",
                                        cssClass:"connection"}],*/
                                    ["Custom", {
                                        create:function(component) {
                                                            return diagram.addRelationBox(label);
                                                        },
                                        location:0.5,
                                        id:"customOverlay"
                                    }]
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
                                connectorStyle: {
                                    strokeStyle: '#AEAA78',
                                    lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", {
                                        width:10,
                                        length:10,
                                        location:1,
                                        id:"arrow"}]
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
        var modelName = diagram.loadBox(nodeType);

        // The next lines is to select the new alias in the box
        var elem = $('.select-nodetype-' + nodeType + ' #' + modelName + (diagram.nodetypesCounter[nodeType] + 1 - 1)).length - 1;
        $($('.select-nodetype-' + nodeType + ' #' + modelName + (diagram.nodetypesCounter[nodeType] + 1 - 1))[elem]).attr('selected', 'selected');
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

        jsPlumb.repaintEverything();
    });

    /**
     * Add field row inside a rel type
     */
    $("#diagramContainer").on('click', '.add-field-row-rel', function() {
        var $this = $(this);
        var label = $this.data("label");
        var parentId = $this.data("parentid");

        divField = diagram.addFieldRelRow(label, parentId);

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
     * Remove field row inside a box type
     */
    $("#diagramContainer").on('click', '.remove-field-row-rel', function() {
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
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.css({
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookup.timepicker();
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
            inputLookup.addClass("lookup-value time");
            inputLookup.css({
                "width": "35px",
                "margin-left": "5%",
                "margin-top": "3%"
            });
            inputLookup.timepicker();
            $('#' + fieldId).append(inputLookup);
        } else if(datatype == 'e') {
            // Users select
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var select = $("<INPUT>");
            //select.addClass("lookup-value chosen-select");
            //select.attr("data-placeholder", "choose a value...");
            select.addClass("lookup-value autocomplete");
            select.css({
                "width": "75px",
                "margin-left": "5%",
                "margin-top": "3%"
            });

            $('#' + fieldId).append(select);
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
            $(".autocomplete").autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "http://localhost:8000/operators/jj/query/collaborators/",
                        data: { term: request.term },
                        success: function (data) {
                            var elements = JSON.parse(data);
                            var transformed = $.each(elements, function(index, elem) {
                                return elem.value ;
                            });
                            response(transformed);
                        },
                        error: function () {
                            response([]);
                        }
                    });
                }
            });
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
        var label = $this.data("label");
        var source = $this.data("source");

        if(source) {
            var uuidSource = parentId + "-source";
            if(!jsPlumb.getEndpoint(uuidSource)) {
                var endpointSource = jsPlumb.addEndpoint(parentId, { uuid:uuidSource, connector: "Flowchart"}, diagram.getRelationshipOptions('source', label, 0.5));
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
        var elements = $('option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var type = "relationship";
            // We check the type of the origin
            if($(element).attr("class").indexOf("nodetype") >= 0)
                type = "node";

            var origin = "{'alias': \'" + $(element).val() + "\'," + " 'type': " + "\'" + type + "\'" + "," + " 'type_id': " + $(element).data('modelid') + '},';
            origins = origins + origin;
        });
        origins = origins + '],';
        result = result + origins + '\n';

        // Patterns
        var patterns = "'patterns': [";
        // This is the way to get the connections in early versions
        //var elements = jsPlumb.getAllConnections().jsPlumb_DefaultScope;
        // This is the way to get the connections in the actual version
        var elements = jsPlumb.getAllConnections();
        var ways = "";
        $.each(elements, function(index, element) {
            // We get the source and the target of the relation
            var sourceId = element.sourceId;
            var targetId = element.targetId;

            // We get the selectors for every component to build
            // the json correctly
            var relation = "{'relation': {},";

            var sourceSelector = $('#' + sourceId + ' .title');
            var sourceAlias = sourceSelector.data('boxalias');
            var sourceModelId = sourceSelector.data('modelid');
            var source = "'source': {";
            source = source + "'alias': \'" + sourceAlias + "\'," + " 'type': 'node'," + " 'type_id': " + sourceModelId + '},';

            var targetSelector = $('#' + targetId + ' .title');
            var targetAlias = targetSelector.data('boxalias');
            var targetModelId = targetSelector.data('modelid');
            var target = "'target': {";
            target = target + "'alias': \'" + targetAlias + "\'," + " 'type': 'node'," + " 'type_id': " + targetModelId + '}';
            ways = ways + relation + source + target + '},';
        });
        //ways = ways + ;
        patterns = patterns + ways + '],';
        result = result + patterns + '\n';

        // Result
        var results = "'results': [";
        var elements = $('option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var properties = propertiesChecked[element.value];
            var value = "{'alias': \'" + $(element).val() + "\'," + " 'properties': [";
            if(properties) {
                $.each(properties, function(index, property) {
                    var val = "\'" + property + "\'";
                    value = value + val;
                });
            }
            results = results + value  + ']},';
        });
        results = results + ']';
        result = result + results + '}';

        console.log(result);
    });

    $(document).ready(init);
})(jQuery);
