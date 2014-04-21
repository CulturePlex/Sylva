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
diagram.relindex = {};

diagram.stringValues = {
    'em': "",
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

diagram.lookupsBackendValues = {
    'equals': 'eq',
    'is less than or equal to': 'lte',
    'is less than': 'lt',
    'is greater than': 'gt',
    'is greater than or equal to': 'gte',
    'is between': 'is between',
    'does not equal': 'neq',
    'has some value': 'has some value',
    'has no value': 'has no value',
    'contains': 'contains',
    "doesn't contain": "doesn't contain",
    'starts with': 'startswith',
    'ends with': 'endswith'
}

diagram.lookupsAllValues = [
    diagram.stringValues['em'],
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
    diagram.stringValues['em'],
    diagram.stringValues['e'],
    diagram.stringValues['ne'],
    diagram.stringValues['v'],
    diagram.stringValues['nv']
];

diagram.lookupsTextValues = [
    diagram.stringValues['em'],
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
            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, divAllRel, fieldName, field, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, handlerAnchor, idBoxAllRels, selectAllRel;
            model = diagram.Models[graphName][modelName];
            root = $("#"+ diagram.Container);
            diagram.Counter++;
            idBox = "diagramBox-" + diagram.Counter +"-"+ modelName;
            idTopBox = "diagramTopBox-" + diagram.Counter + "-" + modelName;
            idFields = "diagramFields-" + diagram.Counter + "-" + modelName;
            idBoxAllRels = "diagramBoxAllRels-" + diagram.Counter + "-" + modelName;
            idAllRels = "diagramAllRel-" + diagram.Counter + "-" + modelName;
            idContainerBoxes = "diagramContainerBoxes-" + diagram.Counter + "-" + modelName;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "350px"
                //"width": "245px"
                //"width": "33%"
            });
            divBox.addClass("body");
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("box-all-rel");
            boxAllRel.attr('id', idBoxAllRels);

            selectAllRel = $("<SELECT>");
            selectAllRel.addClass("select-rel");

            var relationsIds = [];
            if(typeName != "wildcard") {
                var relationsLength = model.relations.length;
                for(var i = 0; i < relationsLength; i++) {
                    var relation = model.relations[i];

                    // We only add the relations when the field is the source
                    if(modelName == relation.source) {
                        var label = relation.label;
                        var name = relation.name.replace(/-/g, "_");
                        var relationId = idBox + "-" + name;

                        var optionRel = $("<OPTION>");
                        optionRel.addClass("option-rel");
                        optionRel.attr('id', relationId);
                        optionRel.attr('value', name);
                        optionRel.attr('data-parentid', idBox);
                        optionRel.attr('data-boxrel', idBoxAllRels);
                        optionRel.attr('data-relsid', idAllRels);
                        optionRel.attr('data-relationid', relationId);
                        optionRel.attr('data-label', label);
                        optionRel.attr('data-name', name);
                        optionRel.attr('data-idrel', relation.id);
                        optionRel.attr('data-scope', relation.target);
                        optionRel.html(label);
                        diagram.fieldsForRels[name] = relation.fields;

                        if(relation.source) {
                            optionRel.attr("data-source", relation.source);
                            diagram.relindex[idBox] = 1;
                        }

                        relationsIds.push(relationId);

                        selectAllRel.append(optionRel);
                    }
                }
            }

            // Wildcard relationship
            var wildCardName = "WildcardRel";
            var wildCardRelId = idBox + "-" + "wildcard";

            // Option for the wildcard relationship
            var optionRelWildcard = $("<OPTION>");
            optionRelWildcard.addClass("option-rel");
            optionRelWildcard.attr('id', relationId);
            optionRelWildcard.attr('value', wildCardName);
            optionRelWildcard.attr('data-parentid', idBox);
            optionRelWildcard.attr('data-boxrel', idBoxAllRels);
            optionRelWildcard.attr('data-relsid', idAllRels);
            optionRelWildcard.attr('data-relationid', wildCardRelId);
            optionRelWildcard.attr('data-label', wildCardName);
            optionRelWildcard.attr('data-name', wildCardName);
            optionRelWildcard.attr('data-idrel', -1);
            optionRelWildcard.attr('data-scope', "wildcard");
            optionRelWildcard.html(wildCardName);
            diagram.fieldsForRels[wildCardName] = [];
            optionRelWildcard.attr("data-source", wildCardName);

            relationsIds.push(wildCardRelId);

            // This 'if' is to initialize the dictionary for
            // the wildcard box
            if(!diagram.relindex[idBox])
                diagram.relindex[idBox] = 1;

            selectAllRel.append(optionRelWildcard);

            // Link to add the relations
            addRelation = $("<A>");
            addRelation.addClass("add-relation");
            // Add relation icon
            addRelationIcon = $("<I>");
            addRelationIcon.addClass("icon-plus-sign");
            addRelationIcon.attr('id', 'add-relation-icon');
            addRelation.append(addRelationIcon);

            boxAllRel.append(selectAllRel);
            boxAllRel.append(addRelation);

            divAllowedRelationships = $("<DIV>");
            divAllowedRelationships.attr("id", idAllRels);
            divAllowedRelationships.append(boxAllRel);
            // We append the divs
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            divFields.css({
                "margin-top": "10px"
            });
            countFields = 0;

            if(typeName != "wildcard") {
                divTitle = diagram.addTitleDiv(graphName, model, typeName, modelName, idTopBox, idBox, idAllRels, relationsIds);
            } else {
                divTitle = diagram.addWildcardTitleDiv(graphName, model, typeName, typeName, idTopBox, idBox, idAllRels, relationsIds);
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
            addFieldIcon.attr('id', 'add-field-icon');
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

            var exampleDropOptions = {
                tolerance:"touch",
                hoverClass:"dropHover",
                activeClass:"dragActive"
            }
            var uuidTarget = idBox + "-target";
            if(!jsPlumb.getEndpoint(uuidTarget)) {
                // This offset is for centering the endpoint
                var offset = 7;
                var anchor = ($('#' + idBox).height() - $('#' + idBox + ' .title').height() + offset) / $('#' + idBox).height()
                var endpointTarget = jsPlumb.addEndpoint(idBox, { uuid:uuidTarget, connector: "Flowchart"},diagram.getRelationshipOptions('target', 0, 0, 1 - anchor));
                endpointTarget.addClass("endpoint-target");
                endpointTarget.scopeTarget = typeName;
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
                "background-color": "#AEAA78"
            });
            divTitle.attr("data-modelid", idRel);
            // Select for the type
            selectReltype = $("<SELECT>");
            selectReltype.addClass("select-reltype-" + label);
            selectReltype.css({
                "width": "65px",
                "float": "left",
                "padding": "0",
                "margin-left": "5%"
            });
            optionReltype = $("<OPTION>");
            optionReltype.addClass("option-reltype-" + label);
            optionReltype.attr('id', label + diagram.reltypesCounter[label]);
            optionReltype.attr('value', label + diagram.reltypesCounter[label]);
            optionReltype.attr('data-modelid', idRel);
            optionReltype.html(label + diagram.reltypesCounter[label]);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.reltypesCounter[label]; i++) {
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
            checkboxType.addClass("checkbox-select-type");
            checkboxType.attr("id", "checkbox");
            checkboxType.attr("type", "checkbox");
            divTitle.append(checkboxType);
            diagram.setName(divTitle, label);
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
            boxAllRel.addClass("box-all-rel");
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
                    addField.attr('data-parentid', idFields);
                    addField.attr('data-label', label);
                    // Icon
                    addFieldIcon = $("<I>");
                    addFieldIcon.addClass("icon-plus-sign");
                    addFieldIcon.attr('id', 'add-field-icon-prop')
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
         * - idAllRels
         * - relationsIds
         */
        diagram.addTitleDiv = function(graphName, model, typeName, modelName, idTopBox, idBox, idAllRels, relationsIds) {
            var divTitle, selectNodetype, optionNodetype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete;
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.attr('data-modelid', model.id);
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
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++) {
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
            checkboxType.addClass("checkbox-select-type");
            checkboxType.attr("id", "checkbox-" + idBox);
            checkboxType.attr("type", "checkbox");
            divTitle.append(checkboxType);
            diagram.setName(divTitle, model.name);
            divTitle.append(selectNodetype);
            anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ modelName);
            iconToggle = $("<I>");
            iconToggle.addClass("icon-minus-sign");
            iconToggle.attr('id', 'icon-toggle');

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
                // Recalculate anchor for source endpoints
                diagram.recalculateAnchor(idBox, idAllRels);

                jsPlumb.repaintEverything();
                diagram.saveBoxPositions();
            });
            anchorDelete = $("<A>");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.attr("id", "inlineDeleteLink_"+ modelName);
            iconDelete = $("<I>");
            iconDelete.addClass("icon-remove-sign");
            anchorDelete.append(iconDelete);
            anchorDelete.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\\."+ modelName).click();
                jsPlumb.detachAllConnections(idBox);
                for(var i = 0; i < relationsIds.length; i++)
                    jsPlumb.deleteEndpoint(relationsIds[i] + "-source");
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
         * - idAllRels
         * - relationsIds
         */
        diagram.addWildcardTitleDiv = function(graphName, model, typeName, modelName, idTopBox, idBox, idAllRels, relationsIds) {
            var divTitle, selectNodetype, optionNodetype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete, typeId;
            typeId = -1;
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.attr('data-modelid', typeId);
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
            checkboxType.addClass("checkbox-select-type");
            checkboxType.attr("id", "checkbox-" + idBox);
            checkboxType.attr("type", "checkbox");
            divTitle.append(checkboxType);
            diagram.setName(divTitle, modelName);
            divTitle.append(selectNodetype);
            anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ modelName);
            iconToggle = $("<I>");
            iconToggle.addClass("icon-minus-sign");
            iconToggle.attr('id', 'icon-toggle');
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
                diagram.recalculateAnchor(idBox, idAllRels);

                jsPlumb.repaintEverything();
                diagram.saveBoxPositions();
            });
            anchorDelete = $("<A>");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.attr("id", "inlineDeleteLink_"+ modelName);
            iconDelete = $("<I>");
            iconDelete.addClass("icon-remove-sign");
            anchorDelete.append(iconDelete);
            anchorDelete.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\\."+ modelName).click();
                jsPlumb.detachAllConnections(idBox);
                for(var i = 0; i < relationsIds.length; i++)
                    jsPlumb.deleteEndpoint(relationsIds[i] + "-source");
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
                div.html(label.substr(0, 20) +"…");
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
            diagram.fieldCounter++;
            fieldId = "field" + diagram.fieldCounter;
            if(typeName != "wildcard") {
                lengthFields = model.fields.length;
                // Select property
                selectProperty = $("<SELECT>");
                selectProperty.addClass("select-property");
                selectProperty.css({
                    "width": "80px"
                });
                selectProperty.attr('data-fieldid', fieldId)
                selectProperty.attr('data-boxalias', boxalias);

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
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
                selectLookup.css({
                    "width": "80px"
                });
            } else {
                // We add an input field to get the return value
                selectProperty = $("<INPUT>");
                selectProperty.addClass("wildCardInput select-property");
                selectProperty.attr('id', fieldId);
                selectProperty.attr('data-fieldid', fieldId);
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
                selectLookup.css({
                    "width": "80px"
                });
            }

            divField = $("<DIV>");
            divField.addClass("field");
            divField.attr('id', fieldId);
            // Checkbox for select property
            checkboxProperty = $("<INPUT>");
            checkboxProperty.addClass("checkbox-property");
            checkboxProperty.attr("type", "checkbox");
            // If we have more than 1 field row, add and-or div
            if ($('#' + parentId).children().length > 0) {
                divAndOr = $("<DIV>");
                divAndOr.addClass("and-or-option");
                divAndOr.css({
                    "margin-bottom": "5%"
                });
                selectAndOr = $("<SELECT>");
                selectAndOr.addClass("select-and-or");
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
                removeFieldIcon.attr('id', 'remove-field-icon');
                removeField.append(removeFieldIcon);
                divField.append(removeField);
            }

            if ($('#' + parentId).children().length == 0) {
                divField.css({
                    "margin-left": "-5px"
                })
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
            divField.attr('id', fieldId);
            // We check if there are fields
            if(lengthFields > 0) {
                // Select property
                selectProperty = $("<SELECT>");
                selectProperty.addClass("select-property");
                selectProperty.attr('data-fieldid', fieldId)
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
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
                checkboxProperty.addClass("checkbox-property");
                checkboxProperty.attr("type", "checkbox");
                // If we have more than 1 field row, add and-or div
                if ($('#' + idFields).children().length > 0) {
                    divAndOr = $("<DIV>");
                    divAndOr.addClass("and-or-option");
                    divAndOr.css({
                        "margin-bottom": "5%"
                    });
                    selectAndOr = $("<SELECT>");
                    selectAndOr.addClass("select-and-or");
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
                    removeFieldIcon.attr('id', 'remove-field-icon-prop');

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
            var selectRelHeight = 17;
            var proportion = (($('#' + parentId).height() + selectRelHeight) - $('#' + relsId).height()) / $('#' + parentId).height();
            // We add 17 because the select rel height
            var offset = relIndex * 10 + 20;

            if(relIndex > 1) {
                offset = (relIndex * 10) + ((relIndex - 1) * 13) + 20;
            }
            var result = (offset/$('#' + parentId).height()) + proportion;

            return result;
         };

        /**
         * Recalculate the anchor for sources endpoints
         * - idBox
         * - idAllRels
         */
         diagram.recalculateAnchor = function(idBox, idAllRels) {
            if(jsPlumb.getEndpoints(idBox).length > 1) {
                for(var i = 1; i < jsPlumb.getEndpoints(idBox).length; i++) {
                    var endpoint = jsPlumb.getEndpoints(idBox)[i];
                    var anchor = diagram.calculateAnchor(idBox, idAllRels, endpoint.relIndex);
                    endpoint.anchor.y = anchor;
                }
            }
         }

        /**
         * Recalculate the anchor for targets endpoints
         * - idBox
         */
         diagram.recalculateAnchorTarget = function(idBox) {
            var endpointTarget = jsPlumb.getEndpoints(idBox)[0];
            // This offset is for centering the endpoint
            var offset = 7;
            var anchor = ($('#' + idBox).height() - $('#' + idBox + ' .title').height() + offset) / $('#' + idBox).height();
            endpointTarget.anchor.y = 1 - anchor;
         }

         /**
          * Function to change the special characters (i.e tildes) for
          * regular characters
          * - text
          */
         diagram.replaceChars = function (text) {
            var specials = "ÃÀÁÄÂÈÉËÊÌÍÏÎÒÓÖÔÙÚÜÛãàáäâèéëêìíïîòóöôùúüûÑñÇç";
            var originals = "AAAAAEEEEIIIIOOOOUUUUaaaaaeeeeiiiioooouuuunncc";

            if(text != null) {
                for (var i=0; i<specials.length; i++) {
                    text = text.replace(specials.charAt(i), originals.charAt(i));
                }
            }

            return text;
         }


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
                relationshipOptions = { endpoint: ["Image", {
                    src: "../../../static/img/rarr2.gif",
                    cssClass:"endpoint-image"}],
                                anchor: [1, anchor, 1, 0],
                                isSource: true,
                                connectorStyle: {
                                    strokeStyle: '#AEAA78',
                                    lineWidth: 2
                                },
                                connectorOverlays:[
                                    [ "PlainArrow", {
                                        foldback: 0,
                                        width:10,
                                        length:10,
                                        location:1,
                                        id:"arrow"}],
                                    [ "Label", {
                                        label:label,
                                        id:"label"}],
                                    ["Custom", {
                                        create:function(component) {
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
                relationshipOptions = { endpoint: ["Rectangle",
                {width: 350,
                 height: 30,
                 cssClass: 'query-box-endpoint-target'}],
                                //anchor: [1, anchor, -1, 0],
                                anchor: "TopCenter",
                                isTarget: true,
                                maxConnections: 99,
                                connectorStyle: {
                                    strokeStyle: '#AEAA78',
                                    lineWidth: 2},
                                connectorOverlays:[
                                    [ "PlainArrow", {
                                        foldback: 0,
                                        width:10,
                                        length:10,
                                        location:0,
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
     * Generate the query to send to the backend
     */
    diagram.generateQuery = function() {
        var query = {};
        var propertiesChecked = {};

        // Conditions
        var conditionsArray = new Array();
        var properties = $('.select-property');
        $.each(properties, function(index, property) {
            var conditionArray = new Array();
            var lookup = $(property).next().val();
            var propertyTag = "property";
            //var alias = $(property).data('boxalias');
            // We really should think about another solution
            var parent = $(property).parent().parent().parent().parent().parent();
            var parentId = $(parent).attr('id');
            var alias = diagram.replaceChars($('#' + parentId + ' .title select').val());
            var propertyName = $(property).val();
            var propertyValue = $(property).next().next().val();

            // We store the checked properties
            if(!propertiesChecked[alias])
                propertiesChecked[alias] = new Array();
            if($(property).prev().attr('checked')) {
                propertiesChecked[alias].push($(property).val());
            }

            // We check if we have and/or option
            var andOrId = $(property).parent().attr('id');
            var andOrVal = $('#' + andOrId + ' .and-or-option select').val();

            if((lookup != "undefined") && (lookup != null)) {
                var propertyArray = new Array();
                propertyArray.push(propertyTag);
                propertyArray.push(alias);
                propertyArray.push(propertyName);

                conditionArray.push(lookup);
                conditionArray.push(propertyArray);
                conditionArray.push(propertyValue);

                if(andOrVal) {
                    conditionArray.push(andOrVal);
                } else {
                    conditionArray.push("not");
                }

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
            var alias = diagram.replaceChars($(element).val());
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
            if(relationSelector.length == 0) {
                alert("There's been an error in the relationship " + sourceId + "-" + targetId + ". Please remove it and try again");
            }
            var relationAlias = $('#' + relationId + ' .title select').val();
            var relationModelId = relationSelector.data('modelid');
            relation.alias = diagram.replaceChars(relationAlias);
            relation.type = 'relationship';
            relation.type_id = relationModelId;

            var sourceSelector = $('#' + sourceId + ' .title');
            var sourceAlias = $('#' + sourceId + ' .title select').val();
            var sourceModelId = sourceSelector.data('modelid');
            source.alias = diagram.replaceChars(sourceAlias);
            source.type = 'node';
            source.type_id = sourceModelId;

            var targetSelector = $('#' + targetId + ' .title');
            var targetAlias = $('#' + targetId + ' .title select').val();
            var targetModelId = targetSelector.data('modelid');
            target.alias = diagram.replaceChars(targetAlias);
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
            var alias = diagram.replaceChars($(element).val());
            var properties = propertiesChecked[diagram.replaceChars(element.value)];

            if(!properties)
                properties = new Array();

            result.alias = alias;
            result.properties = properties;

            resultsArray.push(result);
        });
        query["results"] = resultsArray;

        return query;
    };

    /**
     * Load the query
     */
    diagram.loadQuery = function(jsonQuery) {
        jsonDict = JSON.parse(jsonQuery);
        types = jsonDict["aliases"];
        nodetypes = {};
        origins = jsonDict["query"]["origins"];
        originsLength = origins.length;
        conditions = jsonDict["query"]["conditions"];
        conditionsLength = conditions.length;
        patterns = jsonDict["query"]["patterns"];
        patternsLength = patterns.length;
        results = jsonDict["query"]["results"];
        resultsLength = results.length;
        var resultsArray = {};
        var fieldIndex = 0;
        // We save the results to return
        for(key in types) {
            for(var i = 0; i < resultsLength; i++) {
                if(results[i].alias == key) {
                    resultsArray[key] = results[i].properties;
                }
            }
        }
        // We save the node types to load the boxes
        for(var i = 0; i < originsLength; i++) {
            if(origins[i].type == "node") {
                nodeAlias = origins[i].alias;
                nodetypes[nodeAlias] = types[nodeAlias];
            }
        }
        // Load the boxes for nodetypes
        for(key in nodetypes) {
            id = nodetypes[key].id;
            typename = nodetypes[key].typename;
            leftPos = nodetypes[key].left;
            topPos = nodetypes[key].top;
            // Load the box and set the positions
            diagram.loadBox(typename);
            $('#' + id).css({
                "left": leftPos,
                "top": topPos
            });
            // Load the conditions for the box
            // This loop could be replace if we have a
            // dict instead an array
            // ---------------------------------------
            // Every index in the loop is an index for a field
            fieldIndex++;
            var boxFields = 0;
            for(var i = 0; i < conditionsLength; i++) {
                alias = conditions[i][1][1];
                // We check if the condition is for the type
                if(alias == key) {
                    boxFields++;
                    // If we have more than one field, we add
                    // a new field
                    if(boxFields > 1) {
                        $('#' + id + ' .add-field-row').click();
                        fieldIndex++;
                    }
                    // lookup
                    lookup = jsonDict["query"]["conditions"][i][0];
                    // property
                    property = jsonDict["query"]["conditions"][i][1][2];
                    // value
                    value = jsonDict["query"]["conditions"][i][2];
                    // We have to check the and-or value
                    andOr = jsonDict["query"]["conditions"][i][3];
                    // We set the values in the correct position
                    //$field = $('#' + id + " #field" + (i+1));
                    $('#' + id + " #field" + fieldIndex + " .select-property").click();
                    $('#' + id + " #field" + fieldIndex + " .select-property").val(property);
                    $('#' + id + " #field" + fieldIndex + " .select-lookup").click();
                    $('#' + id + " #field" + fieldIndex + " .select-lookup").val(lookup);
                    $('#' + id + " #field" + fieldIndex + " .lookup-value").val(value);
                    if(andOr != "not") {
                        $('#' + id + " #field" + fieldIndex + " .select-and-or").val(andOr);
                    }
                    // We check if the field has results to return
                    if(resultsArray[key].indexOf(property) != -1) {
                        $('#' + id + " #field" + fieldIndex + ' .checkbox-property').click();
                    }
                }
            }
            // We select the correct value for the alias
            $('#' + id + ' .title select').val(key);
        }
        // Load the relationships between the boxes
        for(var i = 0; i < patternsLength; i++) {
            var source = jsonDict["query"]["patterns"][i].source.alias;
            var sourceId = types[source].id;

            var target = jsonDict["query"]["patterns"][i].target.alias;
            var targetId = types[target].id;

            var relation = jsonDict["query"]["patterns"][i].relation.alias;
            var relationValue = types[relation].typename;
            var relationName = relationValue;

            // We check if the relationship is of type wildcard
            if(relationValue == "wildcard")
               relationValue = "WildcardRel";

            var uuidSource = sourceId + '-' + relationName + '-source';
            console.log(uuidSource);
            var uuidTarget = targetId + '-target';
            console.log(uuidTarget);

            $('#' + sourceId + ' .select-rel').val(relationValue);
            $('#' + sourceId + ' .add-relation').click();

            jsPlumb.connect({uuids: [uuidSource, uuidTarget] })
        }

        jsPlumb.repaintEverything();
    }

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

        // Recalculate anchor for source endpoints
        diagram.recalculateAnchor(idBox, idAllRels);

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
        // Recalculate anchor for source endpoints
        diagram.recalculateAnchor(idBox, idAllRels);

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
        }
    });

    /**
     * Add a new relationship row for that box type
     */
    $("#diagramContainer").on('click', '.add-relation', function() {
        var $this = $(this);
        // We gonna select the select field
        var parent = $this.parent();
        var parentId = parent.attr("id");
        var selectField = $('#' + parentId + " .select-rel");

        var idBox = $('option:selected', selectField).data("parentid");
        var boxrel = $('option:selected', selectField).data("boxrel");
        var idAllRels = $('option:selected', selectField).data("relsid");
        var relationId = $('option:selected', selectField).data("relationid");
        var label = $('option:selected', selectField).data("label");
        var name = $('option:selected', selectField).data("name");
        var idrel = $('option:selected', selectField).data("idrel");
        var source = $('option:selected', selectField).data("source");
        var scopeSource = $('option:selected', selectField).data("scope");

        // If exists a relationship with that id, we dont add the
        // relationship

        if($('#div-' + relationId).length == 0) {

            divAllRel = $("<DIV>");
            divAllRel.addClass("div-list-rel");
            divAllRel.attr("id", "div-" + relationId);

            listRelElement = $("<LI>");
            listRelElement.addClass("list-rel");

            diagram.setLabel(listRelElement, label);
            //listRelElement.html(label);

            if(source) {
                var relIndex = diagram.relindex[idBox];
                // calculate anchor
                // We need idBox and idAllRels
                var anchor = diagram.calculateAnchor(idBox, idAllRels, relIndex);
                if(source) {
                    var uuidSource = relationId + "-source";
                    if(!jsPlumb.getEndpoint(uuidSource)) {
                        var endpointSource = jsPlumb.addEndpoint(idBox, { uuid:uuidSource, connector: "Flowchart"}, diagram.getRelationshipOptions('source', name, idrel, anchor));
                        endpointSource.relIndex = relIndex;
                        endpointSource.scopeSource = scopeSource;
                    }
                }
                diagram.relindex[idBox]++;
            }

            // Link to remove the relations
            removeRelation = $("<A>");
            removeRelation.addClass("remove-relation");
            removeRelation.attr('data-parentid', relationId);
            removeRelation.attr('data-idbox', idBox);
            removeRelation.attr('data-relsid', idAllRels);
            removeRelation.attr('data-divrelid', "div-" + relationId);
            removeRelation.attr('data-label', label);

            // Remove relation icon
            removeRelationIcon = $("<I>");
            removeRelationIcon.addClass("icon-minus-sign");
            removeRelationIcon.attr('id', 'remove-relation-icon');
            removeRelation.append(removeRelationIcon);

            // Help text for drag relationship
            var helpText = $("<SPAN>");
            helpText.addClass("help-text");
            helpText.css({
                "font-style": "italic"
            });

            divAllRel.append(listRelElement);
            divAllRel.append(removeRelation);

            $('#' + boxrel).append(divAllRel);
        }
        // Recalculate anchor for source endpoints
        diagram.recalculateAnchor(idBox, idAllRels);
        // Recalculate anchor for target endpoints
        //diagram.recalculateAnchorTarget(idBox);

        $('.endpoint-image').attr("title", "drag me!")

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

        // This if is for check if the select-property is for a wildcard input
        if(!arrayOptions) {
            datatype = 'u';
            arrayOptions = diagram.lookupOptions(datatype);
        }

        for (var i = 0; i < arrayOptions.length; i++) {
            var value = diagram.lookupsBackendValues[arrayOptions[i]];
            $(selector).append('<option class="lookup-option" value="' + value + '">' + arrayOptions[i] + '</option>');
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
                "width": "60px",
                "display": "inline",
                "margin-left": "8px",
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
                "width": "60px",
                "display": "inline",
                "margin-left": "8px",
                "padding": 0
            });
            select.append('<option class="lookup-value" value=""></option>');
            for(var j = 3; j < choicesArray.length; j = j + 2) {
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
                "width": "60px",
                "margin-left": "8px"
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
                "width": "60px",
                "margin-left": "8px"
            });
            inputLookup.timepicker();
            $('#' + fieldId).append(inputLookup);
        } else if(datatype == 'd') {
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
                "width": "60px",
                "margin-left": "8px"
            });
            var options = {
                appendText: "(yyyy-mm-dd)",
                gotoCurrent: true,
                dateFormat: 'yy-mm-dd',
                changeYear: true,
                yearRange: "-3000:3000"
            };
            inputLookup.datepicker(options);
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
            select.addClass("lookup-value autocomplete");
            select.css({
                "width": "60px",
                "margin-left": "8px"
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
                "width": "60px",
                "margin-left": "8px"
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
        var condition = datatype != 'd'
                        && datatype != 'b'
                        && datatype != 'c'
                        && datatype != 'w'
                        && datatype != 'a'
                        && datatype != 'e';
        if(condition) {
            if(value == "is between") {
                // two inputs - we check if we have introduced an input field
                var inputValueFirst = $this.next().val();
                var inputValueSecond = $this.next().next().val();
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input style=\"width: 35px; margin-left: 5%; margin-top:3%;\" />");
                $this.after("<input style=\"width: 35px; margin-left: 5%; margin-top:3%;\" />");
                // We keep the value of the inputs
                if(inputValueFirst) {
                    $this.next().val(inputValueFirst);
                } else if(inputValueSecond) {
                    $this.next().next().val(inputValueSecond);
                }
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
                var inputValue = $this.next().val();
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input style=\"width: 60px; margin-left: 8px;\" />");
                // We keep the value of the input
                if(inputValue) {
                    $this.next().val(inputValue);
                }
            }
        } else {
            // In this branch, the type would be boolean, choices, date or user
        }
    });

    /**
     * Add the handler to remove the wire
     */
     $("#diagramContainer").on('click', '.remove-relation', function() {
        var $this = $(this);
        var patternId = $this.data("parentid");
        var idBox = $this.data("idbox");
        var idAllRels = $this.data("relsid");
        var divRelId = $this.data("divrelid");
        var label = $this.data("label");

        diagram.relindex[idBox]--;

        var oldEndpointRelIndex = jsPlumb.getEndpoint(patternId + '-source').relIndex;
        jsPlumb.deleteEndpoint(patternId + '-source');
        $('#' + divRelId).remove();

        // Recalculate anchor if we have source endpoints already
        if(jsPlumb.getEndpoints(idBox).length > 1) {
            // We start at index 1 because the index 0 si the target
            var endpointsLength = jsPlumb.getEndpoints(idBox).length;
            for(var i = 1; i < endpointsLength; i++) {
                var endpoint = jsPlumb.getEndpoints(idBox)[i];
                var anchor = 0;
                // This is for the case that we have removed some
                // element and need to update the rel index.
                // The substract operation is because we have an endpoint
                // extra: The target endpoint
                if(endpoint.relIndex > oldEndpointRelIndex) {
                    var newRelIndex = endpoint.relIndex - 1;
                    anchor = diagram.calculateAnchor(idBox, idAllRels, newRelIndex);
                    endpoint.relIndex = newRelIndex;

                } else {
                    anchor = diagram.calculateAnchor(idBox, idAllRels, endpoint.relIndex);
                }
                endpoint.anchor.y = anchor;
            }
        }

        // Recalculate anchor for target endpoints
        //diagram.recalculateAnchorTarget(idBox);

        jsPlumb.repaintEverything();
     });

    /**
     * Bind methods for control jsPlumb events
     */

     jsPlumb.bind("connection", function(info) {
        var scopeSource = info.sourceEndpoint.scopeSource;
        var scopeTarget = info.targetEndpoint.scopeTarget;

        var compare = scopeSource != scopeTarget;
        var compareWildcard = (scopeSource == "wildcard") ||
                                (scopeTarget == "wildcard");

        if(!compare || compareWildcard) {
            var sourceIdValue = info.sourceId;
            var targetIdValue = info.targetId;

            var idBoxRel = info.connection.getOverlays()[2].id;
            var labelRel = info.connection.getOverlays()[1].label;
            info.connection.idrel = idBoxRel;

            var elem = $('.select-reltype-' + labelRel + ' #' + labelRel + (diagram.reltypesCounter[labelRel] + 1 - 1)).length - 1;
            $($('.select-reltype-' + labelRel + ' #' + labelRel + (diagram.reltypesCounter[labelRel] + 1 - 1))[elem]).attr('selected', 'selected');

            diagram.CounterRels++;
        } else {
            jsPlumb.detach(info.connection);
        }

        var selector = '#' + info.targetEndpoint.elementId + ' .title';
        $(selector).on('mouseover', function() {
            $(selector).css({
                "box-shadow": ""
            });
        });

        $('.endpoint-image').css('visibility', 'visible');
        info.sourceEndpoint.addClass("endpointInvisible");
        info.targetEndpoint.removeClass("dragActive");
        info.targetEndpoint.removeClass("dropHover");
     });

    jsPlumb.bind("connectionDrag", function(connection) {
        // We make the endpoint invisible
        $('.endpoint-image').css('visibility', 'hidden');

        // We make the drag css style for nodes with the correct target
        var scopeSource = connection.endpoints[0].scopeSource;

        jsPlumb.selectEndpoints().each(function(endpoint) {
            var scopeTarget = endpoint.scopeTarget;
                if(scopeTarget) {
                var compare = scopeSource == scopeTarget;
                var compareWildcard = (scopeSource == "wildcard") ||
                                        (scopeTarget == "wildcard");
                if(compare || compareWildcard) {
                    endpoint.addClass("dragActive");
                    var selector = '#' + endpoint.elementId + ' .title';
                    $(selector).on('mouseover', function() {
                        $(selector).css({
                            "box-shadow": "0 0 1em 0.75em #348E82"
                        });
                    });
                    $(selector).on('mouseout', function() {
                        $(selector).css({
                            "box-shadow": ""
                        });
                    });
                }
            }
        });
    });

    jsPlumb.bind("connectionDragStop", function(connection) {
        jsPlumb.selectEndpoints().each(function(endpoint) {
            endpoint.removeClass("dragActive");
            var selector = '#' + endpoint.elementId + ' .title';
            $(selector).on('mouseover', function() {
                $(selector).css({
                    "box-shadow": ""
                });
            });
        });
    });

    /**
     * Handler for create the JSON file
     */
    $(document).on('click', '#run-button', function() {
        var query = diagram.generateQuery();
        console.log("query: ");
        console.log(query);

        var queryJson = JSON.stringify(query);

        $.ajax({
            type: "POST",
            url: diagram.url_query,
            data: {"query": queryJson},
            success: function (data) {
                var headers = $.grep(data, function(n, i) {
                    return typeof(n) == "string";
                });
                if(data.length > 0) {
                    $("#results").html("");
                    var table = $("<TABLE>");
                    table.addClass("content-table");
                    for (var i = 0; i < headers.length; i++) {
                        var header = $("<TH>");
                        header.addClass("header");
                        header.html(headers[i]);
                        table.append(header);
                    }
                    for (var i = 0, j = data.length; i < j; i += 1) {
                        if(typeof(data[i]) != "string") {
                            var row = $("<TR>");
                            row.addClass("row-even");
                            if((i % 2) == 0)
                                row.addClass("row-odd");
                            for (var k = 0, l = data[i].length; k < l; k += 1) {
                                var cell = $("<TD>");
                                cell.text(data[i][k]);
                                row.append(cell);
                            }

                            table.append(row);
                        }
                    }
                    $("#results").append(table);
                    $('#query-builder-query').hide();
                    $('#query-builder-results').show();
                    $('#results').show();
                } else {
                    $("#results").html(gettext("No results found"));
                    $('#query-builder-query').hide();
                    $('#query-builder-results').show();
                    $('#results').show();
                }
                $.unblockUI();
            },
            error: function (e) {
                $("#results").html(gettext("Sorry, was an error in the server: Please, refresh the page and try again. If the error continues, maybe the database is not running."));
                $('#query-builder-query').hide();
                $('#query-builder-results').show();
                $('#results').show();

                $.unblockUI();
            },
            dataType: "json"
        });

    });

    /**
     * Handler for run the query in the backend
     */
    $('#run-button').click(function() {
        $.blockUI({
            message: '<span>' + gettext("Your query is executing. Please wait...") + '</span>',
            css: {
                border: 'none',
                padding: '15px',
                backgroundColor: '#000',
                '-webkit-border-radius': '10px',
                '-moz-border-radius': '10px',
                opacity: .5,
                color: '#fff'
            },
            overlayCSS: {
                opacity: 0.0
            },
            onOverlayClick: $.unblockUI
        });
    });

    /**
     * Handler to get the information to save the query
     */
    $('#save-button').click(function() {
        var saveElements = {};
        var query = diagram.generateQuery();
        saveElements["query"] = query;
        var elements = $('.title select');
        var aliasDict = {};
        $.each(elements, function(index, element) {
            var valuesDict = {};
            var parent = $(element).parent().parent();

            var alias = diagram.replaceChars($(element).val());
            var id = $(parent).attr('id');
            var typename = $(element).attr('class').substring(15);
            // This is for check if we have a relationship or a node
            if(typename.substring(0,1) == "-")
                typename = typename.substring(1);
            var left = $(parent).css('left');
            var top = $(parent).css('top');

            valuesDict['id'] = id;
            valuesDict['typename'] = typename;
            valuesDict['left'] = left;
            valuesDict['top'] = top;

            aliasDict[alias] = valuesDict;
        });
        saveElements['aliases'] = aliasDict;
        // We store all the important values
        saveElements['counter'] = diagram.Counter;
        saveElements['counterRels'] = diagram.CounterRels;
        saveElements['fieldCounter'] = diagram.fieldCounter;
        saveElements['fieldRelsCounter'] = diagram.fieldRelsCounter;
        // What we do with nodetypesCounter and reltypesCounter?
        console.log(JSON.stringify(saveElements));

        $('#query-information').css({
            'display': 'block'
        });
    });

    $(document).ready(init);
})(jQuery);
