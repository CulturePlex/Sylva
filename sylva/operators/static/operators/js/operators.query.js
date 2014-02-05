/* Adapted from https://github.com/versae/qbe */
if (!diagram) {
    var diagram = {};
}
diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.CurrentRelations = {};
diagram.Counter = 0;
diagram.lookupCounter = [];

diagram.lookupsValues = ["equals",
                        "is less than or equal to",
                        "is less than",
                        "is greater than",
                        "is greater than or equal to",
                        "is between",
                        "does not equal",
                        "has some value",
                        "has no value"];

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
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px"
            });
            /* Not needed anymore scrollTo
            divBox.on("mouseenter", function() {
                $(".content2-first").scrollTo("#model_"+ modelName, {
                    "duration": 500,
                    "queue": false
                });
            });ç
            */
            divBox.addClass("body");
            divTitle = $("<DIV>");
            divTitle.addClass("title");
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
            divFields = $("<DIV>");
            divFields.attr("id", "diagramFields_"+ modelName);
            countFields = 0;
            lengthFields = model.fields.length;
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = model.fields[fieldIndex];
                var id = "diagramBoxField_"+ diagram.Counter +"_"+ graphName +"_"+ modelName +"_"+ field.name;
                // Initialize the lookups counter for the field
                diagram.lookupCounter[field.name] = 0;
                divField = $("<DIV>");
                divField.addClass("field");
                divField.css('display', 'block');
                diagram.setLabel(divField, field.label, field.primary);
                divField.attr("id", id);
                // link to add new lookups
                addLookup = $("<A>");
                addLookup.addClass("add-lookup");
                addLookup.attr("id", "lookup-" + field.name);
                addLookup.attr("href", "javascript:void(0);");
                addLookup.css("float", "right");
                addLookup.css("margin-right", "5%");
                // Icon
                addLookupIcon = $("<I>");
                addLookupIcon.addClass("icon-plus-sign");
                // Div to draw the lookups
                divLookup = $("<DIV>");
                divLookup.addClass("div-" + field.name);
                addLookup.attr("data-name", "div-" + field.name);
                addLookup.attr("data-id", id);
                addLookup.attr("data-field", field.name);
                addLookup.attr("data-type", field.type);
                addLookup.append(addLookupIcon);
                divField.append(addLookup);
                divField.append(divLookup);
                // TODO
                if (field.type == "ForeignKey") {
                    divField.addClass("single");
                    divField.click(diagram.addRelated);
                    divBox.prepend(divField);
                } else if (field.type == "ManyToManyField") {
                    divField.addClass("double");
                    divField.click(diagram.addRelated);
                    if (!divManies) {
                        divManies = $("<DIV>");
                    }
                    divManies.append(divField);
                } else if (field.primary) {
                    divField.addClass("primary");
                    primaries.push(divField);
                } else {
                    divFields.append(divField);
                    countFields++;
                }
            }
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
            /* TODO: Not send positions until the query is not saved
            $.ajax({
                url: $("#id_diagram_positions_url").val(),
                dataType: 'json',
                data: {diagram_positions: positionsString},
                type: 'post',
                success: function() {
                    // $("#id_diagram_positions").val(positionsString);
                }
            });
            */
        };

        /**
         * Load the models from the schema
         */
        diagram.loadModels = function() {
            var graph, models, modelName, position, positionºs, titleAnchor;
            if (diagram.Models) {
                for(graph in diagram.Models) {
                    models = diagram.Models[graph];
                    for(modelName in models) {
                        diagram.addModel(graph, modelName);
                    }
                }
            }
            positions = JSON.parse($("#id_diagram_positions").val());
            for(var i=0; i<positions.length; i++) {
                position = positions[i]
                // Show just selected models
                // if (!(appModel in diagram.CurrentModels)) {
                //     $("#diagramModelItem_"+ modelName).toggleClass("selected");
                //     diagram.addModule(graphName, modelName);
                // }
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
         * Load the models from the schema
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
        * Create a contextual menu with the lookups
        * - parentId
        * - className
        * - datatype
        * - fieldName
        */
        diagram.lookups = function(parentId, className, datatype, fieldName) {
            divSelectLookup = $("<DIV>");
            divSelectLookup.addClass(className + "-lookup-" + diagram.lookupCounter[fieldName]);
            // Select field with the lookups options
            selectLookup = $("<SELECT>");
            selectLookup.addClass("select-lookup");
            selectLookup.attr("style", "width: 35%; display: inline; margin-left: 3%;");
            for (var i = 0; i<diagram.lookupsValues.length; i++) {
                selectLookup.append('<option value="' + diagram.lookupsValues[i] + '">' + diagram.lookupsValues[i] + '</option>');
            }
            // Initial input
            inputLookup = $("<INPUT>");
            inputLookup.attr("style", "width: 35%; margin-left: 5%;");
            // Link to remove the lookup
            removeLookup = $("<A>");
            removeLookup.addClass("remove-lookup");
            removeLookup.attr("id", className + "-lookup-" + diagram.lookupCounter[fieldName]);
            removeLookup.attr("data-field", fieldName);
            removeLookup.attr("data-parentid", parentId);
            removeLookup.attr("href", "javascript:void(0);");
            removeLookup.css("margin-left", "2%");
            // Icon
            removeLookupIcon = $("<I>");
            removeLookupIcon.addClass("icon-minus-sign");
            // We append the elements
            removeLookup.append(removeLookupIcon);
            divSelectLookup.append(selectLookup);
            divSelectLookup.append(inputLookup);
            divSelectLookup.append(removeLookup);
            $("." + className).append(divSelectLookup);
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

    $("#diagramContainer").on('click', '.add-lookup', function() {
        var $this = $(this);
        var id = $this.data("id");
        var className = $this.data("name");
        var datatype = $this.data("type");
        var fieldName = $this.data("field");
        $('#' + id).css('display', 'inline-table');
        diagram.lookups(id, className, datatype, fieldName);
        var newValue = diagram.lookupCounter[fieldName];
        diagram.lookupCounter[fieldName] = newValue + 1;
    });

    /**
      * Remove lookup inside a box type
      */

    $("#diagramContainer").on('click', '.remove-lookup', function() {
        var $this = $(this);
        var id = "." + this.id;
        var fieldName = $this.data("field");
        var parentId = $this.data("parentid");
        $(id).remove();
        var newValue = diagram.lookupCounter[fieldName];
        diagram.lookupCounter[fieldName] = newValue - 1;
        if(diagram.lookupCounter[fieldName] == 0)
            $('#' + parentId).css('display', 'block');
    });

    /**
      * Add a special input related to the lookup selected
      */

    $("#diagramContainer").on('change', '.select-lookup', function() {
        var $this = $(this);
        var value = $this.val();
        if(value == "is between") {
            // two inputs - we check if we have introduced an input field
            if(this.nextElementSibling.tagName == "INPUT") {
                $(this.nextElementSibling).remove();
                if(this.nextElementSibling.tagName == "INPUT") {
                    $(this.nextElementSibling).remove();
                }
            }
            $(this).after("<input style=\"width: 10%; margin-left: 5%;\" />");
            $(this).after("<input style=\"width: 10%; margin-left: 5%;\" />");
        } else if((value == "has some value") || (value == "has no value")) {
            // no inputs
            if(this.nextElementSibling.tagName == "INPUT") {
                $(this.nextElementSibling).remove();
                if(this.nextElementSibling.tagName == "INPUT") {
                    $(this.nextElementSibling).remove();
                }
            }
        } else {
            // one input - we check if we have introduced an input field
            if(this.nextElementSibling.tagName == "INPUT") {
                $(this.nextElementSibling).remove();
                if(this.nextElementSibling.tagName == "INPUT") {
                    $(this.nextElementSibling).remove();
                }
            }
            $(this).after("<input style=\"width: 35%; margin-left: 5%;\" />");
        }
    });

    $(document).ready(init);
})(jQuery);
