/* Adapted from https://github.com/versae/qbe */

// Django i18n.
var gettext = window.gettext || String;

if (!diagram) {
    var diagram = {};
}

// Global variables for the query builder logic

diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.Counter = 0;
diagram.CounterRels = 0;
diagram.fieldCounter = 0;
diagram.fieldRelsCounter = 0;
diagram.nodetypesCounter = [];
diagram.nodetypesList = {};
diagram.reltypesCounter = [];
diagram.reltypesList = {};
diagram.fieldsForNodes = {};
diagram.savedFieldsForRels = {};
diagram.fieldsForRels = {};
diagram.relindex = {};
diagram.boxesSelects = {};
diagram.boxesValues = {};

/*
 * The next dictionaries are useful for the distinct options
 * in the lookups
 */

// Relationship between the string name and the key used in the backend

diagram.stringValues = {
    'em': gettext("matches"),
    'eq': gettext("equals"),
    'lte': gettext("is less than or equal to"),
    'lt': gettext("is less than"),
    'gt': gettext("is greater than"),
    'gte': gettext("is greater than or equal to"),
    'between': gettext("is between"),
    'neq': gettext("does not equal"),
    'isnotnull': gettext("has some value"),
    'isnull': gettext("has no value"),
    'icontains': gettext("contains"),
    'idoesnotcontain': gettext("doesn't contain"),
    'istartswith': gettext("starts with"),
    'iendswith': gettext("ends with")
};

diagram.lookupsBackendValues = {
    'equals': 'eq',
    'is less than or equal to': 'lte',
    'is less than': 'lt',
    'is greater than': 'gt',
    'is greater than or equal to': 'gte',
    'is between': 'between',
    'does not equal': 'neq',
    'has some value': 'isnotnull',
    'has no value': 'isnull',
    'contains': 'icontains',
    "doesn't contain": "idoesnotcontain",
    'starts with': 'istartswith',
    'ends with': 'iendswith'
}

// All the options for the lookups

diagram.lookupsAllValues = [
    diagram.stringValues['em'],
    diagram.stringValues['eq'],
    diagram.stringValues['lte'],
    diagram.stringValues['lt'],
    diagram.stringValues['gt'],
    diagram.stringValues['gte'],
    diagram.stringValues['between'],
    diagram.stringValues['neq'],
    diagram.stringValues['isnotnull'],
    diagram.stringValues['isnull'],
    diagram.stringValues['icontains'],
    diagram.stringValues['idoesnotcontain'],
    diagram.stringValues['istartswith'],
    diagram.stringValues['iendswith']
];

// Set of specific values for the lookups for the types boolean,
// choices, collaborator and auto_user

diagram.lookupsSpecificValues = [
    diagram.stringValues['em'],
    diagram.stringValues['eq'],
    diagram.stringValues['neq'],
    diagram.stringValues['isnotnull'],
    diagram.stringValues['isnull']
];

// Set of specific values for the lookups for the numeric types

diagram.lookupsNumberValues = [
    diagram.stringValues['em'],
    diagram.stringValues['eq'],
    diagram.stringValues['lte'],
    diagram.stringValues['lt'],
    diagram.stringValues['gt'],
    diagram.stringValues['gte'],
    diagram.stringValues['between'],
    diagram.stringValues['neq'],
    diagram.stringValues['isnotnull'],
    diagram.stringValues['isnull']
];

// Set of specific values for the lookups for the text and string types

diagram.lookupsTextValues = [
    diagram.stringValues['em'],
    diagram.stringValues['eq'],
    diagram.stringValues['neq'],
    diagram.stringValues['isnotnull'],
    diagram.stringValues['isnull'],
    diagram.stringValues['icontains'],
    diagram.stringValues['idoesnotcontain'],
    diagram.stringValues['istartswith'],
    diagram.stringValues['iendswith']
];

diagram.lookupsValuesType = {
    'default': diagram.lookupsAllValues,
    'string': diagram.lookupsTextValues,
    'boolean': diagram.lookupsSpecificValues,
    'number': diagram.lookupsNumberValues,
    'text': diagram.lookupsTextValues,
    'date': diagram.lookupsAllValues,
    'time': diagram.lookupsAllValues,
    'choices': diagram.lookupsSpecificValues,
    'float': diagram.lookupsNumberValues,
    'collaborator': diagram.lookupsSpecificValues,
    'auto_now': diagram.lookupsAllValues,
    'auto_now_add': diagram.lookupsAllValues,
    'auto_increment': diagram.lookupsNumberValues,
    'auto_increment_update': diagram.lookupsNumberValues,
    'auto_user': diagram.lookupsSpecificValues
};

