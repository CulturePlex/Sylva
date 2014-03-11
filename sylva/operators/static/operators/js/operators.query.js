/* Adapted from https://github.com/versae/qbe */

// Django i18n.
var gettext = window.gettext || String;

if (!diagram) {
    var diagram = {};
}

diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.Counter = 0;
diagram.CounterRels = 0;
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
    diagram.stringValues['nv'],
    diagram.stringValues['c'],
    diagram.stringValues['nc'],
    diagram.stringValues['s'],
    diagram.stringValues['en']
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
    'u': diagram.lookupsAllValues,
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
            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, divAllRel, fieldName, field, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, handlerAnchor, wildcardIndex;
            wildcardIndex = 0;
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

            if(typeName != "wildcard") {
                var relationsLength = model.relations.length;
                for(var i = 0; i < relationsLength; i++) {
                    var relation = model.relations[i];

                    // We only add the relations when the field is the source
                    if(modelName == relation.source) {
                        var label = relation.label;
                        //var name = relation.name;
                        var name = relation.label;
                        var relationId = idBox;

                        divAllRel = $("<DIV>");
                        divAllRel.addClass("div-list-rel");
                        divAllRel.css({
                            "display": "table-row"
                        });
                        divAllRel.attr("id", idBox);

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
                        diagram.setLabel(listRelElement, name);
                        //listRelElement.html(name);

                        // Link to add the relations
                        addRelation = $("<A>");
                        addRelation.addClass("add-relation");
                        addRelation.attr('data-parentid', idBox);
                        addRelation.attr('data-relsid', idAllRels);
                        addRelation.attr('data-relindex', (i + 1));
                        addRelation.attr('data-label', label);
                        addRelation.attr('data-idrel', relation.id);
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

                        wildcardIndex++;
                    }
                }
            }

            // Wildcard relationship
            divAllRel = $("<DIV>");
            divAllRel.addClass("div-list-rel");
            divAllRel.css({
                "display": "table-row"
            });
            divAllRel.attr("id", idBox);

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
            diagram.setLabel(listRelElement, "wildcard");

            // Link to add the relations
            addRelation = $("<A>");
            addRelation.addClass("add-relation");
            addRelation.attr('data-parentid', idBox);
            addRelation.attr('data-relsid', idAllRels);
            addRelation.attr('data-relindex', (wildcardIndex + 1));
            addRelation.attr('data-label', "wildcard");
            addRelation.attr('data-idrel', -1);
            diagram.fieldsForRels["wildcard"] = [];
            addRelation.attr("data-source", "wildcard");

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
            removeRelation.attr('data-label', "wildcard");

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

            divAllowedRelationships = $("<DIV>");
            divAllowedRelationships.attr("id", idAllRels);
            divAllowedRelationships.append(boxAllRel);
            // We append the divs
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            countFields = 0;

            if(typeName != "wildcard") {
                divTitle = diagram.addTitleDiv(graphName, model, typeName, modelName, idTopBox, idBox);
            } else {
                divTitle = diagram.addWildcardTitleDiv(graphName, model, typeName, typeName, idTopBox, idBox);
            }
            // Create the select for the properties
            var boxalias = divTitle.data('boxalias');
            divField = diagram.addFieldRow(graphName, modelName, idFields, typeName, boxalias, idBox, idAllRels);
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
            addField.attr("data-typename", typeName);
            addField.attr("data-boxalias", boxalias);
            addField.attr("data-idbox", idBox);
            addField.attr("data-idallrels", idAllRels);
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
                    diagram.saveBoxPositions();
                    jsPlumb.repaintEverything();
                }
            });
        };

        /**
         * Add a box for the relation. In this case, we implement
         * the title part and the main box part in the same
         * function
         * - label
         * - idRel
         */
        diagram.addRelationBox = function(label, idRel) {
            var divTitle, selectReltype, optionReltype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete;

            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, fieldName, field, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, handlerAnchor;

            /*
             *  Title part
            */

            if(diagram.reltypesCounter[label] >= 0) {
                diagram.reltypesCounter[label]++;
            } else {
                diagram.reltypesCounter[label] = 0;
            }

            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.css({
                "padding-bottom": "3%",
                "background-color": "#AEAA78"
            });
            divTitle.attr("data-modelid", idRel);
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
            optionReltype.attr('data-modelid', idRel);
            optionReltype.html(label + diagram.reltypesCounter[label]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.reltypesCounter[label]; i++)
            {
                $($('.select-reltype-' + label)[i]).append(optionReltype.clone(true));
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.reltypesCounter[label]; j++) {
                var value = label + j;
                selectReltype.append("<option class='option-reltype-" + label + "' id='" + value + "' value='" + value +"' data-modelid='" + idRel + "' selected=''>" + value + "</option>");
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

            /*
             *  Box part
            */

            root = $("#"+ diagram.Container);
            idBox = "diagramBoxRel-" + diagram.CounterRels + "-" + label;
            idTopBox = "diagramTopBoxRel-" + diagram.CounterRels + "-" + label;
            idFields = "diagramFieldsRel-" + diagram.CounterRels + "-" + label;
            idAllRels = "diagramAllRelRel-" + diagram.CounterRels + "-" + label;
            idContainerBoxes = "diagramContainerBoxesRel-" + diagram.CounterRels + "-" + label;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "160px",
                "background-color": "white",
                "border": "2px solid #AEAA78"
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
            if(diagram.fieldsForRels[label].length > 0) {
                // Create the select for the properties
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
                // We check if there are fields for add more
                if(divFields.children() > 0) {
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
                        "margin-right": "4px",
                        "color": "#AEAA78"
                    });
                    addField.append(addFieldIcon);
                }
            }
            divAddBox = $("<DIV>");
            divAddBox.append(divFields);
            divAddBox.append(addField);
            divContainerBoxes = $("<DIV>");
            divContainerBoxes.attr("id", idContainerBoxes);
            divContainerBoxes.append(divAddBox);
            divContainerBoxes.append(divAllowedRelationships);

            divBox.append(divContainerBoxes);
            divBox.prepend(divTitle);

            jsPlumb.draggable("diagramBoxRel-"+ diagram.CounterRels +"-"+ label, {
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
                        jsPlumb.repaint(["diagramBoxRel-"+ diagram.CounterRels +"-"+ label]);
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
         */
        diagram.addTitleDiv = function(graphName, model, typeName, modelName, idTopBox, idBox) {
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
         * Set all the neccesary to create the title div for the wildcard
         * type
         * - graphName
         * - model
         * - typeName
         * - modelName
         * - idTopBox
         * - idBox
         */
        diagram.addWildcardTitleDiv = function(graphName, model, typeName, modelName, idTopBox, idBox) {
            var divTitle, selectNodetype, optionNodetype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete, typeId;
            typeId = -1;
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.attr('data-modelid', typeId);
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
            optionNodetype.attr('id', modelName + diagram.nodetypesCounter[typeName]);
            optionNodetype.attr('data-modelid', typeId);
            optionNodetype.attr('value', modelName + diagram.nodetypesCounter[typeName]);
            optionNodetype.html(modelName + diagram.nodetypesCounter[typeName]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++)
            {
                $($('.select-nodetype-' + typeName)[i]).append(optionNodetype.clone(true));
            }
            // This for loop is to include the old options in the new box
            for(var j = 0; j < diagram.nodetypesCounter[typeName]; j++) {
                var value = modelName + j;
                selectNodetype.append("<option class='option-nodetype-" + typeName + "' id='" + value + "' data-modelid='" + typeId + "' value='" + value +"' selected=''>" + value + "</option>");
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
            diagram.setName(divTitle, modelName);
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

            divTitle.attr("data-boxalias", modelName + diagram.nodetypesCounter[typeName]);

            return divTitle;
        }

        /**
         * Set the label fo the fields getting shorter and adding ellipsis
         */
        diagram.setLabel = function (div, label) {
            div.html(label);
            if (label.length > 5) {
                div.html(label.substr(0, 5) +"…");
            }
            div.attr("title", label);
            div.attr("alt", label);

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
                        if(modelName.localeCompare(typeName) == 0) {
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
                    if(typeName == "wildcard") {
                        // Node type counter for the node type select field
                        if(diagram.nodetypesCounter[typeName] >= 0) {
                            diagram.nodetypesCounter[typeName]++;
                        } else {
                            diagram.nodetypesCounter[typeName] = 0;
                        }

                        diagram.addBox(graph, typeName, typeName);
                        modelNameValue = "wildcard";
                    }
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
         * - idBox
         * - idAllRels
         */
        diagram.addFieldRow = function(graphName, modelName, parentId, typeName, boxalias, idBox, idAllRels) {
            var model, lengthFields, fieldId, selectProperty, selectLookup, field, datatype, optionProperty, inputLookup, divField, divAndOr, selectAndOr, removeField, removeFieldIcon, checkboxProperty;
            model = diagram.Models[graphName][modelName];
            if(typeName != "wildcard") {
                lengthFields = model.fields.length;
            } else {
                lengthFields = 0;
            }
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
                removeField.attr('data-idbox', idBox);
                removeField.attr('data-idallrels', idAllRels);
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
            divField = $("<DIV>");
            divField.addClass("field");
            divField.css({
                "display": "inline-table",
                "margin-top": "4%"
            });
            divField.attr('id', fieldId);
            // We check if there are fields
            if(lengthFields > 0) {
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
                        "float": "right",
                        "color": "#AEAA78"
                    });
                    removeField.append(removeFieldIcon);
                    divField.append(removeField);
                }

                // We append the patterns
                divField.append(checkboxProperty);
                divField.append(selectProperty);
                divField.append(selectLookup);
            }

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
         diagram.calculateAnchor = function(parentId, relsId, relIndex) {
            var proportion = ($('#' + parentId).height() - $('#' + relsId).height()) / $('#' + parentId).height();
            var offset = relIndex * 10;

            if(relIndex > 1) {
                offset = (relIndex * 10) + ((relIndex - 1) * 15);
            }
            var result = (offset/$('#' + parentId).height()) + proportion;

            return result;
         };

        /**
         * Returns the options of a relationship
         * - type
         * - label
         * - idRel
         * - anchor
         */
         diagram.getRelationshipOptions = function(type, label, idRel, anchor) {
            var relationshipOptions = null;

            if(type == 'source') {
                relationshipOptions = { endpoint: ["Dot", {radius: 7}],
                                anchor: [1, anchor, -1, 0],
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
                                    [ "Label", {
                                        label:label,
                                        id:"label"}],
                                    ["Custom", {
                                        create:function(component) {
                                                            //return "<div id=" + "diagramBoxRel-" + diagram.Counter + "-" + label + "></div>"
                                                            return diagram.addRelationBox(label, idRel);
                                                        },
                                        location:0.5,
                                        id:"diagramBoxRel-" + diagram.CounterRels + "-" + label
                                    }]
                                ],
                                paintStyle: {
                                    strokeStyle: '#AEAA78'
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: '#AEAA78',
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
                                    strokeStyle: '#AEAA78'
                                },
                                backgroundPaintStyle: {
                                    strokeStyle: '#AEAA78',
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
        var typeName = $this.data("typename");
        var boxalias = $this.data("boxalias");
        var idBox = $this.data("idbox");
        var idAllRels = $this.data("idallrels");

        divField = diagram.addFieldRow(graphName, modelName, parentId, typeName, boxalias, idBox, idAllRels);

        $("#" + parentId).append(divField);

        // Recalculate anchor if we have source endpoints already
        if(jsPlumb.getEndpoints(idBox).length > 1) {
            var endpoint = jsPlumb.getEndpoints(idBox)[1];
            var anchor = diagram.calculateAnchor(idBox, idAllRels, endpoint.relIndex);
            endpoint.anchor.y = anchor;
        }

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
        var idBox = $this.data("idbox");
        var idAllRels = $this.data("idallrels");

        // We check that the field box need to have one
        // field row at least
        if($('#' + parentId).children().length > 1) {
            $("#" + fieldId).remove();
        } else {
            alert("You need a field at least");
        }

        // Recalculate anchor if we have source endpoints already
        if(jsPlumb.getEndpoints(idBox).length > 1) {
            var endpoint = jsPlumb.getEndpoints(idBox)[1];
            var anchor = diagram.calculateAnchor(idBox, idAllRels, endpoint.relIndex);
            endpoint.anchor.y = anchor;
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
                        url: diagram.url_collaborators,
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
        var relsId = $this.data("relsid");
        var relIndex = $this.data("relindex");
        var label = $this.data("label");
        var idRel = $this.data("idrel");
        var source = $this.data("source");

        // calculate anchor
        // We need idBox and idAllRels
        var anchor = diagram.calculateAnchor(parentId, relsId, relIndex);

        if(source) {
            var uuidSource = parentId + "-source";
            if(!jsPlumb.getEndpoint(uuidSource)) {
                var endpointSource = jsPlumb.addEndpoint(parentId, { uuid:uuidSource, connector: "Flowchart"}, diagram.getRelationshipOptions('source', label, idRel, anchor));
                endpointSource.relIndex = relIndex;
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

     jsPlumb.bind("connection", function(info) {
        var sourceIdValue = info.sourceId;
        var targetIdValue = info.targetId;

        var idBoxRel = info.connection.getOverlays()[2].id;
        var labelRel = info.connection.getOverlays()[1].label;
        //$('#' + idBoxRel).attr("data-idrel", idBoxRel);
        info.connection.idrel = idBoxRel;

        var elem = $('.select-reltype-' + labelRel + ' #' + labelRel + (diagram.reltypesCounter[labelRel] + 1 - 1)).length - 1;
        $($('.select-reltype-' + labelRel + ' #' + labelRel + (diagram.reltypesCounter[labelRel] + 1 - 1))[elem]).attr('selected', 'selected');

        diagram.CounterRels++;

     });

    /**
     * Handler for create the JSON file
     */
    $(document).on('click', '#run-button', function() {
        var query = {};
        var propertiesChecked = {};
        // Conditions

        var conditionsArray = new Array();
        var properties = $('.select-property');
        $.each(properties, function(index, property) {
            var conditionArray = new Array();
            var lookup = $(property).next().val();
            var propertyTag = "property";
            var alias = $(property).data('boxalias');
            var propertyName = $(property).val();
            var propertyValue = $(property).next().next().val();

            // We store the checked properties
            propertiesChecked[alias] = new Array();
            if($(property).prev().attr('checked')) {
                propertiesChecked[alias].push($(property).val());
            }

            if(lookup) {
                var propertyArray = new Array();
                propertyArray.push(propertyTag);
                propertyArray.push(alias);
                propertyArray.push(propertyName);

                conditionArray.push(lookup);
                conditionArray.push(propertyArray);
                conditionArray.push(propertyValue);

                conditionsArray.push(conditionArray);
            }
        });
        query["conditions"] = conditionsArray;

        // Origin
        var originsArray = new Array();
        var elements = $('option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var origin = {};
            var type = "relationship";
            // We check the type of the origin
            if($(element).attr("class").indexOf("nodetype") >= 0)
                type = "node";
            var alias = $(element).val();
            var type_id = $(element).data('modelid');
            origin.alias = alias;
            origin.type = type;
            origin.type_id = type_id;
            originsArray.push(origin);
        });
        query["origins"] = originsArray;

        // Patterns
        var patternsArray = new Array();
        // This is the way to get the connections in early versions
        // var elements = jsPlumb.getAllConnections().jsPlumb_DefaultScope;
        // This is the way to get the connections in the actual version
        var elements = jsPlumb.getAllConnections();
        $.each(elements, function(index, element) {
            var pattern = {};
            var relation = {};
            var source = {};
            var target = {};
            // We get the id for the relation div
            var relationId = element.idrel;

            // We get the source and the target of the relation
            var sourceId = element.sourceId;
            var targetId = element.targetId;

            // We get the selectors for every component to build
            // the json correctly
            var relationSelector = $('#' + relationId + ' .title');
            var relationAlias = $('#' + relationId + ' .title select').val();
            var relationModelId = relationSelector.data('modelid');
            relation.alias = relationAlias;
            relation.type = 'relationship';
            relation.type_id = relationModelId;

            var sourceSelector = $('#' + sourceId + ' .title');
            var sourceAlias = sourceSelector.data('boxalias');
            var sourceModelId = sourceSelector.data('modelid');
            source.alias = sourceAlias;
            source.type = 'node';
            source.type_id = sourceModelId;

            var targetSelector = $('#' + targetId + ' .title');
            var targetAlias = targetSelector.data('boxalias');
            var targetModelId = targetSelector.data('modelid');
            target.alias = targetAlias;
            target.type = 'node';
            target.type_id = targetModelId;

            pattern.relation = relation;
            pattern.source = source;
            pattern.target = target;

            patternsArray.push(pattern);
        });
        query["patterns"] = patternsArray;

        // Result
        var resultsArray = new Array();
        var elements = $('option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var result = {};
            var alias = $(element).val();
            var properties = propertiesChecked[element.value];

            if(!properties)
                properties = new Array();

            result.alias = alias;
            result.properties = properties;

            resultsArray.push(result);
        });
        query["results"] = resultsArray;
        console.log("query: ");
        console.log(query);

        var queryJson = JSON.stringify(query);

        $.ajax({
            type: "POST",
            url: diagram.url_query,
            data: {"query": queryJson},
            success: function (data) {
                if(data.length > 0) {
                    $("#results").html("");
                    var table = $("<TABLE>");
                    for (var i = 0, j = data.length; i < j; i += 1) {
                        var row = $("<TR>");
                        for (var k = 0, l = data[i].length; k < l; k += 1) {
                            var cell = $("<TD>");
                            cell.text(data[i][k]);
                            row.append(cell);
                        }
                        table.append(row);
                    }
                    $("#results").append(table);
                    $("#results").css({
                        "border": "1px solid #348E82",
                        "padding": "1em",
                        "margin-top": "50px",
                        "margin-left": "25px",
                        "display": "none"
                    });
                    $('#builder-results h2').css({
                        "color": "#0000FF"
                    });
                } else {
                    $("#results").css({
                            "border": "1px solid #348E82",
                            "padding": "1em",
                            "margin-top": "50px",
                            "margin-left": "25px",
                            "display": "none"
                    });
                    $("#results").html("No results found");
                    $('#builder-results h2').css({
                        "color": "#FF0000"
                    });
                }
            },
            error: function (e) {
                $("#results").css({
                            "border": "1px solid #348E82",
                            "padding": "1em",
                            "margin-top": "50px",
                            "margin-left": "25px",
                            "display": "none"
                });
                $("#results").html("There's an error in your query. Please, fix it.");
                $('#builder-results h2').css({
                    "color": "#000000"
                });
            },
            dataType: "json"
        });
    });

    $(document).ready(init);
})(jQuery);