diagram.aggregates = [
    "Count",
    "Max",
    "Min",
    "Sum",
    "Average",
    "Deviation"
];

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
            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divManies, divAllowedRelationships, divAllRel, fieldName, field, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox, idBoxAllRels, selectAllRel;
            model = diagram.Models[graphName][typeName];
            root = $("#"+ diagram.Container);
            diagram.Counter++;
            idBox = "diagramBox-" + diagram.Counter +"-"+ typeName;
            idTopBox = "diagramTopBox-" + diagram.Counter + "-" + typeName;
            idFields = "diagramFields-" + diagram.Counter + "-" + typeName;
            idBoxAllRels = "diagramBoxAllRels-" + diagram.Counter + "-" + typeName;
            idAllRels = "diagramAllRel-" + diagram.Counter + "-" + typeName;
            idContainerBoxes = "diagramContainerBoxes-" + diagram.Counter + "-" + typeName;
            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "390px"
            });
            divBox.addClass("body");
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("box-all-rel");
            boxAllRel.attr('id', idBoxAllRels);

            selectAllRel = $("<SELECT>");
            selectAllRel.addClass("select-rel");
            selectAllRel.attr("title", gettext("Add a relationship"));

            var relationsIds = [];
            if(typeName != "wildcard") {
                var relationsLength = model.relations.length;
                for(var i = 0; i < relationsLength; i++) {
                    var relation = model.relations[i];

                    // We only add the relations when the field is the source
                    if(typeName == relation.source) {
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
                        optionRel.html(label + " (" + relation.target_name + ")");
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

            // First option to choose one
            optionRelDefault = $("<OPTION>");
            optionRelDefault.addClass('option-rel');
            optionRelDefault.attr('value', 'choose relationship');
            optionRelDefault.attr('disabled', 'disabled');
            optionRelDefault.attr('selected', 'selected');
            optionRelDefault.html(gettext("choose relationship"));

            selectAllRel.prepend(optionRelDefault);

            boxAllRel.append(selectAllRel);

            divAllowedRelationships = $("<DIV>");
            divAllowedRelationships.attr("id", idAllRels);
            divAllowedRelationships.append(boxAllRel);
            // We append the divs
            divFields = $("<DIV>");
            divFields.attr("id", idFields);
            divFields.css({
                "margin-top": "10px",
                "margin-bottom": "10px"
            });
            countFields = 0;

            divTitle = diagram.addTitleDiv(graphName, model, typeName, modelName, idTopBox, idBox, idAllRels, relationsIds);
            // Create the select for the properties
            //var boxalias = divTitle.data('boxalias');
            var boxalias = divTitle.data('slug');
            diagram.fieldsForNodes[boxalias] = [];
            divField = diagram.addFieldRow(graphName, typeName, idFields, typeName, boxalias, idBox, idAllRels);
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
            addField.attr("data-model", typeName);
            addField.attr("data-typename", typeName);
            addField.attr("data-boxalias", boxalias);
            addField.attr("data-idbox", idBox);
            addField.attr("data-idallrels", idAllRels);
            // Icon
            addFieldIcon = $("<I>");
            addFieldIcon.addClass("fa fa-plus-circle");
            addFieldIcon.attr('id', 'add-field-icon');
            addField.append(addFieldIcon);
            divAddBox = $("<DIV>");
            divAddBox.attr("id", idTopBox);
            divAddBox.append(divFields);

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
            jsPlumb.draggable("diagramBox-"+ diagram.Counter +"-"+ typeName, {
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
                        jsPlumb.repaint(["diagramBox_"+ modelName]);
                        jsPlumb.repaintEverything();
                    });
                }
            });
        };

        /**
         * Add a box for the relation. In this case, we implement
         * the title part and the main box part in the same
         * function
         * - name
         * - label
         * - idRel
         */
        diagram.addRelationBox = function(name, label, idRel) {
            var divTitle, selectReltype, optionReltype, checkboxType, anchorShowHide, iconToggle, anchorDelete, iconDelete;

            var model, root, idBox, divBox, divAddBox, divContainerBoxes, divField, divFields, divAllowedRelationships, fieldName, field, countFields, idFields, boxAllRel, listRelElement, idAllRels, addField, addFieldIcon, idContainerBoxes, removeRelation, idTopBox;

            root = $("#"+ diagram.Container);

            idBox = "diagramBoxRel-" + diagram.CounterRels + "-" + name;
            idTopBox = "diagramTopBoxRel-" + diagram.CounterRels + "-" + name;
            idFields = "diagramFieldsRel-" + diagram.CounterRels + "-" + name;
            idAllRels = "diagramAllRelRel-" + diagram.CounterRels + "-" + name;
            idContainerBoxes = "diagramContainerBoxesRel-" + diagram.CounterRels + "-" + name;
            /*
             *  Title part
             */

            // We need to check if we already have done this, because
            // we have two operation modes for relationships:
            // auto connection and drag and drop

            if(diagram.reltypesCounter[name] >= 1) {
                diagram.reltypesCounter[name]++;
            } else {
                diagram.reltypesCounter[name] = 1;
            }

            // We get the relValue and the slug name to avoid duplicate
            // keys for queries.
            slugValue = name + "_" + diagram.reltypesCounter[name];
            relValue = label + " " + diagram.reltypesCounter[name];

            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.css({
                "background-color": "#AEAA78"
            });
            divTitle.attr("id", idBox + "-title");
            divTitle.attr("data-modelid", idRel);
            divTitle.attr('data-slug', slugValue);
            // Select for the type
            selectReltype = $("<SELECT>");
            selectReltype.addClass("select-reltype-" + name);
            selectReltype.css({
                "width": "65px",
                "float": "left",
                "padding": "0",
                "margin-left": "5%",
                "margin-top": "-1px",
                "display": "none"
            });

            //diagram.savedFieldsForRels[relValue] = [];
            diagram.savedFieldsForRels[slugValue] = [];
            optionReltype = $("<OPTION>");
            optionReltype.addClass("option-reltype-" + name);
            optionReltype.attr('id', name + diagram.reltypesCounter[name]);
            optionReltype.attr('value', relValue);
            optionReltype.attr('data-modelid', idRel);
            optionReltype.html(relValue);
            // This for loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.reltypesCounter[name]; i++) {
                var alias = $(optionReltype).val();
                var selectRel = $($('.select-reltype-' + name)[i]);
                // We check if we already have include this alias
                if ($("option[value='" + alias + "']", selectRel).length == 0)
                    selectRel.append(optionReltype.clone(true));
            }
            // This for loop is to include the old options in the new box
            var typeBoxesLength = diagram.reltypesList[name].length;
            for(var i = 0; i < typeBoxesLength; i++) {
                var alias = diagram.reltypesList[name][i];
                var id = alias.replace(/\s/g, '');
                var selectRelOptions = $('option', selectReltype);
                var exists = false;
                // We need to check if already we have included this alias.
                // This is because the new way to set the relationships:
                // If we drag, we connect and then reconnect.
                $.each(selectRelOptions, function(index, elem) {
                    if($(elem).val() == alias) {
                        exists = true;
                    }
                });
                if(!exists) {
                    var optionToInclude = $("<OPTION>");
                    optionToInclude.addClass("option-reltype-" + name);
                    optionToInclude.attr('id', id);
                    optionToInclude.attr('value', alias);
                    optionToInclude.attr('data-modelid', idRel);
                    optionToInclude.html(alias);
                    selectReltype.append();
                }
            }
            // We add the new alias to the list of the reltype if it does not
            // contain it
            if(diagram.reltypesList[name].indexOf(relValue) == -1)
                diagram.reltypesList[name].push(relValue);
            selectReltype.append(optionReltype);
            diagram.setName(divTitle, label, name, "relation");

            // Show/hide button in the corner of the box and its associated event
            anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ name);
            anchorShowHide.attr("title", gettext("Show/hide box properties"));
            iconToggle = $("<I>");
            iconToggle.addClass("fa fa-plus-circle icon-style");
            iconToggle.css({
                'margin-right': '8px'
            });
            iconToggle.attr('id', 'icon-toggle');

            anchorShowHide.append(iconToggle);
            anchorShowHide.click(function () {
                $('#' + idFields).toggleClass("hidden");
                if (iconToggle.attr('class') == 'fa fa-plus-circle icon-style') {
                    iconToggle.removeClass('fa fa-plus-circle icon-style');
                    iconToggle.addClass('fa fa-minus-circle icon-style');
                    $('#' + idBox).css({
                        'width': '360px'
                    });
                    // We change the width of the select field
                    $('#' + idBox + ' .select-reltype-' + name).css({
                        'width': '46%'
                    });
                    // We show the advanced mode button
                    $('#' + idBox + ' #inlineAdvancedMode_' + name).css({
                        'display': 'inline'
                    });
                } else {
                    iconToggle.removeClass('fa fa-minus-circle icon-style');
                    iconToggle.addClass('fa fa-plus-circle icon-style');
                    $('#' + idBox).css({
                        'width': '195px'
                    });
                    // We change the width of the select field
                    $('#' + idBox + ' .select-reltype-' + name).css({
                        'width': '65px'
                    });
                    // We hide the advanced mode button and the select
                    $('#' + idBox + ' #inlineAdvancedMode_' + name).css({
                        'display': 'none'
                    });
                    $('#' + idBox + ' .select-aggregate').css({
                        'display': 'none'
                    });
                }
            });
            // Advanced mode button in the corner of the box and its associated event
            anchorAdvancedMode = $("<A>");
            anchorAdvancedMode.attr("href", "javascript:void(0);");
            anchorAdvancedMode.attr("id", "inlineAdvancedMode_" + name);
            anchorAdvancedMode.attr("title", gettext("Advanced options"));
            anchorAdvancedMode.css({
                'display': 'none'
            });
            iconAdvancedMode = $("<I>");
            iconAdvancedMode.addClass("fa fa-gear icon-style");
            anchorAdvancedMode.append(iconAdvancedMode);
            anchorAdvancedMode.click(function () {
                var display = $('#' + idBox + " .select-aggregate").css('display');
                var selectorBox = '#' + idBox;
                var selectorAggregate = '#' + idBox + " .select-aggregate";
                var selectorRemoveRelation = '#' + idBox + " #remove-relation-icon";
                if(display == "none") {
                    // We change the width of the box div
                    $(selectorBox).css({
                        'width': '440px'
                    });
                    // We show the advanced options
                    $(selectorAggregate).css({
                        "display": "inline"
                    });
                    // We change the margin left of the relationships remove icon
                    $(selectorRemoveRelation).css({
                        'margin-left': '336px'
                    });
                } else {
                    // We change the width of the box div
                    $(selectorBox).css({
                        'width': '360px'
                    });
                    // We show the advanced options
                    $(selectorAggregate).css({
                        "display": "none"
                    });
                    // We change the margin left of the relationships remove icon
                    $(selectorRemoveRelation).css({
                        'margin-left': '261px'
                    });
                    // We change the value of the aggregate
                    $(selectorAggregate).val('');
                }
            });

            anchorEditSelect = $("<A>");
            anchorEditSelect.attr("href", "javascript:void(0);");
            anchorEditSelect.attr("id", "inlineEditSelect_"+ name);
            anchorEditSelect.attr("title", gettext("Edit alias name"));
            anchorEditSelect.css({
                'display': 'none',
                'margin-right': '4px'
            });
            var iconEditSelect = $("<I>");
            iconEditSelect.addClass("fa fa-pencil icon-style");
            anchorEditSelect.append(iconEditSelect);
            anchorEditSelect.click(function () {
                if(iconEditSelect.attr('class') == 'fa fa-pencil icon-style') {
                    iconEditSelect.removeClass('fa fa-pencil icon-style');
                    iconEditSelect.addClass('fa fa-undo icon-style');
                    var selectorAlias = '#' + idBox + " .select-reltype-" + name;
                    // We store the select for the type
                    selectorObject = $(selectorAlias)[0];
                    diagram.boxesSelects[idBox] = selectorObject;
                    // We get the select value
                    var selectValue = $(selectorAlias).val();
                    // We replace the selectAlias with the input for the user
                    var inputAlias = $("<INPUT>");
                    var classesInput = "select-reltype-" + name + " edit-alias";
                    inputAlias.addClass(classesInput);
                    // This attr is for the logical to get the fields for the query
                    inputAlias.attr("selected", "selected");
                    inputAlias.attr("data-modelid", idRel);
                    inputAlias.attr("data-idbox", idBox);
                    inputAlias.attr("data-oldvalue", selectValue);
                    inputAlias.attr("data-typename", name);
                    inputAlias.attr("data-datatype", 'rel');
                    inputAlias.css({
                        "width": "60px",
                        "float": "left",
                        "padding": "0",
                        "margin-left": "5%",
                        "margin-top": "-1px"
                    });
                    inputAlias.val(selectValue);
                    $(selectorAlias).replaceWith(inputAlias);
                } else {
                    iconEditSelect.removeClass('fa fa-undo icon-style');
                    iconEditSelect.addClass('fa fa-pencil icon-style');
                    var inputSelector = $('#' + idBox + ' .select-reltype-' + name);
                    // We get the select to restore the previous behaviour
                    var selectSelector = diagram.boxesSelects[idBox];
                    inputSelector.replaceWith(selectSelector);
                }
            });

            anchorRemoveRelation = $("<A>");
            anchorRemoveRelation.addClass("remove-box-relation");
            anchorRemoveRelation.attr("href", "javascript:void(0);");
            anchorRemoveRelation.attr("id", "inlineRemoveRelationLink_"+ name);
            anchorRemoveRelation.attr("title", gettext("Remove box"));
            var iconRemoveRelation = $("<I>");
            iconRemoveRelation.addClass("fa fa-times-circle icon-style");
            iconRemoveRelation.attr('id', 'remove-relation-icon')
            iconRemoveRelation.css({
                'margin-right': '4px'
            });
            iconRemoveRelation.attr('id', 'icon-toggle');

            anchorRemoveRelation.append(iconRemoveRelation);
            anchorRemoveRelation.click(function () {
                // We get the connections by type (scope)
                var connections = jsPlumb.select({scope:name});
                // We check the connections between the source and the target
                // to get the idrel appropiated
                var connectionToDelete = undefined;
                connections.each(function(connection) {
                    if(connection.idrel == idBox)
                        connectionToDelete = connection;
                });

                if(connectionToDelete) {
                    // We get the alias of the box to remove it in the selects
                    var boxAlias = $('#' + idBox + ' .select-reltype-' + name).val();
                    // We treat the alias if we have the boxAlias defined
                    if(boxAlias) {
                        // We remove the boxAlias in the other selects
                        diagram.removeAlias(name, boxAlias, "relationship");

                        // We remove the boxAlias of the list
                        var aliasIndex = diagram.reltypesList[name].indexOf(boxAlias);
                        diagram.reltypesList[name].splice(aliasIndex, 1);
                    }

                    // We remove the connection
                    jsPlumb.detach(connectionToDelete);

                    // We check if we have only one box to hide the selects for the alias
                    diagram.hideSelects(name, "relationship");

                    jsPlumb.repaintEverything();
                }
            });

            // We create the div for the corner buttons
            divCornerButtons = $("<DIV>");
            divCornerButtons.addClass("corner-buttons");

            /*
             *  Box part
             */

            divBox = $("<DIV>");
            divBox.attr("id", idBox);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px",
                "width": "195px",
                "background-color": "white",
                "border": "2px solid #AEAA78"
            });
            divBox.addClass("body");
            // Allowed relationships
            // Select for the allowed relationships
            boxAllRel = $("<DIV>");
            boxAllRel.addClass("box-all-rel");
            // We append the divs
            divFields = $("<DIV>");
            divFields.addClass("hidden");
            divFields.attr("id", idFields);
            countFields = 0;
            divCornerButtons.append(anchorRemoveRelation);
            if(diagram.fieldsForRels[name].length > 0) {
                // If we have properties, we add the button to
                // minimize/maximize the box
                divCornerButtons.append(anchorShowHide);
                divCornerButtons.append(anchorAdvancedMode);
                // Create the select for the properties
                divField = diagram.addFieldRelRow(slugValue, name, idFields, idBox);
                divFields.append(divField);
                if (countFields < 5 && countFields > 0) {
                    divFields.addClass("noOverflow");
                } else if (countFields > 0) {
                    divFields.addClass("fieldsContainer");
                }
                // We check if there are fields for add more
                if(divFields.children() > 0) {
                    // Link to add a new row
                    addField = $("<A>");
                    addField.addClass("add-field-row-rel");
                    addField.attr('data-parentid', idFields);
                    addField.attr('data-label', name);
                    // Icon
                    addFieldIcon = $("<I>");
                    addFieldIcon.addClass("fa fa-plus-circle");
                    addFieldIcon.attr('id', 'add-field-icon-prop')
                    addField.append(addFieldIcon);
                }
            }
            divCornerButtons.append(anchorEditSelect);
            divAddBox = $("<DIV>");
            divAddBox.append(divFields);
            divAddBox.append(addField);
            divContainerBoxes = $("<DIV>");
            divContainerBoxes.attr("id", idContainerBoxes);
            divContainerBoxes.append(divAddBox);
            divContainerBoxes.append(divAllowedRelationships);

            divTitle.append(selectReltype);
            divTitle.append(divCornerButtons);

            divBox.append(divContainerBoxes);
            divBox.prepend(divTitle);

            return divBox;
        };

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

            // We check if the typeName is not "wildcard" to change the modelid
            var typeId = -1;
            if(typeName != "wildcard") {
                typeId = model.id;
            }

            // We get the alias for the box and the slug value to avoid
            // duplicated values for boxes with the same key
            var boxAlias = modelName + " " + diagram.nodetypesCounter[typeName];
            var slugValue = typeName + "_" + diagram.nodetypesCounter[typeName];

            divTitle = $("<DIV>");
            divTitle.addClass("title");
            divTitle.attr('id', idBox + "-title");
            divTitle.attr('data-modelid', typeId);
            divTitle.attr('data-slug', slugValue);
            // Select for the type
            selectNodetype = $("<SELECT>");
            selectNodetype.addClass("select-nodetype-" + typeName);
            selectNodetype.css({
                "width": "46%",
                "float": "left",
                "padding": "0",
                "margin-left": "10%",
                "margin-top": "-1px",
                "display": "none"
            });
            optionNodetype = $("<OPTION>");
            var idAndValue = modelName + diagram.nodetypesCounter[typeName];

            optionNodetype.addClass("option-nodetype-" + typeName);
            optionNodetype.attr('id', idAndValue);
            optionNodetype.attr('data-modelid', typeId);
            optionNodetype.attr('value', boxAlias);
            optionNodetype.html(boxAlias);
            // This 'for' loop is to add the new option in the old boxes
            for(var i = 0; i < diagram.nodetypesCounter[typeName]; i++) {
                $($('.select-nodetype-' + typeName)[i]).append(optionNodetype.clone(true));
            }
            // This 'for' loop is to include the old options in the new box
            var typeBoxesLength = diagram.nodetypesList[typeName].length;
            for(var i = 0; i < typeBoxesLength; i++) {
                var alias = diagram.nodetypesList[typeName][i];
                var id = alias.replace(/\s/g, '');;
                selectNodetype.append("<option class='option-nodetype-" + typeName + "' id='" + id + "' data-modelid='" + typeId + "' value='" + alias +"' selected=''>" + alias + "</option>");
            }
            // We add the new alias to the list of the nodetype
            diagram.nodetypesList[typeName].push(boxAlias);
            selectNodetype.append(optionNodetype);
            diagram.setName(divTitle, modelName, typeName, "node");
            //selectNodetype.val(boxAlias).change();
            divTitle.append(selectNodetype);
            // Show/hide button in the corner of the box and its associated event
            anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ typeName);
            anchorShowHide.attr("title", gettext("Show/hide box properties"));
            iconToggle = $("<I>");
            iconToggle.addClass("fa fa-minus-circle icon-style");
            iconToggle.attr('id', 'icon-toggle');

            anchorShowHide.append(iconToggle);
            anchorShowHide.click(function () {
                $('#' + idTopBox).toggleClass("hidden");
                if (iconToggle.attr('class') == 'fa fa-minus-circle icon-style') {
                    iconToggle.removeClass('fa fa-minus-circle icon-style');
                    iconToggle.addClass('fa fa-plus-circle icon-style');
                } else {
                    iconToggle.removeClass('fa fa-plus-circle icon-style');
                    iconToggle.addClass('fa fa-minus-circle icon-style');
                }
                // Recalculate anchor for source endpoints
                diagram.recalculateAnchor(idBox, idAllRels);

                jsPlumb.repaintEverything();
            });
            // Close button in the corner of the box and its associated event
            anchorClose = $("<A>");
            anchorClose.attr("href", "javascript:void(0);");
            anchorClose.attr("id", "inlineDeleteLink_"+ typeName);
            anchorClose.attr("title", gettext("Remove the box"));

            iconClose = $("<I>");
            iconClose.addClass("fa fa-times-circle icon-style");

            anchorClose.append(iconClose);
            anchorClose.click(function () {
                // We remove the option of the properties boxes select
                var selectBoxesProperties = $('.select-other-boxes-properties');
                $.each(selectBoxesProperties, function(index, elem) {
                    $('option[data-slugvalue="' + slugValue + '"]', elem).remove();
                });

                var connections = jsPlumb.getEndpoint(idBox + '-target').connections;
                // We redraw the endpoint of the endpoints connected to this
                // target
                for(var i = 0; i < connections.length; i++) {
                    connections[i].endpoints[0].removeClass('endpointInvisible');
                }

                // We gonna check if we have to hide the alias select of the relationship boxes
                var boxEndpoints = jsPlumb.getEndpoints(idBox);
                // We gonna save the names of the relationships
                var relNamesArray = new Array();
                // We gonna save the ids of the relationship boxes
                var relIdsArray = {};
                $.each(boxEndpoints, function(id, endpoint) {
                    if(endpoint.isSource) {
                        // It is the name, dont confuse with the label
                        var name = endpoint.connectorOverlays[1][1].label;
                        var idRelBox = endpoint.connectorOverlays[2][1].id;
                        relNamesArray.push(name);
                        relIdsArray[name] = idRelBox;
                    }
                });

                // We check if we have to remove some alias of the relationship selects
                $.each(relIdsArray, function(name, idRel) {
                    var boxAlias = $('#' + idRel + ' .select-reltype-' + name).val();
                    // We remove the boxAlias in the other selects
                    diagram.removeAlias(name, boxAlias, "relationship");

                    // We remove the boxAlias of the list
                    var aliasIndex = diagram.reltypesList[name].indexOf(boxAlias);
                    diagram.reltypesList[name].splice(aliasIndex, 1);
                });

                // We detach all the connections
                jsPlumb.detachAllConnections(idBox);
                for(var i = 0; i < relationsIds.length; i++)
                    jsPlumb.deleteEndpoint(relationsIds[i] + "-source");
                jsPlumb.deleteEndpoint(idBox + "-target");

                // We check if we have to hide the selects of some relationships boxes
                $.each(relNamesArray, function(id, name) {
                    diagram.hideSelects(name, "relationship");
                });

                // We get the alias of the box to remove it in the selects
                var boxAlias = $('#' + idBox + ' .select-nodetype-' + typeName).val();

                $('#' + idBox).remove();

                // We remove the boxAlias in the other selects
                diagram.removeAlias(typeName, boxAlias, "node");

                // We remove the boxAlias of the list
                var aliasIndex = diagram.nodetypesList[typeName].indexOf(boxAlias);
                diagram.nodetypesList[typeName].splice(aliasIndex, 1);

                // We check if we have only one box to hide the selects for the alias
                diagram.hideSelects(typeName, "node");
            });
            // We create the div for the corner buttons
            divCornerButtons = $("<DIV>");
            divCornerButtons.addClass("corner-buttons");
            // Advanced mode button in the corner of the box and its associated event
            anchorAdvancedMode = $("<A>");
            anchorAdvancedMode.attr("href", "javascript:void(0);");
            anchorAdvancedMode.attr("id", "inlineAdvancedMode_"+ typeName);
            anchorAdvancedMode.attr("title", gettext("Advanced options"));

            var iconAdvancedMode = $("<I>");
            iconAdvancedMode.addClass("fa fa-gear icon-style");

            anchorAdvancedMode.append(iconAdvancedMode);
            anchorAdvancedMode.click(function () {
                var display = $('#' + idBox + " .select-aggregate").css('display');
                var selectorBox = '#' + idBox;
                var selectorAggregate = '#' + idBox + " .select-aggregate";
                var selectorRemoveRelation = '#' + idBox + " #remove-relation-icon";
                window.idBox = idBox;
                if(display == "none") {
                    // We change the width of the box div
                    $(selectorBox).css({
                        'width': '465px'
                    });
                    // We show the advanced options
                    $(selectorAggregate).css({
                        "display": "inline"
                    });
                    // We change the margin left of the relationships remove icon
                    $(selectorRemoveRelation).css({
                        'margin-left': '336px'
                    });
                } else {
                    // We need the aggregate value in case that we need to
                    // change the option in the order by select
                    var aggregate = $(selectorAggregate).val();
                    // We change the width of the box div
                    $(selectorBox).css({
                        'width': '390px'
                    });
                    // We show the advanced options
                    $(selectorAggregate).css({
                        "display": "none"
                    });
                    // We change the margin left of the relationships remove icon
                    $(selectorRemoveRelation).css({
                        'margin-left': '261px'
                    });
                    // We change the value of the aggregate
                    $(selectorAggregate).val('');
                    // We need to check if we had the checkbox clicked to
                    // restore the value in the order by select
                    var checkboxClicked = $(selectorAggregate).prev().prop('checked');
                    if(checkboxClicked && aggregate) {
                        // We need to take into account that we could have
                        // more than one aggregate
                        var aggregates = $(selectorAggregate);
                        $.each(aggregates, function(index, elem) {
                            var fieldId = $(elem).parent().attr('id');
                            var propertyValue = $(elem).next().val();
                            var titleDiv = $(elem).prev().parent().parent().parent().parent().prev();
                            var boxSlug = $(titleDiv).data('slug');
                            var boxAlias = $('select', titleDiv).val();

                            // We use the slug for the value and alias for the html
                            var orderByFieldVal = boxSlug + '.' + propertyValue;
                            var orderByFieldHTML = boxAlias + '.' + propertyValue;

                            // We remove the option because we have a new option
                            $('#id_select_order_by option[data-fieldid="' + fieldId + '"]').remove();

                            // We add the orderByField to the select
                            var selectNewOption = $("<OPTION>");
                            selectNewOption.attr('data-fieldid', fieldId);
                            selectNewOption.attr('value', orderByFieldVal);
                            selectNewOption.html(orderByFieldHTML);
                            $('#id_select_order_by').append(selectNewOption);
                        });
                    }
                    // We change the aggregate in the select for 
                    // properties of other boxes
                    var aggregates = $(selectorAggregate);
                    $.each(aggregates, function(index, elem) {
                        var fieldId = $(elem).parent().attr('id');
                        var propertyValue = $(elem).next().val();
                        var titleDiv = $(elem).prev().parent().parent().parent().parent().prev();
                        var boxSlug = $(titleDiv).data('slug');
                        var boxAlias = $('select', titleDiv).val();

                        // We use the slug for the value and alias for the html
                        var newValue = boxSlug + '.' + propertyValue;
                        var newHTML = boxAlias + '.' + propertyValue;

                        var selectOtherBoxesProps = $('.select-other-boxes-properties');

                        window.fieldId = fieldId;
                        window.newValue = newValue;
                        window.newHTML = newHTML;

                        $.each(selectOtherBoxesProps, function(index, elem) {
                            var anotherIdBox = $(elem).parent().parent().parent().parent().parent().attr('id');
                            if(idBox !== anotherIdBox) {
                                var $option = $('option[data-fieldid="' + fieldId + '"]', $(elem));
                                // We get the value of the lookup input to 
                                // check if we need to change it too.
                                var $lookupInput = $option.parent().prev();
                                var sameValue = $option.html() === $lookupInput.val();
                                // Let's check if the value is already in the 
                                // select
                                var existsValue = $('option[value="' + newValue + '"]', $(elem)).length;

                                // If exists, we remove it.
                                if(existsValue > 0) {
                                    $option.remove();
                                } else {
                                    $option.attr('value', newValue);
                                    $option.html(newHTML);
                                }

                                if(sameValue) {
                                    $('option[value="' + newValue + '"]', elem).change();
                                    $lookupInput.attr('data-withvalue', newValue);
                                    $lookupInput.val(newHTML);
                                }
                            }
                        });
                    });
                }

                jsPlumb.repaintEverything();
            });
            anchorEditSelect = $("<A>");
            anchorEditSelect.attr("href", "javascript:void(0);");
            anchorEditSelect.attr("id", "inlineEditSelect_"+ typeName);
            anchorEditSelect.attr("title", gettext("Edit alias name"));
            anchorEditSelect.css({
                'display': 'none'
            });

            var iconEditSelect = $("<I>");
            iconEditSelect.addClass("fa fa-pencil icon-style");

            anchorEditSelect.append(iconEditSelect);
            anchorEditSelect.click(function () {
                if(iconEditSelect.attr('class') == 'fa fa-pencil icon-style') {
                    iconEditSelect.removeClass('fa fa-pencil icon-style');
                    iconEditSelect.addClass('fa fa-undo icon-style');
                    var selectorAlias = '#' + idBox + " .select-nodetype-" + typeName;
                    // We store the select for the type
                    selectorObject = $(selectorAlias)[0];
                    diagram.boxesSelects[idBox] = selectorObject;
                    // We get the select value for next comparisons
                    var selectValue = $(selectorAlias).val();
                    // We replace the selectAlias with the input for the user
                    var inputAlias = $("<INPUT>");
                    var classesInput = "select-nodetype-" + typeName + " edit-alias";
                    inputAlias.addClass(classesInput);
                    // This attr is for the logical to get the fields for the query
                    inputAlias.attr("selected", "selected");
                    inputAlias.attr("data-modelid", typeId);
                    inputAlias.attr("data-idbox", idBox);
                    inputAlias.attr("data-oldvalue", selectValue);
                    //inputAlias.attr("data-firstvalue", selectValue);
                    inputAlias.attr("data-typename", typeName);
                    inputAlias.attr("data-datatype", 'node')
                    inputAlias.css({
                        "width": "36%",
                        "float": "left",
                        "padding": "0",
                        "margin-left": "10%",
                        "margin-top": "-1px"
                    });
                    inputAlias.val(selectValue);
                    $(selectorAlias).replaceWith(inputAlias);
                } else {
                    iconEditSelect.removeClass('fa fa-undo icon-style');
                    iconEditSelect.addClass('fa fa-pencil icon-style');
                    var inputSelector = $('#' + idBox + ' .select-nodetype-' + typeName);
                    // We get the select to restore the previous behaviour
                    var selectSelector = diagram.boxesSelects[idBox];
                    inputSelector.replaceWith(selectSelector);
                }
            });

            divCornerButtons.append(anchorClose);
            divCornerButtons.append(anchorShowHide);
            divCornerButtons.append(anchorAdvancedMode);
            divCornerButtons.append(anchorEditSelect);

            divTitle.append(divCornerButtons);
            divTitle.attr("data-boxalias", boxAlias);

            return divTitle;
        };

        /**
         * Set the name fo the model box getting shorter and adding ellipsis
         */
        diagram.setName = function (div, name, typeName, type) {
            // We check if we show the select to allow more space for the name
            var numOfBoxes = $('.select-nodetype-' + typeName).length;
            var selectorForName = $('.select-nodetype-' + typeName);
            if(type == "relation") {
                // If the name is equals to the typeName, is a relationship
                numOfBoxes =  $('.select-reltype-' + typeName).length;
                selectorForName = $('.select-reltype-' + typeName);
            }
            var html = "<span class='box-name'>" + name + " <span class='show-as'>" + gettext("as") + "</span></span>";
            if(numOfBoxes == 1) {
                if(name.length > 5) {
                    html = "<span class='box-name'>" + name.substr(0, 5) + "…" + " <span class='show-as'>" + gettext("as") + "</span></span>";
                    // We change the name of the box number 0 too
                    var firstBoxName = selectorForName.prev();
                    firstBoxName.replaceWith(html);
                }
            } else if(numOfBoxes > 1) {
                if(name.length > 5) {
                    html = "<span class='box-name'>" + name.substr(0, 5) + "…" + " <span class='show-as'>" + gettext("as") + "</span></span>";
                }
            } else {
                // We allow more space
                if(name.length > 25) {
                    html = "<span class='box-name'>" + name.substr(0, 25) + "…" + " <span class='show-as'>" + gettext("as") + "</span></span>";
                }
            }
            div.append(html);
            return div;
        };

        /**
         * Load the node type from the schema
         * - typeName
         */
        diagram.loadBox = function(typeName) {
            var graph, models, modelName;
            var modelNameValue = "";
            if (diagram.Models) {
                for(graph in diagram.Models) {
                    models = diagram.Models[graph];
                    for(modelName in models) {
                        if(modelName.localeCompare(typeName) == 0) {
                            // Node type counter for the node type select field
                            if(diagram.nodetypesCounter[typeName] >= 1) {
                                diagram.nodetypesCounter[typeName]++;
                            } else {
                                diagram.nodetypesCounter[typeName] = 1;
                                diagram.nodetypesList[typeName] = new Array();
                            }

                            modelNameValue = models[modelName].name;
                            diagram.addBox(graph, modelNameValue, typeName);
                        }
                    }
                    if(typeName == "wildcard") {
                        // Node type counter for the node type select field
                        if(diagram.nodetypesCounter[typeName] >= 1) {
                            diagram.nodetypesCounter[typeName]++;
                        } else {
                            diagram.nodetypesCounter[typeName] = 1;
                            diagram.nodetypesList[typeName] = new Array();
                        }

                        modelNameValue = "Wildcard";
                        diagram.addBox(graph, modelNameValue, typeName);
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
            model = diagram.Models[graphName][typeName];
            diagram.fieldCounter++;
            fieldId = "field" + diagram.fieldCounter;
            diagram.fieldsForNodes[boxalias].push(fieldId);
            if(typeName != "wildcard") {
                lengthFields = model.fields.length;
                // Select property
                selectProperty = $("<SELECT>");
                selectProperty.addClass("select-property");
                selectProperty.css({
                    "width": "80px"
                });
                selectProperty.attr('data-fieldid', fieldId);
                selectProperty.attr('data-boxalias', boxalias);
                selectProperty.attr("title", gettext("Select a property"));
                // First option to choose one
                optionProperty = $("<OPTION>");
                optionProperty.addClass('option-property');
                optionProperty.attr('value', 'undefined');
                optionProperty.attr('disabled', 'disabled');
                optionProperty.attr('selected', 'selected');
                optionProperty.html(gettext("choose one"));
                selectProperty.append(optionProperty);

                // We get the values for the properties select and the values
                // for the lookups option in relation with the datatype
                for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                    field = model.fields[fieldIndex];
                    datatype = field.type;
                    optionProperty = $("<OPTION>");
                    optionProperty.addClass('option-property');
                    optionProperty.attr('value', field.label);
                    optionProperty.attr('data-propertyid', field.id);
                    optionProperty.attr('data-datatype', field.type);
                    if(field.choices)
                        optionProperty.attr('data-choices', field.choices);
                    optionProperty.html(field.label);
                    selectProperty.append(optionProperty);
                }
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
                selectLookup.attr("title", gettext("Select a lookup"));
                selectLookup.css({
                    "width": "80px"
                });
            } else {
                // We add an input field to get the return value
                selectProperty = $("<INPUT>");
                selectProperty.addClass("wildCardInput select-property");
                selectProperty.attr('id', fieldId);
                selectProperty.attr('data-fieldid', fieldId);
                selectProperty.attr("title", gettext("Select a property"));
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
                selectLookup.attr("title", gettext("Select a lookup"));
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
            checkboxProperty.attr("title", gettext("Check it to return the property"));
            checkboxProperty.prop("disabled", true);
            // Add and-or div
            divAndOr = $("<DIV>");
            divAndOr.addClass("and-or-option");
            divAndOr.css({
                'display': 'inline'
            });
            selectAndOr = $("<SELECT>");
            selectAndOr.addClass("select-and-or");
            selectAndOr.attr('data-parentid', parentId);
            selectAndOr.attr('data-model', modelName);
            selectAndOr.attr('data-graph', graphName);
            selectAndOr.attr('data-typename', typeName);
            selectAndOr.attr('data-boxalias', boxalias);
            selectAndOr.attr('data-idbox', idBox);
            selectAndOr.attr('data-idallrels', idAllRels);
            selectAndOr.attr("title", gettext("Add another property"));
            selectAndOr.append("<option class='option-and-or' value='not' selected='selected' disabled>" + gettext("choose one") + "</option>");
            selectAndOr.append("<option class='option-and-or' value='and'>" + gettext("And") + "</option>");
            selectAndOr.append("<option class='option-and-or' value='or'>" + gettext("Or") + "</option>");
            divAndOr.append(selectAndOr);

            // Link to remove the lookup
            removeField = $("<A>");
            removeField.addClass("remove-field-row");
            removeField.attr('data-fieldid', fieldId);
            removeField.attr('data-parentid', parentId);
            removeField.attr('data-idbox', idBox);
            removeField.attr('data-idallrels', idAllRels);
            // Icon
            removeFieldIcon = $("<I>");
            removeFieldIcon.addClass("fa fa-minus-circle");
            removeFieldIcon.attr('id', 'remove-field-icon');
            removeField.append(removeFieldIcon);

            // Select for the aggregates elements
            selectAggregate = $("<SELECT>");
            selectAggregate.addClass("select-aggregate");
            $(selectAggregate).prop('disabled', true);
            // We check if we have other aggregates visibles
            displayAggregates = $("#" + idBox + " .select-aggregate").css('display');
            selectAggregate.css({
                'display': displayAggregates
            });
            selectAggregate.append("<option class='option-aggregate' value='' selected='selected'>" + gettext("None") + "</option>");
            for(var i = 0; i < diagram.aggregates.length; i++) {
                // We append the aggregate and the aggregate Distinct
                var aggregate = diagram.aggregates[i];
                var aggregateDistinct = aggregate + " distinct";
                selectAggregate.append("<option class='option-aggregate' value='" + aggregate + "' data-distinct='false'>" + gettext(aggregate) + "</option>");
                selectAggregate.append("<option class='option-aggregate' value='" + aggregate + "' data-distinct='true'>" + gettext(aggregateDistinct) + "</option>");
            }
            // We append the patterns
            divField.append(checkboxProperty);
            divField.append(selectAggregate);
            divField.append(selectProperty);
            divField.append(selectLookup);
            divField.append(divAndOr);
            divField.append(removeField);

            return divField;
        };

        /**
         * Add a new row for a field in a rel box
         * - boxAlias
         * - label
         * - idFields
         * - idBox
         */
        diagram.addFieldRelRow = function(boxAlias, label, idFields, idBox) {
            var model, lengthFields, fieldId, selectProperty, selectLookup, field, datatype, optionProperty, inputLookup, divField, divAndOr, selectAndOr, removeField, removeFieldIcon, checkboxProperty;
            var fields = diagram.fieldsForRels[label];
            lengthFields = fields.length;
            diagram.fieldRelsCounter++;
            fieldId = "field-" + diagram.fieldRelsCounter + "-" + label;
            diagram.savedFieldsForRels[boxAlias].push(fieldId);
            divField = $("<DIV>");
            divField.addClass("field");
            divField.css({
                "margin-top": "14px"
            });
            divField.attr('id', fieldId);
            // We check if there are fields
            if(lengthFields > 0) {
                // Select property
                selectProperty = $("<SELECT>");
                selectProperty.addClass("select-property");
                selectProperty.attr('data-fieldid', fieldId);
                selectProperty.attr("title", gettext("Select a property"));
                // First option to choose one
                optionProperty = $("<OPTION>");
                optionProperty.addClass('option-property');
                optionProperty.attr('value', 'undefined');
                optionProperty.attr('disabled', 'disabled');
                optionProperty.attr('selected', 'selected');
                optionProperty.html(gettext("choose one"));
                selectProperty.append(optionProperty);
                // Select lookup
                selectLookup = $("<SELECT>");
                selectLookup.addClass("select-lookup");
                selectLookup.attr("title", gettext("Select a lookup"));
                // We get the values for the properties select and the values
                // for the lookups option in relation with the datatype
                for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                    field = fields[fieldIndex];
                    datatype = field.type;
                    optionProperty = $("<OPTION>");
                    optionProperty.addClass('option-property');
                    optionProperty.attr('value', field.label);
                    optionProperty.attr('data-propertyid', field.id);
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
                checkboxProperty.attr("title", gettext("Check it to return the property"));
                checkboxProperty.prop("disabled", true);
                // Add and-or div
                divAndOr = $("<DIV>");
                divAndOr.addClass("and-or-option");
                divAndOr.css({
                    'display': 'inline'
                });
                selectAndOr = $("<SELECT>");
                selectAndOr.addClass("select-and-or-rel");
                selectAndOr.attr('data-label', label);
                selectAndOr.attr('data-parentid', idFields);
                selectAndOr.attr("title", gettext("Add another property"));
                selectAndOr.append("<option class='option-and-or' value='not' selected='selected' disabled>" + gettext("choose one") + "</option>");
                selectAndOr.append("<option class='option-and-or' value='and'>" + gettext("And") + "</option>");
                selectAndOr.append("<option class='option-and-or' value='or'>" + gettext("Or") + "</option>");
                divAndOr.append(selectAndOr);

                // Link to remove the lookup
                removeField = $("<A>");
                removeField.addClass("remove-field-row-rel");
                removeField.attr('data-fieldid', fieldId);
                removeField.attr('data-parentid', idFields);
                // Icon
                removeFieldIcon = $("<I>");
                removeFieldIcon.addClass("fa fa-minus-circle");
                removeFieldIcon.attr('id', 'remove-field-icon-rel');
                removeField.append(removeFieldIcon);

                // Select for the aggregates elements
                selectAggregate = $("<SELECT>");
                selectAggregate.addClass("select-aggregate");
                // We check if we have other aggregates visibles
                displayAggregates = $("#" + idBox + " .select-aggregate").css('display');
                selectAggregate.css({
                    'display': displayAggregates
                });
                $(selectAggregate).prop('disabled', true);
                selectAggregate.append("<option class='option-aggregate' value='' selected='selected'>" + gettext("None") + "</option>");
                for(var i = 0; i < diagram.aggregates.length; i++) {
                    // We append the aggregate and the aggregate Distinct
                    var aggregate = diagram.aggregates[i];
                    var aggregateDistinct = aggregate + " distinct";
                    selectAggregate.append("<option class='option-aggregate' value='" + aggregate + "' data-distinct='false'>" + gettext(aggregate) + "</option>");
                    selectAggregate.append("<option class='option-aggregate' value='" + aggregate + "' data-distinct='true'>" + gettext(aggregateDistinct) + "</option>");
                }
            }

                // We append the patterns
                divField.append(checkboxProperty);
                divField.append(selectAggregate);
                divField.append(selectProperty);
                divField.append(selectLookup);
                divField.append(divAndOr);
                divField.append(removeField);

            return divField;
        };

        /**
         * Calculate the anchor for an endpoint pattern.
         * The height used for the relations divs are
         * 24 px each. The accuracy of the calculations
         * have been obtained by testing the results.
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
        };

        /**
         * Function that checks the number of boxes of a type to
         * show the selects for the alias. If we have more than 1 box,
         * we show them.
         * - typeName
         * - elemType
         */
        diagram.showSelects = function(typeName, elemType) {
            var numberOfBoxes = 0;

            // We check if the elemType is a node or a  relationship
            var boxesSelector = '.select-nodetype-' + typeName;
            var elems = $('#diagram').children();
            if(elemType == "relationship") {
                boxesSelector = '.select-reltype-' + typeName;
                elems = $('#diagramContainer').children();
            }

            // We check the number of boxes of that type that we already have
            $.each(elems, function(index, elem) {
                var elemId = $(elem).attr('id');
                if(elemId != undefined) {
                    var filter = new RegExp(".-" + typeName);
                    if(elemId.match(filter)) {
                        numberOfBoxes++;
                    }
                }
            });

            // If we have more than one box of that type at least, we show the selects and the "as" text
            if(numberOfBoxes > 1) {
                // We get the id of the type boxes
                var boxes = $(boxesSelector).parent().parent();
                // And we show the selects and the "as" text of each
                $.each(boxes, function(index, elem) {
                    idBox = $(elem).attr('id');
                    $('#' + idBox + ' ' + boxesSelector).css({
                        "display": "inline"
                    });
                    $('#' + idBox +  ' .show-as').css({
                        "display": "inline"
                    });
                    $('#' + idBox +  ' #inlineEditSelect_' + typeName).css({
                        "display": "inline"
                    });
                });
            }
        };

        /**
         * Function that checks the number of boxes of a type to
         * hide the selects for the alias. If we have 1 box, then we hide
         * them.
         * - typeName
         * - elemType
         */
        diagram.hideSelects = function(typeName, elemType) {
            var numberOfBoxes = 0;

            // We check if the elemType is a node or a  relationship
            var boxesSelector = '.select-nodetype-' + typeName;
            var elems = $('#diagram').children();
            if(elemType == "relationship") {
                boxesSelector = '.select-reltype-' + typeName;
                elems = $('#diagramContainer').children();
            }

            // We check the number of boxes of that type that we already have
            $.each(elems, function(index, elem) {
                var elemId = $(elem).attr('id');
                if(elemId != undefined) {
                    var filter = new RegExp(".-" + typeName);
                    if(elemId.match(filter)) {
                        numberOfBoxes++;
                    }
                }
            });

            // If we have one box of that nodetype at least, we hide the selects and the "as" text
            if(numberOfBoxes == 1) {
                // We get the id of the nodetype boxes
                var boxes = $(boxesSelector).parent().parent();
                // And we hide the selects and the "as" text of each
                $.each(boxes, function(index, box) {
                    idBox = $(box).attr('id');
                    $('#' + idBox + ' ' + boxesSelector).css({
                        "display": "none"
                    });
                    $('#' + idBox +  ' .show-as').css({
                        "display": "none"
                    });
                    $('#' + idBox +  ' #inlineEditSelect_' + typeName).css({
                        "display": "none"
                    });
                    // We restore the name for the type
                    var name = $(boxesSelector).parent().data('boxalias').split(' ')[0];
                    $('#' + idBox + ' .box-name').html(name);
                });
            } else if(numberOfBoxes == 0) {
                // We reset the counter
                if(elemType == "node") {
                    diagram.nodetypesCounter[typeName] = 1;
                } else {
                    diagram.reltypesCounter[typeName] = 1;
                }
            }
        };

        /**
         * Function that removes in the selects of the boxes, the alias
         * of a deleted box
         * - typeName
         * - boxAlias
         * - elemType
         */
        diagram.removeAlias = function(typeName, boxAlias, elemType) {
            var boxes = $('.select-nodetype-' + typeName);

            if(elemType == "relationship") {
                boxes = $('.select-reltype-' + typeName);
            }

            // We iterate over the boxes
            $.each(boxes, function(index, box) {
                // We iterate over the options of every box
                $(box).children().each(function(index) {
                    var $this = $(this);
                    if($this.val() == boxAlias) {
                        $this.remove();
                    }
                })
            })
        };

        /**
         * Function that changes the name of a specific type alias
         * - newAlias
         * - oldAlias
         * - typeName
         * - isNodetype
         */
        diagram.propagateValue = function(newAlias, oldAlias, typeName, isNodetype) {
            // We check if we treat with nodes or relationships
            if(isNodetype) {
                // We need to change the old alias for the new
                // We treat the nodetypesList
                if (diagram.nodetypesList[typeName]) {
                    aliases = diagram.nodetypesList[typeName];
                    $.each(aliases, function(index, elem) {
                        if(elem == oldAlias) {
                            diagram.nodetypesList[typeName][index] = newAlias;
                        }
                    });
                }
                // We treat the fieldsForNodes
                if (diagram.fieldsForNodes[oldAlias]) {
                    Object.defineProperty(diagram.fieldsForNodes, newAlias,
                        Object.getOwnPropertyDescriptor(diagram.fieldsForNodes, oldAlias));
                    delete diagram.fieldsForNodes[oldAlias];
                }
                // We iterate over all the options of the selects and the inputs
                var selectsAlias = $('.select-nodetype-' + typeName + ' option');
                $.each(selectsAlias, function(index, select) {
                    if($(select, 'option').val() == oldAlias) {
                        $newOption = $(this);
                        $newOption.attr('id', typeName + diagram.nodetypesCounter[typeName]);
                        $newOption.attr('value', newAlias);
                        $newOption.html(newAlias);
                    }
                });
            } else {
                // We need to change the old alias for the new
                // We treat the nodetypesList
                if (diagram.reltypesList[typeName]) {
                    aliases = diagram.reltypesList[typeName];
                    $.each(aliases, function(index, elem) {
                        if(elem == oldAlias) {
                            diagram.reltypesList[typeName][index] = newAlias;
                        }
                    });
                }
                // We treat the fieldsForNodes
                if (diagram.fieldsForRels[oldAlias]) {
                    Object.defineProperty(diagram.fieldsForRels, newAlias,
                        Object.getOwnPropertyDescriptor(diagram.fieldsForRels, oldAlias));
                    delete diagram.fieldsForRels[oldAlias];
                }
                // We iterate over all the options of the selects and the inputs
                var selectsAlias = $('.select-reltype-' + typeName + ' option');
                $.each(selectsAlias, function(index, select) {
                    if($(select, 'option').val() == oldAlias) {
                        $newOption = $(this);
                        $newOption.attr('id', typeName + diagram.nodetypesCounter[typeName]);
                        $newOption.attr('value', newAlias);
                        $newOption.html(newAlias);
                    }
                });
            }
        };

        /**
         * Function that encapsules all the necessary to load a query with
         * an alias different to default
         * - idBox
         * - newAlias
         * - typeName
         * - isNodetype
         */
        diagram.loadQueryWithAlias = function(idBox, newAlias, typeName, isNodetype) {
            // We select the correct value for the alias
            // We need to take into account the edit alias feature
            // We get all the values in the select
            var boxOptions = $('#' + idBox + ' .title select option');
            var arrayValues = $.map(boxOptions, function(elem){
                return $(elem).val();
            });
            // The new alias is the latest of the list, so we need to
            // change that element
            var elementsLength = arrayValues.length - 1;
            var latestElement = arrayValues[elementsLength];
            if(latestElement != newAlias) {
                // We check if we have to show the 'alias selects' for a correct behaviour
                if(isNodetype) {
                    diagram.showSelects(typeName, "node");
                } else {
                    diagram.showSelects(typeName, "relationship");
                }
                // We change the value and the html
                var newElement = $($('#' + idBox + ' .title select option')[elementsLength]);
                var oldAlias = newElement.val();
                newElement.val(newAlias);
                newElement.html(newAlias);
                // We propagate the new alias.
                // We need to change the old alias for the new
                if(isNodetype) {
                    // We treat the nodetypesList
                    if (diagram.nodetypesList[typeName]) {
                        aliases = diagram.nodetypesList[typeName];
                        // We check the last element
                        aliasesLength = aliases.length;
                        lastElement = aliases[aliasesLength - 1];
                        if(lastElement == oldAlias) {
                            diagram.nodetypesList[typeName][aliasesLength - 1] = newAlias;
                        }
                    }
                } else {
                    // We treat the reltypesList
                    if (diagram.reltypesList[typeName]) {
                        aliases = diagram.reltypesList[typeName];
                        // We check the last element
                        aliasesLength = aliases.length;
                        lastElement = aliases[aliasesLength - 1];
                        if(lastElement == oldAlias) {
                            diagram.reltypesList[typeName][aliasesLength - 1] = newAlias;
                        }
                    }
                }
                // We iterate over the last options of the selects and
                // the inputs
                var selects = $('.select-nodetype-' + typeName);
                var selectsLength = selects.length;
                var index = 0;
                while(index < selectsLength) {
                    var select = selects[index];
                    var selectLastElem = select.length - 1;
                    // We only change the last element of the select
                    var $lastElemVal = $(select[selectLastElem]);
                    if($lastElemVal.val() == oldAlias) {
                        $lastElemVal.attr('id', typeName + diagram.nodetypesCounter[typeName]);
                        $lastElemVal.attr('value', newAlias);
                        $lastElemVal.html(newAlias);
                    }
                    index++;
                }
            }
            $('#' + idBox + ' .title select').val(newAlias);
        };

        /**
         * Function to create the logic when a field row is deleted
         * - parentId
         * - fieldId
         * - selectAndOr
         */
        diagram.removeFields = function(parentId, fieldId, selectorAndOr) {
            // We check that the field box need to have one
            // field row at least
            if($('#' + parentId).children().length > 1) {
                $("#" + fieldId).remove();
            } else {
                // We restore the default display for a field
                var fieldSelector = "#" + fieldId;
                $(fieldSelector + ' .select-property option[value="undefined"]').attr('selected', 'selected');
                $(fieldSelector + ' .select-lookup option[value="undefined"]').attr('selected', 'selected');
                $(fieldSelector + ' .select-lookup').css({
                    'display': 'none'
                });
                $(fieldSelector + ' .lookup-value').val('');
                $(fieldSelector + ' .lookup-value').css({
                    'display': 'none'
                });

                $(fieldSelector + ' .select-other-boxes-properties').css({
                    'display': 'none'
                });

                $(fieldSelector + ' ' + selectorAndOr + ' option[value="not"]').attr('selected', 'selected');
                $(fieldSelector + ' ' + selectorAndOr).css({
                    'display': 'none'
                });
            }

            // We select the 'Choose one' value for the last field
            var newFieldId = $($('#' + parentId).children().last()).attr('id');
            $('#' + newFieldId + ' .option-and-or:disabled').attr('disabled', false);
            $('#' + newFieldId + ' ' + selectorAndOr).val(gettext('choose one'));
            $('#' + newFieldId + ' ' + + selectorAndOr).children().first().prop('disabled', 'disabled');
        };

        /**
         * Returns the options of a relationship
         * - type
         * - label
         * - idRel
         * - anchor
         */
        diagram.getRelationshipOptions = function(type, name, label, idRel, anchor) {
            var relationshipOptions = null;

            if(type == 'source') {
                relationshipOptions = {
                    endpoint: [
                        "Image",{
                            src: diagram.relationshipImageSrc,
                            cssClass:"endpoint-image"
                        }],
                    anchors: [1, anchor, 1, 0],
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
                            label:name,
                            id:label}],
                        ["Custom", {
                            create:function(component) {
                                var divBox = diagram.addRelationBox(name, label, idRel);
                                return divBox;
                            },
                            location:0.5,
                            id:"diagramBoxRel-" + diagram.CounterRels + "-" + name
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
                relationshipOptions = {
                    endpoint: [
                    "Rectangle",
                        {
                            width: 360,
                            height: 23,
                            cssClass: 'query-box-endpoint-target'
                        }
                    ],
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
        };

        /**
         * Function triggered when a new relationship is loaded and checks
         * if we have loaded some box with the target equal to targetType.
         * If not, we load a box with that target and create a relationship
         * between the boxes.
         * - targetType
         * - relation
         * - sourceId
         * - label
         * - name
         * - idRel
         */
        diagram.checkTargetType = function(targetType, relation, sourceId, label, name, idRel) {
            var elems = $('#diagram').children();
            var numberOfBoxes = 0;
            var uuidSource = relation + "-source";
            var uuidTarget = "";
            // We check the number of boxes of that type that we already have
            $.each(elems, function(index, elem) {
                var elemId = $(elem).attr('id');
                if(elemId != undefined) {
                    var filter = new RegExp(".-" + targetType);
                    if(elemId.match(filter)) {
                        numberOfBoxes++;
                    }
                }
            });

            // If we have 1 at least, we do nothing. In another case we load a
            // box of that type and create a relationship.
            if(numberOfBoxes == 0) {
                var typesLinks = $('#node-types td').children();
                $.each(typesLinks, function(index, link) {
                    var dataType = $(link).data("type");
                    if(dataType == targetType) {
                        $(link).click();
                    }
                });

                // We update the elems variable to include the new box added
                elems = $('#diagram').children();
                var targetId = "";
                // We get the id of the new box and we create the connection
                $.each(elems, function(index, elem) {
                    var elemId = $(elem).attr('id');
                    if(elemId != undefined) {
                        var filter = new RegExp(".-" + targetType);
                        if(elemId.match(filter)) {
                            uuidTarget = elemId + "-target";
                            targetId = elemId;
                        }
                    }
                });

                // We create the connection
                diagram.addRelation(sourceId, targetId, label, name, idRel);

                jsPlumb.repaintEverything();
            }
        };

        /**
         * Function to create a new relatioship between two boxes
         * - sourceId
         * - targetId
         * - label
         * - name
         * - idRel
         */
        diagram.addRelation = function(sourceId, targetId, label, name, idRel) {
            // We create the connection between the boxes.
            jsPlumb.connect({
                scope: name,
                source: sourceId,
                target: targetId,
                detachable:false,
                connector:"Flowchart",
                endpoint: "Blank",
                anchor:"Continuous",
                connectorStyle: {
                    strokeStyle: '#AEAA78',
                    lineWidth: 2
                },
                overlays:[
                    [ "PlainArrow", {
                        foldback: 0,
                        width:10,
                        length:10,
                        location:1,
                        id:"arrow"}],
                    [ "Label", {
                        label: name,
                        id: label}],
                    ["Custom", {
                        create:function(component) {
                            var divBox = diagram.addRelationBox(name, label, idRel);
                            return divBox;
                        },
                        location:0.5,
                        id:"diagramBoxRel-" + diagram.CounterRels + "-" + name
                    }]
                ],
                paintStyle: {
                    strokeStyle: '#AEAA78',
                    lineWidth: 2
                },
                backgroundPaintStyle: {
                    strokeStyle: '#AEAA78',
                    lineWidth: 4
                }
            });

            // We increment the diagram.CounterRels
            diagram.CounterRels++;

            // We check if the type is wildcard
            if(name == "WildcardRel")
                   name = "wildcard";
            // We remove the relation row in the source box
            var idDivRelSourceBox = "#div-" + sourceId + "-" + name;
            $(idDivRelSourceBox).remove();
            // We still have the endpoints to create connections.
            // We need to remove the source endpoint of the relationship.
            var endpointUuid = sourceId + '-' + name + '-source';
            jsPlumb.deleteEndpoint(endpointUuid);
            // We decrement the value of the relationship index to calculate
            // the anchor for the source endpoints
            diagram.relindex[sourceId]--;
            // We will repaint everything and recalculate anchors
            var sourceIdSplitted = sourceId.split('-');
            var indexAndName = sourceIdSplitted[1] + '-' + sourceIdSplitted[2];
            var idAllRels = 'diagramAllRel-' + indexAndName;
            diagram.recalculateAnchor(sourceId, idAllRels);
            jsPlumb.repaintEverything();
        };
    };

    /**
     * Generate the query to send to the backend
     */
    diagram.generateQuery = function() {
        var query = {};
        var propertiesChecked = {};

        // Meta
        // Meta dictionary to store meta information to build the query
        // appropriately
        var meta_dict = {}
        meta_dict["has_distinct"] = $('#id_distinct_result').prop('checked');
        // Let's declare the dictionary for the special case of aggregates in
        // conditions.
        meta_dict["with_statement"] = {};
        // And the dictionary for properties used in the lookup input
        meta_dict["boxes_properties"] = {};

        // Conditions
        var conditionsArray = new Array();
        var properties = $('.select-property');
        $.each(properties, function(index, property) {
            var conditionArray = new Array();
            var lookup = $(property).next().val();
            var propertyTag = "property";
            // We really should think about another solution to get the parent element
            var parent = $(property).parent().parent().parent().parent().parent();
            var parentId = $(parent).attr('id');
            var showAlias = $('#' + parentId + ' .title').children().filter('input, select').val();
            var alias = $('#' + parentId + ' .title').data('slug');
            var propertyName = $(property).val();
            var propertyField = $(property).next().next();
            // We need to avoid the cache value for this attribute
            var propertyFromAnotherBox = propertyField.attr('data-boxproperty');
            var propertyValue = propertyField.val();

            // Treatment for the lookup 'has some value & has no value'
            if(lookup === 'isnull') {
                propertyValue = true;
            } else if(lookup === 'isnotnull') {
                lookup = 'isnull';
                propertyValue = false;
            }

            // Treatment for the lookup 'is between'
            if(lookup === 'between') {
                propertyValue1 = propertyValue;
                propertyValue2 = $(property).next().next().next().val();
                propertyValue = new Array(propertyValue1, propertyValue2);
            }

            // We store the datatype
            var fieldId = $(property).parent().attr('id');
            var datatype = $('#' + fieldId + ' .select-property option:selected').data('datatype');

            // If exists, we store the aggregate and the value for distinct
            var aggregate = $(property).prev().find(":selected");
            var aggregateValue = $(aggregate).val();
            var aggregateDistinct = '';
            // We store the slug used for the query
            var headerSlug = '';
            // We store how we want to show the alias in the headers
            var headerAlias = '';
            // We check if the aggregate value is not the "choose one" option
            if(aggregateValue != '') {
                aggregateDistinct = $(aggregate).data("distinct");
                // We check if we have to include the distinct
                distinctValue = "";
                distinctSlug = "";
                if(aggregateDistinct) {
                    distinctValue = " Distinct";
                    distinctSlug = "DISTINCT ";
                }
                // If we have aggregate, we build an appropiate alias
                headerSlug = aggregateValue + '(' + distinctSlug + alias + '.' + propertyName + ')';
                headerAlias = aggregateValue + distinctValue + '(' + showAlias + '.' + propertyName + ')';
            } else {
                aggregateValue = false;
                // We build the appropiate alias
                headerSlug = alias + '.' + propertyName
                headerAlias = showAlias + '.' + propertyName
            }

            // We store the checked properties
            if(!propertiesChecked[alias])
                propertiesChecked[alias] = new Array();
            if($(property).prev().prev().attr('checked')) {
                var propertiesDict = {};
                propertiesDict["property"] = $(property).val();
                propertiesDict["aggregate"] = aggregateValue;
                propertiesDict["distinct"] = aggregateDistinct;
                propertiesDict["datatype"] = datatype;
                propertiesDict["alias"] = headerSlug;
                propertiesDict["display_alias"] = headerAlias;
                propertiesChecked[alias].push(propertiesDict);
            }

            // We check if we have and/or option
            var andOrId = $(property).parent().attr('id');
            var andOrVal = $('#' + andOrId + ' .and-or-option select').val();

            if((lookup != "undefined") && (lookup != null)) {
                // We use the key word 'property_box' to know that we have
                // a property from another box
                if(propertyFromAnotherBox !== undefined) {
                    // Let's treat the property to check that there's no
                    // problem with it
                    datatype = 'property_box';
                    propertyValue = propertyFromAnotherBox;
                    // We need to check if we have aggregates in the
                    // conditions. In that case, our query has a different
                    // cypher so we need to store that useful fields.
                    // Let's check if we have an aggregate
                    var propSplit = propertyFromAnotherBox.split("(");
                    var existsAgg = diagram.aggregates.indexOf(propSplit[0]);
                    if(existsAgg !== -1) {
                        // We have an aggregate and need to change the query,
                        // but we need the slug.property_name, not the
                        // property_id
                        var propertyWithValue = propertyField.data('withvalue');
                        meta_dict["with_statement"][propertyWithValue] = '`' + propertyWithValue + '`';
                    }
                    // Also, we are going to include in the meta dict the 
                    // fieldId of the property, to get it back in case that
                    // the property is not selected or with conditions.
                    var selectOtherBoxes = $(property).next().next().next();
                    var optionFieldId = $('option:selected', selectOtherBoxes).attr('data-fieldid');
                    var isChecked = $('#' + optionFieldId + ' .checkbox-property').attr('checked');
                    if(isChecked === undefined) {
                        var propName = $('option:selected', selectOtherBoxes).attr('data-propname');
                        meta_dict["boxes_properties"][optionFieldId] = propName;
                    }
                }

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

                if(datatype) {
                    conditionArray.push(datatype);
                } else {
                    conditionArray.push("undefined");
                }

                conditionsArray.push(conditionArray);
            }
        });

        query["conditions"] = conditionsArray;

        // Origin
        var originsArray = new Array();
        var elements = $('input, option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var origin = {};
            var type = "relationship";
            // We check the type of the origin
            if($(element).attr("class").indexOf("nodetype") >= 0)
                type = "node";
            var alias = $(element).val();
            var type_id = $(element).data('modelid');
            var slug = $(element).parent().parent().data('slug');
            origin.alias = alias;
            origin.type = type;
            origin.type_id = type_id;
            origin.slug = slug;
            originsArray.push(origin);

            // We need to check if the slug has to be included in the
            // with statement
            var includeSlug = $.isEmptyObject(meta_dict["with_statement"]);
            if(!includeSlug) {
                meta_dict["with_statement"][slug] = slug;
            }
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
            // We need to check if the targetId contains 'title',
            // because we use that div for reflexive connections
            targetArrayElements = targetId.split('-');
            lastPosition = targetArrayElements.length - 1;
            isTitle = targetArrayElements[lastPosition];
            if(isTitle == 'title') {
                // If contains title, we use the sourceId as targetId
                targetId = sourceId;
            }

            // We get the selectors for every component to build
            // the json correctly
            var relationSelector = $('#' + relationId + ' .title');
            if(relationSelector.length == 0) {
                alert("There's been an error in the relationship " + sourceId + "-" + targetId + ". Please remove it and try again");
            }

            var relationSlug = $('#' + relationId + ' .title').data('slug');
            var relationAlias = $('#' + relationId + ' .title').children().filter('input, select').val();
            var relationModelId = relationSelector.data('modelid');
            relation.slug = relationSlug;
            relation.alias = relationAlias;
            // We save the relation slug to not be confused in queries
            // with the same box alias
            relation.type = 'relationship';
            relation.type_id = relationModelId;

            var sourceSelector = $('#' + sourceId + ' .title');
            var sourceAlias = $('#' + sourceId + ' .title').data('slug');
            var sourceModelId = sourceSelector.data('modelid');
            source.alias = sourceAlias;
            source.type = 'node';
            source.type_id = sourceModelId;

            var targetSelector = $('#' + targetId + ' .title');
            var targetAlias = $('#' + targetId + ' .title').data('slug');
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
        var elements = $('input, option').filter(function(){ return $(this).attr("class") && $(this).attr("class").match(/(option-reltype|option-nodetype)./) && $(this).attr("selected");});
        $.each(elements, function(index, element) {
            var result = {};

            var alias = $(element).parent().parent().data('slug');
            var properties = propertiesChecked[alias];

            if(!properties)
                properties = new Array();

            result.alias = alias;
            result.properties = properties;

            resultsArray.push(result);
        });

        query["results"] = resultsArray;

        query["meta"] = meta_dict

        return query;
    };

    /**
     * Load the query
     */
    diagram.loadQuery = function(jsonQuery) {
        try {

            jsonDict = JSON.parse(jsonQuery);
            types = jsonDict["aliases"]["types"];
            nodetypes = {};
            reltypes = {};
            origins = jsonDict["query"]["origins"];
            originsLength = origins.length;
            conditions = jsonDict["query"]["conditions"];
            conditionsLength = conditions.length;
            conditionsDict = {};
            patterns = jsonDict["query"]["patterns"];
            patternsLength = patterns.length;
            checkboxes = jsonDict["checkboxes"];
            aggregates = jsonDict["aggregates"];
            aggregatesRels = jsonDict["aggregatesRels"];
            sortingParams = jsonDict["sortingParams"];
            meta = jsonDict["query"]["meta"];

            var fieldIndex = 0;
            var fieldIndexRel = 0;
            var conditionsIndex = 0;

            // We save the node types to load the boxes
            for(var i = 0; i < originsLength; i++) {
                if(origins[i].type == "node") {
                    // We check if we have the slug value or we use the alias
                    // for older queries
                    nodeAlias = origins[i].alias;
                    if(origins[i].slug)
                        nodeAlias = origins[i].slug
                    nodetypes[nodeAlias] = types[nodeAlias];
                } else {
                    relAlias = origins[i].alias;
                    if(origins[i].slug)
                        relAlias = origins[i].slug
                    reltypes[relAlias] = types[relAlias];
                }
            }

            // We store the conditions in a dictionary
            var conditionsAlias = [];
            for(var i = 0; i < conditionsLength; i++) {
                var conditionsArray = [];
                // alias
                alias = conditions[i][1][1];
                // lookup
                lookup = jsonDict["query"]["conditions"][i][0];
                conditionsArray.push(lookup);
                // property
                property = jsonDict["query"]["conditions"][i][1][2];
                conditionsArray.push(property);
                // value
                value = jsonDict["query"]["conditions"][i][2];
                conditionsArray.push(value);
                // We have to check the and-or value
                andOr = jsonDict["query"]["conditions"][i][3];
                conditionsArray.push(andOr);

                if(!conditionsDict[alias])
                    conditionsDict[alias] = [];
                conditionsDict[alias].push(conditionsArray);
            }

            for(key in nodetypes) {
                if(nodetypes.hasOwnProperty(key)) {
                    id = nodetypes[key].id;
                    // We change the counter to get the correct id of the box
                    counter = parseInt(id.split("-")[1]);
                    diagram.Counter = counter - 1;
                    // This is to replace the alias if we have edited it.
                    // We need to maintain the old logic.
                    var fieldsKey = "";
                    alias = nodetypes[key].alias;
                    if(alias === undefined) {
                        alias = key;
                    }

                    if(jsonDict["fields"].hasOwnProperty(alias)) {
                        fieldsKey = alias;
                    } else {
                        fieldsKey = key;
                    }

                    typename = nodetypes[key].typename;
                    leftPos = nodetypes[key].left;
                    topPos = nodetypes[key].top;
                    // Load the box and set the positions
                    diagram.loadBox(typename);
                    $('#' + id).css({
                        "left": leftPos,
                        "top": topPos
                    });
                    fields = jsonDict["fields"][fieldsKey];
                    // Load the conditions for the box
                    // This loop could be replaced if we have a
                    // dict instead an array
                    var boxFields = 0;
                    fieldLoopCounter = diagram.fieldCounter;
                    for(var i = 0; i < fields.length; i++) {
                        boxFields++;
                        // If we have more than one field, we add
                        // a new field
                        if(boxFields > 1) {
                            $('#' + id + ' .select-and-or').change();
                            fieldLoopCounter++;
                        }

                        // We need to take into account the old queries
                        fieldIndex = fields[i];
                        if(isNaN(parseInt(fieldIndex))) {
                            fieldIndex = fieldIndex.replace(/\D/g, "");
                        }
                        // We need to set the correct value for the id
                        var newFieldIndex = 'field' + fieldIndex;
                        
                        // Before to set the new index, we need to check if
                        // that index is already used in the boxes.
                        var existsIndex = $('#' + id + " #field" + fieldLoopCounter).length;
                        if(existsIndex > 1) {
                            // Exists, so we need to get the last element
                            $($('#' + id + " #field" + fieldLoopCounter)[1]).attr('id', newFieldIndex);
                        } else {
                            // Don't worry, we set the index without problems
                            $('#' + id + " #field" + fieldLoopCounter).attr('id', newFieldIndex);
                        }

                        // We need to set the fieldid data of some fields.
                        // Look, we use now the new fieldIndex.
                        $('#' + id + " #field" + fieldIndex + ' .select-property').attr('data-fieldid', newFieldIndex);
                        $('#' + id + " #field" + fieldIndex + ' .remove-field-row').attr('data-fieldid', newFieldIndex);

                        // We check if we have conditions
                        if(jsonDict["fieldsConditions"][fieldLoopCounter - 1]) {
                            conditions = conditionsDict[key][conditionsIndex];
                            // lookup
                            lookup = conditions[0];
                            // property
                            property = conditions[1];
                            // value
                            // we check if the lookup is 'is between'
                            if(lookup == "between") {
                                value1 = conditions[2][0];
                                value2 = conditions[2][1];
                            } else {
                                value = conditions[2];
                            }
                            // We have to check the and-or value
                            andOr = conditions[3];
                            // We set the values in the correct position
                            $('#' + id + " #field" + fieldIndex + " .select-property").val(property);
                            $('#' + id + " #field" + fieldIndex + " .select-property").change();
                            $('#' + id + " #field" + fieldIndex + " .select-lookup").val(lookup);
                            $('#' + id + " #field" + fieldIndex + " .select-lookup").change();
                            // If the lookup is "is between", we have two inputs
                            if(lookup == "between") {
                                $($('#' + id + " #field" + fieldIndex + " .lookup-value")[0]).val(value);
                                $($('#' + id + " #field" + fieldIndex + " .lookup-value")[1]).val(value);
                            } else {
                                $('#' + id + " #field" + fieldIndex + " .lookup-value").val(value);
                            }
                            if(andOr != "not") {
                                $('#' + id + " #field" + fieldIndex + " .select-and-or").val(andOr);
                            }
                            conditionsIndex++;
                        } else {
                            // If we dont have conditions, we let the user to change the lookups or the 'and-or' select
                            $('#' + id + " #field" + fieldIndex + " .select-property").change();
                        }
                    }
                    conditionsIndex = 0;
                    // We check if we need to change the alias
                    // (edit alias feature)
                    diagram.loadQueryWithAlias(id, alias, typename, true)
                    // We update the nodetypeCounter
                    newNodeTypeCounter = alias.replace(/\D/g, "");
                    // We need to take into account if this last alias is
                    // edited by the user, because we obtain a counter with
                    // 0 value
                    if(diagram.nodetypesCounter[typename] <= newNodeTypeCounter)
                        diagram.nodetypesCounter[typename] = newNodeTypeCounter;
                }
                // We check if we have to show the 'alias selects' for this type
                diagram.showSelects(typename, "node");
                // The next lines is to select the new alias in the box
                var selectsLength = $('.select-nodetype-' + typename).length;
                var selectsElem = $('.select-nodetype-' + typename)[selectsLength - 1];
                var optionsLength = $(selectsElem).children().length;
                var optionElem = $(selectsElem).children()[optionsLength - 1];
                $(optionElem).attr('selected', 'selected');
            }
            // Once we have loaded the boxes, we update the
            // diagram.fieldsForNodes.
            // But again, we need to take into account the old queries.
            if(fieldsKey === key)
                diagram.fieldsForNodes = jsonDict["fields"];

            // Load the relationships between the boxes
            for(var i = 0; i < patternsLength; i++) {
                var source = jsonDict["query"]["patterns"][i].source.alias;
                var sourceId = types[source].id;

                var target = jsonDict["query"]["patterns"][i].target.alias;
                var targetId = types[target].id;

                var queryRelation = jsonDict["query"]["patterns"][i].relation;
                relation = queryRelation.alias;
                relationAlias = queryRelation.alias;
                if(queryRelation.slug) {
                    relation = queryRelation.slug;
                }
                var idRel = queryRelation.type_id;
                var relationTypeName = types[relation].typename;

                // We need to change the first letter to uppercase
                var relationValue = relationTypeName.charAt(0).toUpperCase() + relationTypeName.slice(1);
                var relationName = relationTypeName;
                var idRelBox = types[relation].id

                // We check if the relationship is of type wildcard
                if(relationValue == "WildcardRel")
                   relationName = "wildcard";

                var uuidSource = sourceId + '-' + relationName + '-source';
                var uuidTarget = targetId + '-target';

                // We need to check if it is a wildcard rel because the name
                // is different
                if(relationValue == "WildcardRel")
                    relationName = relationValue

                $('#' + sourceId + ' .select-rel').val(relationName);
                var labelRel = $('option:selected', '#' + sourceId + ' .select-rel').data('label');
                $('#' + sourceId + ' .select-rel').change();

                // We need to control the reflexive relations
                if(sourceId == targetId) {
                    targetId = sourceId + '-title';
                }

                diagram.addRelation(sourceId, targetId, labelRel, relationName, idRel);

                // We check if we need to show the 'alias selects' for the relationship boxes
                diagram.showSelects(labelRel, "relationship");
                // We check if we need to change the alias
                // (edit alias feature)
                diagram.loadQueryWithAlias(idRelBox, relationAlias, labelRel, false)
            }

            // We will check the conditions for the relationships
            // We create a variable to set up the index for rels 
            // fields
            var setCounterRelsIndex = 0;
            for(key in reltypes) {
                if(reltypes.hasOwnProperty(key)) {
                    // We check if we have fields for the rel
                    if( typeof jsonDict["fieldsRels"] != "undefined") {
                        id = reltypes[key].id;
                        typename = reltypes[key].typename;
                        // We click the button to show the properties
                        $('#' + id + ' #inlineShowHideLink_' + typename).click();
                        // This is to replace the alias if we have edited it.
                        // We need to maintain the old logic.
                        var fieldsKey = "";
                        alias = reltypes[key].alias;
                        if(alias === undefined) {
                            alias = key;
                        }

                        if(jsonDict["fieldsRels"].hasOwnProperty(alias)) {
                            fieldsKey = alias;
                        } else {
                            fieldsKey = key;
                        }
                        fieldsRels = jsonDict["fieldsRels"][fieldsKey];

                        // Load the conditions for the box
                        // This loop could be replace if we have a
                        // dict instead an array
                        var boxFields = 0;
                        fieldLoopCounter = diagram.Counter;
                        for(var i = 0; i < fieldsRels.length; i++) {
                            boxFields++;
                            // If we have more than one field, we add
                            // a new field
                            if(boxFields > 1) {
                                $('#' + id + ' .select-and-or-rel').change();
                                fieldLoopCounter++;
                            }

                            // We need to set the correct value for the id
                            var newFieldIndex = fieldsRels[i];
                            
                            // Let's see if we need to change the index for
                            // the counter of rels fields
                            var newCounterValue = newFieldIndex.split('-')[1];
                            newCounterValue = parseInt(newCounterValue);
                            if(newCounterValue > setCounterRelsIndex)
                                setCounterRelsIndex = newCounterValue;

                            // We get the actual index for the field
                            var lastFieldIndex = $('#' + id + ' .field').length - 1;
                            var actualField = $('#' + id + ' .field')[lastFieldIndex];
                            var indexActualField = $(actualField).attr('id').split('-')[1];

                            // Before to set the new index, we need to check if
                            // that index is already used in the boxes.
                            var existsIndex = $('#' + id + " #field-" + indexActualField + '-' + typename).length;
                            if(existsIndex > 1) {
                                // Exists, so we need to get the last element
                                $($('#' + id + " #field-" + indexActualField + '-' + typename)[1]).attr('id', newFieldIndex);
                            } else {
                                // Don't worry, we set the index without problems
                                $('#' + id + " #field-" + indexActualField + '-' + typename).attr('id', newFieldIndex);
                            }

                            // We need to set the fieldid data of some fields.
                            // Look, we use now the new fieldIndex.
                            $('#' + id + " #" + newFieldIndex + ' .select-property').attr('data-fieldid', newFieldIndex);
                            $('#' + id + " #" + newFieldIndex + ' .remove-field-row-rel').attr('data-fieldid', newFieldIndex);

                            // We check if we have conditions
                            if(jsonDict["fieldsConditions"][fieldLoopCounter]) {
                                conditions = conditionsDict[key][conditionsIndex];
                                // lookup
                                lookup = conditions[0];
                                // property
                                property = conditions[1];
                                // value
                                // we check if the lookup is 'is between'
                                if(lookup == "between") {
                                    value1 = conditions[2][0];
                                    value2 = conditions[2][1];
                                } else {
                                    value = conditions[2];
                                }
                                // We have to check the and-or value
                                andOr = conditions[3];
                                // We set the values in the correct position
                                $('#' + id + " #" + newFieldIndex + " .select-property").val(property);
                                $('#' + id + " #" + newFieldIndex + " .select-property").change();
                                $('#' + id + " #" + newFieldIndex + " .select-lookup").val(lookup);
                                $('#' + id + " #" + newFieldIndex + " .select-lookup").change();
                                // If the lookup is "is between", we have two inputs
                                if(lookup == "between") {
                                    $($('#' + id + " #" + newFieldIndex + " .lookup-value")[0]).val(value);
                                    $($('#' + id + " #" + newFieldIndex + " .lookup-value")[1]).val(value);
                                } else {
                                    $('#' + id + " #" + newFieldIndex + " .lookup-value").val(value);
                                }
                                if(andOr != "not") {
                                    $('#' + id + " #" + newFieldIndex + " .select-and-or-rel").val(andOr);
                                }
                                conditionsIndex++;
                            } else {
                                // If we dont have conditions, we let the user to change the lookups or the 'and-or' select
                                $('#' + id + " #" + newFieldIndex + " .select-property").change();
                            }
                        }
                    }
                    conditionsIndex = 0;
                }
            }
            // Once we have loaded the boxes, we update the
            // diagram.savedFieldsForRels
            if(fieldsKey === key)
                diagram.savedFieldsForRels = jsonDict["fieldsRels"];
            
            // We need to set the diagram.fieldCounterRel to the last
            // element
            if(setCounterRelsIndex !== 0) {
                diagram.fieldRelsCounter = setCounterRelsIndex;
            }

            // We check the checkboxes to return
            for(key in checkboxes) {
                if(checkboxes.hasOwnProperty(key)) {
                    // After update the way to get the checkboxes,
                    // now we have that the fieldIndex is equals to
                    // #field"Id". So, we need to add the #field part
                    // for a correct execution in the saved queries.
                    var property = checkboxes[key];
                    var fieldIndex = key;
                    if(!isNaN(parseInt(key))) {
                        key = parseInt(key) + 1;
                        fieldIndex = "field" + key;
                    }
                    $("#" + fieldIndex + " .select-property").val(property);
                    $("#" + fieldIndex + ' .checkbox-property').click();

                    // If we don't have lookups, we need to "change" the select
                    // to set the property in the other selects for properties
                    // of other boxes
                    var hasLookup = $('#' + fieldIndex + ' .select-lookup').val();
                    if(hasLookup === null)
                        $("#" + fieldIndex + " .select-property").change();
                }
            }

            // We check all the necessary logic for the aggregates
            var aggregatesClicked = 0;
            var prevIdBox = "";
            for(key in aggregates) {
                if(aggregates.hasOwnProperty(key)) {
                    var selector = $("#field" + key + " .select-aggregate");
                    var idBox = selector.parent().parent().parent().parent().parent().attr('id');
                    var typename = idBox.split('-')[2];
                    // We need to click only one time, because we don't want to
                    // hide the aggregates
                    if(idBox !== prevIdBox) {
                        prevIdBox = idBox;
                        aggregatesClicked = 0;
                    }

                    if((aggregatesClicked === 0) && (prevIdBox === idBox)) {
                        $('#' + idBox + ' #inlineAdvancedMode_' + typename).click();
                        aggregatesClicked++;
                    }
                    // We set the aggregate value
                    var aggregateValue = aggregates[key][0];
                    var aggregateDistinct = aggregates[key][1];
                    $('option[value="' + aggregateValue + '"][data-distinct=' + aggregateDistinct + ']', selector).attr("selected", "selected");
                    $(selector).change();
                }
            }

            // We check all the necessary logic for the aggregates in relationships
            var aggregatesClicked = 0;
            var prevIdBox = "";
            for(key in aggregatesRels) {
                if(aggregatesRels.hasOwnProperty(key)) {
                    var aggregateValue = aggregatesRels[key][0];
                    var aggregateDistinct = aggregatesRels[key][1];
                    var idBox = aggregatesRels[key][2];
                    var selector = $("#" + key + " .select-aggregate");
                    var typename = idBox.split('-')[2];
                    // We need to click only one time, because we don't want to
                    // hide the aggregates
                    if(idBox !== prevIdBox) {
                        prevIdBox = idBox;
                        aggregatesClicked = 0;
                    }

                    if((aggregatesClicked === 0) && (prevIdBox === idBox)) {
                        $('#' + idBox + ' #inlineAdvancedMode_' + typename).click();
                        aggregatesClicked++;
                    }
                    aggregatesClicked++;
                    $('option[value="' + aggregateValue + '"][data-distinct=' + aggregateDistinct + ']', selector).attr("selected", "selected");
                    $(selector).change();
                }
            }

            // Here, we are going to check if we need to set properties that
            // are not included in the conditions or checked.
            // We need to take into account saved old queries
            try {
                var extraProperties = meta["boxes_properties"];
                for(key in extraProperties) {
                    if(extraProperties.hasOwnProperty(key)) {
                        // The key is the fieldId and the value is the property
                        // value
                        var value = extraProperties[key];
                        $('#' + key + ' .select-property').val(value).change();
                    }
                }
            } catch(e) {
                // It is a old query, so we do nothing
            }

            // Now, we need to check if the lookup value of some condition is
            // a property of another box. In that case, we need to set
            // it correctly
            for(key in conditionsDict) {
                if(conditionsDict.hasOwnProperty(key)) {
                    // We need to iterate over all the conditions of the key
                    var conditions = conditionsDict[key];
                    $.each(conditions, function(index, condition) {
                        // We need to check if we have a property from another
                        // box
                        // Lookup
                        lookup = condition[0];
                        // Values
                        // we check if the lookup is 'is between'
                        if(lookup == "between") {
                            value1 = condition[2][0];
                            value2 = condition[2][1];
                        } else {
                            value = condition[2];
                            var isOtherBoxProp = $('option[value="' + value + '"]', $('.select-other-boxes-properties')).length;
                            if(isOtherBoxProp > 0) {
                                // We set the lookup value correctly
                                var lookupInput = $('.lookup-value').filter(
                                        function(index, elem) {
                                            if($(elem).val() === value)
                                                return elem;
                                        }
                                    );
                                $(lookupInput).next().val(value).change();
                            }
                        }
                    });
                }
            }   

            // Once all the boxes are setting up, we set the sorting params
            for(key in sortingParams) {
                if(sortingParams.hasOwnProperty(key)) {
                    var elementId = "#id_" + key;
                    // We set the value for that element
                    var elementValue = sortingParams[key];
                    // We need to check if the key is the distinct checkbox,
                    // because the treatment is different
                    if(key == "distinct_result") {
                        $(elementId).prop('checked', elementValue);
                    } else {
                        $(elementId).val(elementValue);
                    }
                }
            }

            jsPlumb.repaintEverything();
        } catch(error) {
            console.log(error.stack);
        }
    };

    /**
     * Save the query
     */
    diagram.saveQuery = function() {
        var saveElements = {};
        var query = diagram.generateQuery();
        saveElements["query"] = query;

        // The input is for the edit alias option
        var elements = $('.title select, .title input');
        var checkboxes = $('.checkbox-property');
        var aggregates = $('.select-aggregate');
        var fieldsDict = {};
        var aliasDict = {};
        var typesDict = {};
        var checkboxesDict = {};
        var aggregatesDict = {};
        var aggregatesDictRels = {};
        var fieldsConditionsDict = {};
        var sortingParamsDict = {};

        // We get the id, typename, left and top of the boxes
        $.each(elements, function(index, element) {
            var valuesDict = {};
            var parent = $(element).parent().parent();

            var alias = $(element).val();
            var id = $(parent).attr('id');
            var typename = $(element).attr('class').substring(15);
            // This is for check if we have a relationship or a node
            if(typename.substring(0,1) == "-")
                typename = typename.substring(1);
            var left = $(parent).css('left');
            var top = $(parent).css('top');

            valuesDict['id'] = id;
            valuesDict['alias'] = alias;
            valuesDict['typename'] = typename;
            valuesDict['left'] = left;
            valuesDict['top'] = top;

            // We obtain the slug value to save the values
            var slugValue = $(element).parent().data('slug');

            typesDict[slugValue] = valuesDict;
        });
        aliasDict["types"] = typesDict;

        // We get the checkboxes checked and the property to return
        $.each(checkboxes, function(index, checkbox) {
            if($(checkbox).prop('checked')) {
                var fieldIndex = $(checkbox).parent().attr('id');
                checkboxesDict[fieldIndex] = $(checkbox).next().next().val();
            }
        });

        // We get the aggregates if they exist
        $.each(aggregates, function(index, aggregate) {
            // We get the value to know if we treat relationships or nodes
            var diagramSelector = $(aggregate).parent().parent().parent().parent().parent().parent();
            if($(diagramSelector).attr('id') == "diagramContainer") {
                // This branch if for the relationships case
                var aggregateValue = $(aggregate).val();
                if(aggregateValue) {
                    var aggregateDistinct = $('option:selected', aggregate).data('distinct');
                    var idBoxRel = $(aggregate).parent().parent().parent().parent().parent().attr('id');
                    var fieldId = $(aggregate).parent().attr('id');
                    aggregatesDictRels[fieldId] = [aggregateValue, aggregateDistinct, idBoxRel];
                }
            } else {
                // This branch if for the nodes case
                var aggregateValue = $(aggregate).val();
                if(aggregateValue) {
                    var aggregateDistinct = $('option:selected', aggregate).data('distinct');
                    // We get the index field
                    var fieldIndex = $(aggregate).parent().attr('id');
                    var onlyIndex = parseInt(fieldIndex.replace(/\D/g, ""));
                    aggregatesDict[onlyIndex] = [aggregateValue, aggregateDistinct];
                }

            }
        });

        // We get the fields that are conditions to construct the box properly
        $.each(checkboxes, function(index, checkbox) {
            var lookup = $(checkbox).next().next().next().val();
            var inputLookup = $(checkbox).next().next().next().next().val();
            if(lookup && inputLookup) {
                fieldsConditionsDict[index] = true;
            } else {
                fieldsConditionsDict[index] = false;
            }
        });
        saveElements['aliases'] = aliasDict;

        // We get the params of the sorting settings and save them into
        // the fields dict
        sortingParamsDict['rows_number'] = $('#id_rows_number').val();
        sortingParamsDict['distinct_result'] = $('#id_distinct_result').prop('checked');
        sortingParamsDict['show_mode'] = $('#id_show_mode').val();
        sortingParamsDict['select_order_by'] = $('#id_select_order_by').val();
        sortingParamsDict['dir_order_by'] = $('#id_dir_order_by').val();

        // We store all the important values
        fieldsDict['fields'] = diagram.fieldsForNodes;
        fieldsDict['fieldsRels'] = diagram.savedFieldsForRels;
        fieldsDict['checkboxes'] = checkboxesDict;
        fieldsDict['aggregates'] = aggregatesDict;
        fieldsDict['aggregatesRels'] = aggregatesDictRels;
        fieldsDict['fieldsConditions'] = fieldsConditionsDict;
        fieldsDict['fieldRelsCounter'] = diagram.fieldRelsCounter;
        fieldsDict['sortingParams'] = sortingParamsDict;

        saveElements['fields'] = fieldsDict;

        return saveElements;
    };

    /**
     * Interactions functions
     * These functions allow the interaction between the user and the boxes.
     */

    /**
     * Add box type to the diagram
     */
    $('.add-box').on('click', function() {
        var $this = $(this);
        var nodeType = $this.data("type");
        var modelName = diagram.loadBox(nodeType);

        // We check if we have more than one box to show the selects for the alias
        diagram.showSelects(nodeType, "node");

        // The next lines is to select the new alias in the box
        var elem = $('.select-nodetype-' + nodeType + ' #' + modelName + (diagram.nodetypesCounter[nodeType])).length - 1;
        $($('.select-nodetype-' + nodeType + ' #' + modelName + (diagram.nodetypesCounter[nodeType]))[elem]).attr('selected', 'selected');
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
        var boxalias = $this.data("slug");
        var idBox = $this.data("idbox");
        var idAllRels = $this.data("idallrels");

        divField = diagram.addFieldRow(graphName, modelName, parentId, typeName, boxalias, idBox, idAllRels);

        $("#" + parentId).append(divField);

        // Recalculate anchor for source endpoints
        diagram.recalculateAnchor(idBox, idAllRels);

        jsPlumb.repaintEverything();
    });

    /**
     * Add field row inside a box type
     */
    $("#diagramContainer").on('change', '.select-and-or', function() {
        var $this = $(this);
        // We check if the field is the last to field to allow the addition
        // of a new field
        var field = $this.parent().parent();
        if($(field).next().length == 0) {
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
        }
    });

    /**
     * Add field row inside a rel type
     */
    $("#diagramContainer").on('change', '.select-and-or-rel', function() {
        var $this = $(this);
        
        var idBox = $this.parent().parent().parent().parent().parent().parent().attr('id');
        var boxAlias = $('#' + idBox + ' .title').data('slug');
        var label = $this.data("label");
        var parentId = $this.data("parentid");

        // We check if the field is the last to field to allow the addition
        // of a new field
        var field = $this.parent().parent();
        if($(field).next().length == 0) {
            divField = diagram.addFieldRelRow(boxAlias, label, parentId, idBox);

            $("#" + parentId).append(divField);
        }
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

        // We store the selector for the and/or select for nodes
        var selectorAndOr = '.select-and-or';
        // We call to the function to remove the field
        diagram.removeFields(parentId, fieldId, selectorAndOr);
        // Recalculate anchor for source endpoints
        diagram.recalculateAnchor(idBox, idAllRels);

        jsPlumb.repaintEverything();

        // We remove this property of all the selects with properties
        // of boxes
        var optionsOtherBoxesProps = $('option', '.select-other-boxes-properties');
        $.each(optionsOtherBoxesProps, function(index, elem) {
            if($(elem).data('fieldid') === fieldId)
                $(elem).remove();
        });

        // We update the diagram.fieldsForNodes for this type
        var slug = $('#' + idBox + ' .title').data('slug');
        var fieldIndex = diagram.fieldsForNodes[slug].indexOf(fieldId);
        diagram.fieldsForNodes[slug].splice(fieldIndex, 1);
    });

    /**
     * Remove field row inside a box type
     */
    $("#diagramContainer").on('click', '.remove-field-row-rel', function() {
        var $this = $(this);
        var fieldId = $this.data("fieldid");
        var parentId = $this.data("parentid");
        var idBox = $this.parent().parent().parent().parent().parent().attr('id');

        // We store the selector for the and/or select for rels
        var selectorAndOr = '.select-and-or-rel';
        // We call to the function to remove the field
        diagram.removeFields(parentId, fieldId, selectorAndOr);

        // We update the diagram.fieldsForRels for this type
        var slug = $('#' + idBox + ' .title').data('slug');
        var fieldIndex = diagram.savedFieldsForRels[slug].indexOf(fieldId);
        diagram.savedFieldsForRels[slug].splice(fieldIndex, 1);
    });

    /**
     * Add a new relationship row for that box type
     */
    $("#diagramContainer").on('change', '.select-rel', function() {
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

        // We check if the box already has a connection of that type
        var existsRel = false;
        var boxConnections = jsPlumb.select({source:idBox});
        boxConnections.each(function(elem) {
            var idBoxRel = elem.idrel;
            // We split the idBoxRel value to check the rel name
            var idBoxRelName = idBoxRel.split('-')[2];
            if(idBoxRelName == name) {
                existsRel = true;
            }
        });
        // We check if we have already selected that relation
        if(!existsRel && ($('#div-' + relationId).length == 0)) {

            // We check if we have the type in the reltypesList. If not,
            // we create it.
            if(!diagram.reltypesList[name]) {
                diagram.reltypesList[name] = new Array();
            }

            divAllRel = $("<DIV>");
            divAllRel.addClass("div-list-rel");
            divAllRel.attr("id", "div-" + relationId);

            listRelElement = $("<LI>");
            listRelElement.addClass("list-rel");

            listRelElement.html(label);
            if (label.length > 5) {
                listRelElement.html(label.substr(0, 20) +"…");
            }
            listRelElement.attr("title", label);
            listRelElement.attr("alt", label);

            if(source) {
                var relIndex = diagram.relindex[idBox];
                // calculate anchor
                // We need idBox and idAllRels
                var anchor = diagram.calculateAnchor(idBox, idAllRels, relIndex);
                if(source) {
                    var uuidSource = relationId + "-source";
                    if(!jsPlumb.getEndpoint(uuidSource)) {
                        var endpointSource = jsPlumb.addEndpoint(idBox, { uuid:uuidSource, connector: "Flowchart"}, diagram.getRelationshipOptions('source', name, label, idrel, anchor));
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
            removeRelation.attr('data-name', name);

            // Remove relation icon
            removeRelationIcon = $("<I>");
            removeRelationIcon.addClass("fa fa-minus-circle");
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

        $('.endpoint-image').attr("title", "drag me!")

        jsPlumb.repaintEverything();

        // We check if the target type is already loaded
        // If it doesn't, we load the type and create the connection
        // between the two types
        diagram.checkTargetType(scopeSource, relationId, idBox, label, name, idrel);

        // We restore the "choose one" value
        $this.val("choose one");
    });

    /**
     * Handler to take into account the change the selects for other boxes
     * properties when we change the selects of the boxes
     */
    $("#diagramContainer").on('change', 'select[class*="select-nodetype-"]', function() {
        // We check if we need to change the alias of the select of other
        // properties boxes
        var $this = $(this);
        var newAlias = $this.val();
        var optionsOtherBoxesProps = $('option', '.select-other-boxes-properties');
        var boxSlug = $this.parent().data('slug');
        $.each(optionsOtherBoxesProps, function(index, elem) {
            var optionSlug = $(elem).data('slugvalue');
            if(optionSlug === boxSlug) {
                // We check if we have an aggregate selected
                // If the length is bigger than 1
                var oldOptionVal = $(elem).html();
                var isThereAgg = oldOptionVal.split("(").length > 1;
                if(isThereAgg) {
                    var oldOptionValSplitted = oldOptionVal.split(/["(",")"]+/);
                    var aggregateValue = oldOptionValSplitted[0];
                    var oldValue = oldOptionValSplitted[1];
                    var oldValueWithoutAgg = oldValue.split(".");
                    var oldAlias = oldValueWithoutAgg[0];
                    
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldValueWithoutAgg[1];
                    var newOptionVal = aggregateValue + "(" + newOptionVal + ")";
                    $(elem).html(newOptionVal);
                } else {
                    var oldOptionValSplitted = oldOptionVal.split(".");
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldOptionValSplitted[1];
                    $(elem).html(newOptionVal);
                }
                // We need to check if the option is selected to change the
                // actual value of the lookup input
                var $lookupInput = $(elem).parent().prev();
                var lookupValue = $lookupInput.val();
                //var isSelected = $(elem).prop('selected');
                var isSelected = lookupValue === oldOptionVal;
                if(isSelected) {
                    // We get the lookup
                    var $lookupInput = $(elem).parent().prev();
                    // We change the lookup input
                    $lookupInput.val(newOptionVal);
                }
            }
        });
    });

    /**
     * We check if we have one property clicked at least, to allow the
     * executing of the query.
     */
    $("#diagramContainer").on('change', '.checkbox-property', function() {
        var checkboxes = $('.checkbox-property');
        var checkBoxesClicked = checkboxes.filter(function() {
            return $(this).prop('checked');
        }).length;
        if(checkBoxesClicked > 0) {
            $runQuery = $('#run-query');
            $runQuery.prop('disabled', false);
            $runQuery.css({
                'color': '#348E82',
                'background-color': '#D6E7DF'
            });
        } else {
            $runQuery = $('#run-query');
            $runQuery.prop('disabled', true);
            $runQuery.css({
                'color': '#9b9b9b',
                'background-color': '#f2f2f2'
            });
        }

        // In this part we are going to treat the adding or removing
        // of the property in the order by select
        var $this = $(this);
        var fieldId = $this.parent().attr('id');
        var propertyValue = $this.next().next().val();
        var titleDiv = $this.parent().parent().parent().parent().prev();
        var boxSlug = $(titleDiv).data('slug');
        var boxAlias = $('select', titleDiv).val();

        // We use the slug for the value and alias for the html
        var orderByFieldVal = boxSlug + '.' + propertyValue;
        var orderByFieldHTML = boxAlias + '.' + propertyValue;

        // We check if there is an aggregate selected
        var aggregate = $this.next().val();

        var distinctValue = "";
        var distinctHTML = "";
        var distinct = $('option:selected', $this).data('distinct');
        if(distinct) {
            distinctValue = "DISTINCT ";
            distinctHTML = " Distinct";
        }

        if(aggregate != '') {
            orderByFieldVal = aggregate + '(' + distinctValue + orderByFieldVal + ')';
            orderByFieldHTML = aggregate + distinctHTML + '(' + orderByFieldHTML + ')';
        } else {
            orderByFieldVal = boxSlug + '.' + propertyValue;
            orderByFieldHTML = boxAlias + '.' + propertyValue;
        }

        if($this.prop("checked")) {
            // We add the orderByField to the select
            var selectNewOption = $("<OPTION>");
            selectNewOption.attr('data-fieldid', fieldId);
            selectNewOption.attr('value', orderByFieldVal);
            selectNewOption.html(orderByFieldHTML);
            $('#id_select_order_by').append(selectNewOption);
        } else {
            // We remove the option because the checbox is non clicked
            $('#id_select_order_by option[data-fieldid="' + fieldId + '"]').remove();
        }
    });

    /**
     * We check if we need to change the property name in the order by
     * select when we select an aggregate.
     */
    $("#diagramContainer").on('change', '.select-aggregate', function() {
        var $this = $(this);
        var checkboxClicked = $this.prev().prop('checked');
        var fieldId = $this.parent().attr('id');
        var propertyValue = $this.next().val();
        var titleDiv = $this.prev().parent().parent().parent().parent().prev();
        var boxSlug = $(titleDiv).data('slug');
        var boxAlias = $('select', titleDiv).val();
        var idBox = $this.parent().parent().parent().parent().parent().attr('id');

        var orderByFieldVal = boxSlug + '.' + propertyValue;
        var orderByFieldHTML = boxAlias + '.' + propertyValue;
        // We add the new option with the aggregate in case that the
        // aggregate is distinct to '' (None option)
        var aggregate = $this.val();

        var distinctValue = "";
        var distinctHTML = "";
        var distinct = $('option:selected', $this).data('distinct');
        if(distinct) {
            distinctValue = "DISTINCT ";
            distinctHTML = " Distinct";
        }

        orderByFieldVal = aggregate + '(' + distinctValue + orderByFieldVal + ')';
        orderByFieldHTML = aggregate + distinctHTML + '(' + orderByFieldHTML + ')';
        if(aggregate == '') {
            orderByFieldVal = boxSlug + '.' + propertyValue;
            orderByFieldHTML = boxAlias + '.' + propertyValue;
        }

        if(checkboxClicked) {
            // We check and remove the option because we have a new option
            $('#id_select_order_by option[data-fieldid="' + fieldId + '"]').remove();

            // We add the orderByField to the select
            var selectNewOption = $("<OPTION>");
            selectNewOption.attr('data-fieldid', fieldId);
            selectNewOption.attr('value', orderByFieldVal);
            selectNewOption.html(orderByFieldHTML);
            $('#id_select_order_by').append(selectNewOption);
        }

        // We need to treat the select for the other properties boxes
        var selectOtherBoxesProps = $('.select-other-boxes-properties');

        window.slugValue = boxSlug;
        window.idBox = idBox;
        window.boxProperties = $('#' + idBox + ' .select-property');

        $.each(selectOtherBoxesProps, function(index, elem) {
            // First, we check that the changes are going to be in other boxes
            var anotherIdBox = $(elem).parent().parent().parent().parent().parent().attr('id');

            // We save the value of the lookup input to check if we need to
            // change it
            var lookupInputVal = $(elem).prev().val();
            var sameValue = false;
            var fieldToChange = "";
            // We remove the options that belong to this slug to avoid
            // conflicts
            $('option', $(elem)).filter(
                function(index, option) {
                    if($(option).data('slugvalue') === slugValue) {
                        if($(option).html() === lookupInputVal) {
                            sameValue = true;
                            fieldToChange = $(option).data('fieldid');
                        }
                        $(option).remove();
                    }
                }
            );

            window.selectOtherProps = elem;
            window.sameValue = sameValue;
            window.fieldToChange = fieldToChange;

            if(idBox !== anotherIdBox) {
                $.each(boxProperties, function(index, prop) {
                    var $titleElem = $('#' + idBox + ' .title');
                    var showAlias = $titleElem.children().filter('input, select').val();
                    var slugAlias = $titleElem.data('slug');
                    var propertyId = $('option:selected', $(prop)).data('propertyid');
                    var propertyValue = $(prop).val();
                    var datatype = $('option:selected', $(prop)).data('datatype');
                    var fieldId = $(prop).parent().attr('id');

                    var value = slugAlias + '.' + propertyId;
                    var label = showAlias + '.' + propertyValue;
                    var withValue = slugAlias + '.' + propertyValue;

                    // Let's check if an aggregate exists
                    var aggregate = $(prop).prev().val();
                    if(aggregate !== "") {
                        var distinctValue = "";
                        var distinctHTML = "";
                        var distinct = $('option:selected', $(prop).prev()).data('distinct');

                        if(distinct) {
                            distinctValue = "DISTINCT ";
                            distinctHTML = " Distinct";
                        }

                        var newValue = aggregate + '(' + distinctValue + value + ')';
                        var newHTML = aggregate + distinctHTML + '(' + label + ')';
                        var newWithValue = aggregate + '(' + distinctValue + withValue + ')';

                    } else if(aggregate == '') {
                        var newValue = value;
                        var newHTML = label;
                        var newWithValue = withValue;
                    }

                    // The new option for the selects
                    var optionBoxesProperty = $("<OPTION>");
                    optionBoxesProperty.addClass('option-other-boxes-properties');
                    optionBoxesProperty.attr('id', newValue);
                    // We add the slug value to manage the option using this field
                    optionBoxesProperty.attr('data-slugvalue', slugAlias);
                    optionBoxesProperty.attr('data-propname', propertyValue);
                    optionBoxesProperty.attr('data-withvalue', newWithValue);
                    optionBoxesProperty.attr('data-datatype', datatype);
                    optionBoxesProperty.attr('data-fieldid', fieldId);

                    optionBoxesProperty.attr('value', newValue);
                    optionBoxesProperty.html(newHTML);

                    $(elem).append(optionBoxesProperty);

                    // We check if we need to change the value of the lookup 
                    // input
                    if(sameValue) {
                        if(fieldId === fieldToChange) {
                            $(elem).val(newValue).change();
                            $(elem).prev().attr('data-withvalue', newValue);
                            $(elem).prev().val(newHTML);
                        }
                    }
                });
            }
        });
    });

    /**
     * Add the values of the select lookup in relation with the property
     * selected
     */
    $("#diagramContainer").on('change', '.select-property', function() {
        var $this = $(this);
        var idBox = $this.parent().parent().parent().parent().parent().attr('id');
        var fieldId = $this.data("fieldid");
        var selector = "#" + idBox + " #" + fieldId + " .select-lookup";
        var datatype = $('option:selected', this).data("datatype");
        var choices = $('option:selected', this).data("choices");
        var arrayOptions = diagram.lookupsValuesType[datatype];
        var propertyId = $('option:selected', this).data("propertyid");
        var propertyValue = $('option:selected', this).val();

        // We change the disabled prop of the checkbox
        $('#' + idBox + ' #' + fieldId + ' .checkbox-property').prop('disabled', false);

        // We change the disabled prop of the aggregate select
        $('#' + idBox + ' #' + fieldId + ' .select-aggregate').prop('disabled', false);

        // We show the select lookup
        $(selector).css({
            "display": "inline"
        });

        // We show the and-or select for nodes
        $('#' + idBox + ' #' + fieldId + ' .select-and-or').css({
            "display": "inline"
        });

        // We show the and-or select for relationships
        $('#' + idBox + ' #' + fieldId + ' .select-and-or-rel').css({
            "display": "inline"
        });

        // If already we have lookups, we remove them to avoid overwritting
        if($(selector).children()) {
            $(selector).children().remove();
        }

        // This if is for check if the select-property is for a wildcard input
        if(!arrayOptions) {
            datatype = 'default';
            arrayOptions = diagram.lookupsValuesType[datatype];
        }

        for (var i = 0; i < arrayOptions.length; i++) {
            var value = diagram.lookupsBackendValues[arrayOptions[i]];
            $(selector).attr("data-fieldid", fieldId);
            if(i == 0) {
                $(selector).append('<option class="lookup-option" value="' + value + '" disabled="disabled" selected="selected">' + arrayOptions[i] + '</option>');
            } else {
                $(selector).append('<option class="lookup-option" value="' + value + '">' + arrayOptions[i] + '</option>');
            }
        }

        // Here we ask if the datatype needs a special input
        var tagName = $this.next().next().prop("tagName");
        if(datatype == 'boolean') {
            // Boolean select
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<SELECT>");
            inputLookup.addClass("lookup-value");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "margin-top": "-4px",
                "padding": "0",
                "display": "none"
            });
            inputLookup.append('<option class="lookup-value" value="true">True</option>');
            inputLookup.append('<option class="lookup-value" value="false">False</option>');
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'choices') {
            // Choices select
            var choicesArray = choices.split(',');
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<SELECT>");
            inputLookup.addClass("lookup-value");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "margin-top": "-4px",
                "padding": "0",
                "display": "none"
            });
            inputLookup.append('<option class="lookup-value" value=""></option>');
            for(var j = 3; j < choicesArray.length; j = j + 2) {
                inputLookup.append('<option class="lookup-value" value="' + choicesArray[j] +'">' + choicesArray[j] + '</option>');
            }
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'auto_now') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            inputLookup.timepicker({
                timeOnly: true,
                showSecond: true,
            });
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'auto_now_add') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value time");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            inputLookup.timepicker({
                timeOnly: true,
                showSecond: true,
            });
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'date') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value time");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            var options = {
                appendText: "(yyyy-mm-dd)",
                gotoCurrent: true,
                dateFormat: 'yy-mm-dd',
                changeYear: true,
                yearRange: "-3000:3000"
            };
            inputLookup.datepicker(options);
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'time') {
            // Datepicker input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value time");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            inputLookup.timepicker({
                timeOnly: true,
                showSecond: true,
            });
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else if(datatype == 'auto_user') {
            // Users select
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                var tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value autocomplete");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        } else {
            // Initial input
            if(tagName == "INPUT" || tagName == "SELECT") {
                $this.next().next().remove();
                tagName = $this.next().next().prop("tagName");
                if(tagName == "INPUT") {
                    $this.next().next().remove();
                }
            }
            var inputLookup = $("<INPUT>");
            inputLookup.addClass("lookup-value");
            inputLookup.attr("type", "text");
            inputLookup.attr("title", gettext("Introduce a value"));
            inputLookup.css({
                "width": "60px",
                "margin-left": "8px",
                "padding": "2px 2px 1px 2px",
                "margin-top": "-4px",
                "display": "none"
            });
            $(inputLookup).insertAfter($('#' + idBox + ' #' + fieldId + ' .select-lookup'))
        }

        if(datatype == 'auto_user') {
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

        // We check if we have already the select field or the undo icon
        var selectClass = $this.next().next().next().attr('class');

        if(selectClass === "select-other-boxes-properties") {
            var selectBoxesProperties = $this.next().next().next();
        } else if(selectClass === "fa fa-undo") {
            $this.next().next().next().click();
            var selectBoxesProperties = $this.next().next().next();
        } else {
            // We create the select field to show after the input
            var selectBoxesProperties = $('<SELECT>');
            selectBoxesProperties.addClass('select-other-boxes-properties');
            selectBoxesProperties.attr("title", gettext("Select a property from another box"));
            selectBoxesProperties.css({
                "width": "20px",
                "display": "none",
                "margin-left": "8px",
                "height": "18px",
                "margin-top": "-4px"
            });
            selectBoxesProperties.attr("data-propselected", false);
            $(selectBoxesProperties).insertAfter($('#' + idBox + ' #' + fieldId + ' .lookup-value'));

            // We create the link to remove the input value again
            var removeLookupValue = $("<A>");
            removeLookupValue.addClass('link-other-boxes-properties');
            removeLookupValue.css({
                "display": "none"
            });
            var removeLookupValueIcon = $("<I>");
            removeLookupValueIcon.addClass("fa fa-undo");
            removeLookupValueIcon.css({
                "margin-left": "8px"
            });
            removeLookupValue.append(removeLookupValueIcon);
            $(removeLookupValue).insertAfter(selectBoxesProperties);

            // The default option for the selects
            var optionDefaultProperty = $("<OPTION>");
            optionDefaultProperty.addClass('option-other-boxes-properties');
            optionDefaultProperty.attr('value', gettext("choose one"));
            optionDefaultProperty.attr('selected', 'selected');
            optionDefaultProperty.prop('disabled', 'disabled');
            optionDefaultProperty.html(gettext("choose one"));

            // We append the default option
            $(selectBoxesProperties).prepend(optionDefaultProperty);
        }

        // We add the new property to the select options and we update
        // all the select that we already have
        var $titleElem = $('#' + idBox + ' .title');
        var showAlias = $titleElem.children().filter('input, select').val();
        var slugAlias = $titleElem.data('slug');
        var value = slugAlias + '.' + propertyId;
        var label = showAlias + '.' + propertyValue;

        var otherBoxesProperties = $('option:selected', '.select-property');
        
        // We define global variables to use them inside the each below
        window.slugValue = slugAlias;
        window.actualProperty = propertyValue;
        window.actualDatatype = datatype;
        window.slugPropValue = value;
        window.idBox = idBox;

        var allSelectsProperties = $('.select-property');
        var allOptionsBoxesProperties = $('option', '.select-other-boxes-properties');

        // If we have changed the property, we need to remove the options
        // of the select.
        $('option', selectBoxesProperties).filter(
            function(index, oldOption) {
                // First, we need to let the "choose one"
                if($(oldOption).val() !== gettext("choose one"))
                    if($(oldOption).data('datatype') !== actualDatatype)
                        $(oldOption).remove();
            }
        );

        // We add all the properties of the other selects
        $.each(allSelectsProperties, function(index, elem) {
            var containsElem = false;
            // We need to avoid to add the properties of the same box
            var idElemBox = $(elem).parent().parent().parent().parent().parent().attr('id');

            if(window.idBox !== idElemBox) {
                var selectOtherBoxesProperties = $(elem).next().next().next();
                // First, we check that the select it's not the new one.
                if(selectOtherBoxesProperties[0] !== selectBoxesProperties[0]) {
                    var datatype = $('option:selected', elem).data('datatype');
                    // Now, we check if the datatype is equal
                    if(datatype === actualDatatype) {
                        var boxAlias = $(elem).data('boxalias');
                        var propertyId = $('option:selected', elem).data('propertyid');    
                        var propertyValue = boxAlias + '.' + propertyId;
                        // Let's check if we have aggregate
                        var aggregate = $(elem).prev().val();
                        if(aggregate !== "") {
                            var distinctValue = "";
                            var distinctHTML = "";
                            var distinct = $('option:selected', $(elem).prev()).data('distinct');
                            if(distinct) {
                                distinctValue = "DISTINCT ";
                                distinctHTML = " Distinct";
                            }

                            propertyValue = aggregate + '(' + distinctValue + propertyValue + ')';
                        }
                        // And now, we check that the select does not contains
                        // the element
                        $('option', selectBoxesProperties).filter(
                            function(index, oldOption) {
                                if($(oldOption).val() === propertyValue)
                                    containsElem = true;
                            }
                        );

                        if(!containsElem) {
                            var idBox = $(elem).parent().parent().parent().parent().parent().attr('id');
                            var $titleElem = $('#' + idBox + ' .title');
                            var showAlias = $titleElem.children().filter('input, select').val();
                            var slugAlias = $titleElem.data('slug');
                            var propertyId = $('option:selected', elem).data('propertyid');
                            var propertyValue = $('option:selected', elem).val();
                            var fieldId = $(elem).data('fieldid');

                            var value = slugAlias + '.' + propertyId;
                            var label = showAlias + '.' + propertyValue;
                            var withValue = slugAlias + '.' + propertyValue;

                            // Let's check if we have aggregate
                            if(aggregate !== "") {
                                var distinctValue = "";
                                var distinctHTML = "";
                                var distinct = $('option:selected', $(elem).prev()).data('distinct');
                                if(distinct) {
                                    distinctValue = "DISTINCT ";
                                    distinctHTML = " Distinct";
                                }

                                value = aggregate + '(' + distinctValue + value + ')';
                                label = aggregate + distinctHTML + '(' + label + ')';
                                withValue = aggregate + '(' + distinctValue + withValue + ')';
                            }

                            // The new option for the selects
                            var optionBoxesProperty = $("<OPTION>");
                            optionBoxesProperty.addClass('option-other-boxes-properties');
                            optionBoxesProperty.attr('id', value);
                            // We add the slug value to manage the option using this field
                            optionBoxesProperty.attr('data-slugvalue', slugAlias);
                            optionBoxesProperty.attr('data-propname', propertyValue);
                            optionBoxesProperty.attr('data-withvalue', withValue);
                            optionBoxesProperty.attr('data-datatype', datatype);
                            optionBoxesProperty.attr('data-fieldid', fieldId);
                            optionBoxesProperty.attr('value', value);
                            optionBoxesProperty.html(label);

                            $(selectBoxesProperties).append(optionBoxesProperty);
                        }
                    }
                }
            }
        });

        // We get the array of properties selected in the actual box
        var boxProperties = $('#' + idBox + ' .select-property');

        // We update all the other selects except the new one
        $.each(allSelectsProperties, function(index, elem) {
            var containsElem = false;
            // We need to avoid to add the properties of the same box
            var idElemBox = $(elem).parent().parent().parent().parent().parent().attr('id');

            if(idBox !== idElemBox) {
                var selectOtherBoxesProperties = $(elem).next().next().next();
                // First, we check that the select it's not the new one.
                if(selectOtherBoxesProperties[0] !== selectBoxesProperties[0]) {
                    // We remove the options of the allSelectsProperties that
                    // belong to this box. This is done to avoid duplicates and
                    // datatypes conflicts.
                    $('option', selectOtherBoxesProperties).filter(
                        function(index, option) {
                            if($(option).data('slugvalue') === slugValue)
                                $(option).remove();
                        }
                    );
                    // We need to iterate over all the properties, because
                    // we need to take into account repeated properties, etc.
                    // Now, we check if the datatypes are equals
                    var propDatatype = $('option:selected', elem).data('datatype');
                    $.each(boxProperties, function(index, propSelected) {
                        var datatype = $('option:selected', propSelected).data('datatype');
                        if(propDatatype === datatype) {
                            var propertyValue = slugPropValue;
                            // Let's check if we have aggregate
                            var aggregate = $(elem).prev().val();
                            if(aggregate !== "") {
                                var distinctValue = "";
                                var distinctHTML = "";
                                var distinct = $('option:selected', $(elem).prev()).data('distinct');
                                if(distinct) {
                                    distinctValue = "DISTINCT ";
                                    distinctHTML = " Distinct";
                                }

                                propertyValue = aggregate + '(' + distinctValue + propertyValue + ')';
                            }
                            // And now, we check that the select does not
                            // contains the element
                            $('option', selectOtherBoxesProperties).filter(
                                function(index, oldOption) {
                                    if($(oldOption).val() === propertyValue)
                                        containsElem = true;
                                }
                            );

                            if(!containsElem) {
                                var idBox = $(propSelected).parent().parent().parent().parent().parent().attr('id');
                                var $titleElem = $('#' + idBox + ' .title');
                                var showAlias = $titleElem.children().filter('input, select').val();
                                var slugAlias = $titleElem.data('slug');
                                var propertyId = $('option:selected', propSelected).data('propertyid');
                                var propertyValue = $('option:selected', propSelected).val();
                                var fieldId = $(propSelected).data('fieldid');

                                var value = slugAlias + '.' + propertyId;
                                var label = showAlias + '.' + propertyValue;
                                var withValue = slugAlias + '.' + propertyValue;

                                // Let's check if we have aggregate
                                var aggregate = $(propSelected).prev().val();
                                if(aggregate !== "") {
                                    var distinctValue = "";
                                    var distinctHTML = "";
                                    var distinct = $('option:selected', $(propSelected).prev()).data('distinct');
                                    if(distinct) {
                                        distinctValue = "DISTINCT ";
                                        distinctHTML = " Distinct";
                                    }

                                    value = aggregate + '(' + distinctValue + value + ')';
                                    label = aggregate + distinctHTML + '(' + label + ')';
                                    withValue = aggregate + '(' + distinctValue + withValue + ')';
                                }

                                // The new option for the selects
                                var optionBoxesProperty = $("<OPTION>");
                                optionBoxesProperty.addClass('option-other-boxes-properties');
                                optionBoxesProperty.attr('id', value);
                                // We add the slug value to manage the option using this field
                                optionBoxesProperty.attr('data-slugvalue', slugAlias);
                                optionBoxesProperty.attr('data-propname', propertyValue);
                                optionBoxesProperty.attr('data-withvalue', withValue);
                                optionBoxesProperty.attr('data-datatype', datatype);
                                optionBoxesProperty.attr('data-fieldid', fieldId);
                                optionBoxesProperty.attr('value', value);
                                optionBoxesProperty.html(label);

                                $(selectOtherBoxesProperties).append(optionBoxesProperty.clone(true));
                            }
                        }
                        
                    });
                }
            }
        });
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

        // We show the input for the lookup value
        $('#' + fieldId + " .lookup-value").css({
            "display": "inline"
        });

        // If the select is hidden, we show the select for the other boxes 
        // properties
        var selectIsShowed = $('#' + fieldId + " .select-other-boxes-properties").css('display');
        var iconIsShowed = $('#' + fieldId + " .link-other-boxes-properties").css('display');
        if(selectIsShowed === 'none' && iconIsShowed === 'none') {
            $('#' + fieldId + " .select-other-boxes-properties").css({
                "display": "inline"
            });
        } else if(selectIsShowed === 'none' && iconIsShowed !== 'none') {
            // We remove the lookup input value
            $this.next().val("");
            $('#' + fieldId + " .link-other-boxes-properties").css({
                "display": "none"
            });
            $('#' + fieldId + " .select-other-boxes-properties").css({
                "display": "inline"
            });
        }

        var datatype = $('#' + fieldId + ' .select-property option:selected').data("datatype");
        var condition = datatype != 'date'
                        && datatype != 'time'
                        && datatype != 'boolean'
                        && datatype != 'choices'
                        && datatype != 'auto_now'
                        && datatype != 'auto_now_add'
                        && datatype != 'auto_user';
        if(condition) {
            if(value == "between") {
                // two inputs - we check if we have introduced an input field
                var inputValueFirst = $this.next().val();
                var inputValueSecond = $this.next().next().val();
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    tagName = $this.next().prop("tagName");
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input class='lookup-value' type='text' style=\"width: 25px; margin-left: 2%; padding: 2px 2px 1px 2px; margin-top: -4px; display: inline;\" />");
                $this.after("<input class='lookup-value' type='text' style=\"width: 25px; margin-left: 2%; padding: 2px 2px 1px 2px; margin-top: -4px; display: inline;\" />");
                // We keep the value of the inputs
                if(inputValueFirst) {
                    $this.next().val(inputValueFirst);
                } else if(inputValueSecond) {
                    $this.next().next().val(inputValueSecond);
                }
            } else if((value == "isnotnull") || (value == "isnull")) {
                // no inputs
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    tagName = $this.next().prop("tagName");
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
            } else {
                // one input - we check if we have introduced an input field
                var inputValue = $this.next().val();
                if(tagName == "INPUT" || tagName == "SELECT") {
                    $this.next().remove();
                    tagName = $this.next().prop("tagName");
                    if(tagName == "INPUT") {
                        $this.next().remove();
                    }
                }
                $this.after("<input class='lookup-value' type='text' style='width: 60px; margin-left: 8px; padding: 2px 2px 1px 2px; margin-top: -4px; display: inline;' />");
                // We keep the value of the input
                if(inputValue) {
                    $this.next().val(inputValue);
                }
            }
        } else {
            // In this branch, the type would be boolean, choices, date or user
        }
    });

    $("#diagramContainer").on('click', '.link-other-boxes-properties', function() {
        var $this = $(this);
        var $selectField = $this.prev();
        // We are going to set the value for the lookup input
        var $lookupInput = $selectField.prev();
        
        // We hide the link
        $this.css('display', 'none');
        // And we show the select
        $selectField.css('display', 'inline');
        // We restore the select field for a correct behaviour with the change 
        // event
        $selectField.val("");

        // We restore the lookup input
        $lookupInput.removeAttr('data-boxproperty');
        $lookupInput.removeAttr('data-withvalue');
        $lookupInput.val("");
        $lookupInput.prop('disabled', '');
    });

    /**
     * We change the value of the lookup input after select a property
     * of another box
     */
    $("#diagramContainer").on('change', '.select-other-boxes-properties', function() {
        var $this = $(this);
        var $selectLink = $this.next();
        // We are going to set the value for the lookup input
        var $lookupInput = $this.prev();
        var propSelected = $('option:selected', this);
        var propValue = $(propSelected).val();
        var propHtml = $(propSelected).html();
        var propWithValue = $(propSelected).data('withvalue');
    
        // We hide the select
        $this.css('display', 'none');
        // And we show the link
        $selectLink.css('display', 'inline');
        // We set all the neccesary in the lookup input
        $lookupInput.attr('data-boxproperty', propValue);
        $lookupInput.attr('data-withvalue', propWithValue);
        $lookupInput.val(propHtml);
        $lookupInput.prop('disabled', 'disabled');
    });

    /**
     * Add the handler to remove the wire
     */
    $("#diagramContainer").on('click', '.remove-relation', function() {
        var $this = $(this);
        var sourceId = $this.data("idbox");
        var name = $this.data("name");
        var patternId = sourceId + "-" + name;
        // We check if the type is wildcard
        if(name == "WildcardRel")
               name = "wildcard";
        // We remove the relation row in the source box
        var idDivRelSourceBox = "#div-" + sourceId + "-" + name;
        $(idDivRelSourceBox).remove();
        // We still have the endpoints to create connections.
        // We need to remove the source endpoint of the relationship.
        var oldEndpointRelIndex = jsPlumb.getEndpoint(patternId + '-source').relIndex;
        var endpointUuid = sourceId + '-' + name + '-source';
        jsPlumb.deleteEndpoint(endpointUuid);
        // We decrement the value of the relationship index to calculate
        // the anchor for the source endpoints
        diagram.relindex[sourceId]--;
        // We will repaint everything and recalculate anchors
        var sourceIdSplitted = sourceId.split('-');
        var indexAndName = sourceIdSplitted[1] + '-' + sourceIdSplitted[2];
        var idAllRels = 'diagramAllRel-' + indexAndName;

        // Recalculate anchor if we have source endpoints already
        if(jsPlumb.getEndpoints(sourceId).length > 1) {
            // We start at index 1 because the index 0 si the target
            var endpointsLength = jsPlumb.getEndpoints(sourceId).length;
            for(var i = 1; i < endpointsLength; i++) {
                var endpoint = jsPlumb.getEndpoints(sourceId)[i];
                var anchor = 0;
                // This is for the case that we have removed some
                // element and need to update the rel index.
                // The substract operation is because we have an endpoint
                // extra: The target endpoint
                if(endpoint.relIndex > oldEndpointRelIndex) {
                    var newRelIndex = endpoint.relIndex - 1;
                    anchor = diagram.calculateAnchor(sourceId, idAllRels, newRelIndex);
                    endpoint.relIndex = newRelIndex;

                } else {
                    anchor = diagram.calculateAnchor(sourceId, idAllRels, endpoint.relIndex);
                }
                endpoint.anchor.y = anchor;
            }
        }

        jsPlumb.repaintEverything();
    });

    /**
     * Add the handler to remove the wire
     */
    $("#diagramContainer").on('change', '.edit-alias', function() {
        // We get all the alias for the type to change if the alias is in another box
        var newAlias = $(this).val();
        var modelId = $(this).data("modelid");
        var idBox = $(this).data("idbox");
        var oldAlias = $(this).data("oldvalue");
        var typeName = $(this).data("typename");
        var dataType = $(this).data("datatype");
        // We save the new entry in the dictionary
        // We are going to have the newAlias like key and the oldAlias like
        // value
        diagram.boxesValues[newAlias] = oldAlias;
        // We get the select for the type and the input
        var selectorInput = $('#' + idBox + ' .edit-alias');
        savedSelect = $(diagram.boxesSelects[idBox]).clone();
        selectorSelect = savedSelect[0]
        // We update the select field
        $(selectorInput).replaceWith(selectorSelect);
        var optionsSelect = $(selectorSelect).children();
        $.each(optionsSelect, function(index, option) {
            if($(option).val() == oldAlias) {
                $newOption = $(this);
                $newOption.attr('value', newAlias);
                $newOption.html(newAlias);
            }
        });
        if(dataType == "node") {
            // We select the new option in the select
            $('#' + idBox + '.select-nodetype-' + typeName).val(newAlias);
            diagram.propagateValue(newAlias, oldAlias, typeName, true);
        } else {
            // We select the new option in the select
            $('#' + idBox + '.select-reltype-' + typeName).val(newAlias);
            diagram.propagateValue(newAlias, oldAlias, typeName, false);
        }
        // We are going to change the icon to edit the alias
        var iconEditSelect = $('#' + idBox + ' #inlineEditSelect_' + typeName + ' i');
        iconEditSelect.removeClass('fa fa-undo icon-style');
        iconEditSelect.addClass('fa fa-pencil icon-style');

        // We check if we need to change the alias in the order by select
        var orderByOptions = $('#id_select_order_by option');
        $.each(orderByOptions, function(index, elem) {
            var orderByAlias = $(elem).html();
            // We check if we have an aggregate selected
            // If the length is bigger than 1
            var isThereAgg = orderByAlias.split("(").length > 1;
            if(isThereAgg) {
                var orderByAliasSplitted = orderByAlias.split(/["(",")"]+/);
                var aggregateValue = orderByAliasSplitted[0];
                var oldOptionVal = orderByAliasSplitted[1];
                var oldOptionValWithoutAgg = oldOptionVal.split(".");
                var oldOptionAlias = oldOptionValWithoutAgg[0];
                if(oldOptionAlias == oldAlias) {
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldOptionValWithoutAgg[1];
                    var newOptionAggregate = aggregateValue + "(" + newOptionVal + ")";
                    $(elem).html(newOptionAggregate);
                }
            } else {
                var oldOptionVal = orderByAlias.split(".");
                var oldOptionAlias = oldOptionVal[0];
                if(oldOptionAlias == oldAlias) {
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldOptionVal[1];
                    $(elem).attr("value", newOptionVal);
                    $(elem).html(newOptionVal);
                }
            }
        });

        // We check if we need to change the alias of the select of other
        // properties boxes
        var optionsOtherBoxesProps = $('option', '.select-other-boxes-properties');
        //var boxSlug = $('#' + idBox + '-title').data('slug');
        $.each(optionsOtherBoxesProps, function(index, elem) {
            // We check if we have an aggregate selected
            // If the length is bigger than 1
            var oldOptionVal = $(elem).html();
            var isThereAgg = oldOptionVal.split("(").length > 1;
            if(isThereAgg) {
                var oldOptionValSplitted = oldOptionVal.split(/["(",")"]+/);
                var aggregateValue = oldOptionValSplitted[0];
                var oldValue = oldOptionValSplitted[1];
                var oldValueWithoutAgg = oldValue.split(".");
                var oldOptionAlias = oldValueWithoutAgg[0];
                if(oldOptionAlias === oldAlias) {
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldValueWithoutAgg[1];
                    var newOptionVal = aggregateValue + "(" + newOptionVal + ")";
                    $(elem).html(newOptionVal);
                }
            } else {
                var oldOptionValSplitted = oldOptionVal.split(".");
                var oldOptionAlias = oldOptionValSplitted[0];
                if(oldOptionAlias === oldAlias) {    
                    // We change the value of the option
                    var newOptionVal = newAlias + "." + oldOptionValSplitted[1];
                    $(elem).html(newOptionVal);
                }
            }
            // We need to check if the option is selected to change the
            // actual value of the lookup input
            var $lookupInput = $(elem).parent().prev();
            var lookupValue = $lookupInput.val();
            //var isSelected = $(elem).prop('selected');
            var isSelected = lookupValue === oldOptionVal;
            if(isSelected) {
                // We get the lookup
                var $lookupInput = $(elem).parent().prev();
                // We change the lookup input
                $lookupInput.val(newOptionVal);
            }
        });
    });

    /**
     * Bind methods for control jsPlumb events
     * These methods allow us to control some JSPlumb events.
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
            // We store the name in the label variable
            var nameRel = info.connection.getOverlays()[1].label;
            // We store the label in the label id
            var labelRel = info.connection.getOverlays()[1].id;
            info.connection.idrel = idBoxRel;
            // We hide the label overlay
            //info.connection.getOverlays()[1].setVisible(false);

            // We select the index of the element for select it for the alias
            var elem = $('.select-reltype-' + nameRel + ' #' + nameRel + (diagram.reltypesCounter[nameRel])).length - 1;
            $($('.select-reltype-' + nameRel + ' #' + nameRel + (diagram.reltypesCounter[nameRel]))[elem]).attr('selected', 'selected');

            $('.endpoint-image').css('visibility', 'visible');
            info.targetEndpoint.removeClass("dragActive");
            info.targetEndpoint.removeClass("dropHover");

            // We check if we have more than one box to show the selects for the alias
            diagram.showSelects(nameRel, "relationship");
        } else {
            // Here we need to reestablish the normal behaviour of the boxes
            jsPlumb.selectEndpoints().each(function(endpoint) {
                $(".dragActive").css({
                    'margin-left': '0px'
                });
                endpoint.removeClass("dragActive");
                endpoint.removeClass("dropHover");
                var selector = '#' + endpoint.elementId + ' .title';
                $(selector).on('mouseover', function() {
                    $(selector).css({
                        "box-shadow": ""
                    });
                });
            });
            $('.endpoint-image').css('visibility', 'visible');
            // We need to remove the another enpoint that appears
            endpointToDelete = $('img').not('.endpointDrag');
            endpointToDelete.remove();

            jsPlumb.detach(info.connection);
        }

        var selector = '#' + info.targetEndpoint.elementId + ' .title';
        $(selector).on('mouseover', function() {
            $(selector).css({
                "box-shadow": ""
            });
        });
    });

    jsPlumb.bind("connectionDrag", function(connection) {
        // We make the endpoint invisible
        $('.endpoint-image').css('visibility', 'hidden');

        // We make the drag css style for nodes with the correct target
        var scopeSource = connection.endpoints[0].scopeSource;

        // We check if the id for the relationship is correct
        var idBoxRel = connection.getOverlays()[2].id;
        // We get the number of idBoxRel
        var idBoxRelParts = idBoxRel.split('-');
        var idNumber = idBoxRelParts[1];
        if(idNumber != diagram.CounterRels) {
            idBoxRel = idBoxRelParts[0] + "-" + diagram.CounterRels + "-" + idBoxRelParts[2];
            connection.getOverlays()[2].id = idBoxRel;
        }

        jsPlumb.selectEndpoints().each(function(endpoint) {
            var scopeTarget = endpoint.scopeTarget;
            if(scopeTarget) {
                var compare = scopeSource == scopeTarget;
                var compareWildcard = (scopeSource == "wildcard") ||
                                        (scopeTarget == "wildcard");
                if(compare || compareWildcard) {
                    // We need to check here if the target box has
                    // the advanced mode activate. So, we assign the
                    // width of the box to the endpoint width
                    var boxWidth = $('#' + endpoint.elementId).css('width');
                    endpoint.addClass("dragActive");
                    if(boxWidth == "440px") {
                        // We select the endpoint to change the width and
                        // position it correctly
                        $(".dragActive").css({
                            'width': '440px',
                            'margin-left': '-40px'
                        });
                    }
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
        $('.endpoint-image').css('visibility', 'visible');
        jsPlumb.selectEndpoints().each(function(endpoint) {
            $(".dragActive").css({
                'margin-left': '0px'
            });
            endpoint.removeClass("dragActive");
            var selector = '#' + endpoint.elementId + ' .title';
            $(selector).on('mouseover', function() {
                $(selector).css({
                    "box-shadow": ""
                });
            });
        });

        // We need to control if we have dragged to another box or not
        if(connection.getConnector()) {
            var sourceIdValue = connection.sourceId;
            var targetIdValue = connection.targetId;

            var idBoxRel = connection.getOverlays()[2].id;
            // We store the name in the label variable
            var nameRel = connection.getOverlays()[1].label;
            // We store the label in the label id
            var labelRel = connection.getOverlays()[1].id;
            connection.idrel = idBoxRel;
            // We get the modelid of the box before detach the connection
            var relModelId = $('#' + idBoxRel + ' .title').data('modelid');
            // We remove the connection that we dragged
            jsPlumb.detach(connection);
            // We substract 1 to the counter of the relationship
            diagram.reltypesCounter[nameRel]--;

            // We need to control the reflexive relations
            if(sourceIdValue == targetIdValue) {
                targetIdValue = sourceIdValue + '-title';
            }

            // And we add the new connection with "Continuous" anchors
            diagram.addRelation(sourceIdValue, targetIdValue, labelRel, nameRel, relModelId);
        }
    });

    /**
     * Handler for create the JSON file
     */
    $(document).on('click', '#form-run-query', function(event) {
        var queryElements = diagram.saveQuery();
        var query = queryElements['query'];
        var query_aliases = queryElements['aliases'];
        var query_fields = queryElements['fields'];

        var queryJson = JSON.stringify(query);
        var queryAliases = JSON.stringify(query_aliases);
        var queryFields = JSON.stringify(query_fields);

        $('input[id=query]').val(queryJson);
        $('input[id=query_aliases]').val(queryAliases);
        $('input[id=query_fields]').val(queryFields);

        return true;
    });

    /**
     * Handler to get the information to save the query
     */
    $(document).on('click', '#save-query', function(event) {
        var queryElements = diagram.saveQuery();
        // We are going to assign the values for the elements of the form
        var numberOfResults = $('.content-table tr').length;
        $('#id_results_count').val(numberOfResults);
        $('#id_last_run').val('1918-12-01');
        $('#id_query_dict').val(JSON.stringify(queryElements['query']));
        $('#id_query_aliases').val(JSON.stringify(queryElements['aliases']));
        $('#id_query_fields').val(JSON.stringify(queryElements['fields']));

        return true;
    });

    $(document).ready(init);

})(jQuery);
