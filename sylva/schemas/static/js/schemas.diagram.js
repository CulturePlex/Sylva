/*jshint scripturl:true*/

/* Adapted from https://github.com/versae/qbe */
if (!diagram) {
    var diagram = {};
}
diagram.Container = "diagram";
diagram.CurrentModels = [];
diagram.CurrentRelations = {};

(function($) {
    /**
      * AJAX Setup for CSRF Django token
      */
    $.ajaxSetup({
         beforeSend: function(xhr, settings) {
             function getCookie(name) {
                 var cookieValue = null;
                 if (document.cookie && document.cookie !== '') {
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
        diagram.Defaults.single = {
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
        diagram.Defaults.double = {
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
        };

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
            divBox = $("<DIV>");
            divBox.attr("id", "diagramBox_"+ modelName);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1, 10) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1, 10) * 10) + "px"
            });
            divBox.on("mouseenter", function() {
                $(".content2-first").scrollTo("#model_"+ modelName, {
                    "duration": 500,
                    "queue": false
                });
            });
            divBox.addClass("body");
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            diagram.setLabel(divTitle, model.name, false);

            // Show/hide button in the corner of the box and its associated event
            var anchorShowHide = $("<A>");
            anchorShowHide.attr("href", "javascript:void(0);");
            anchorShowHide.attr("id", "inlineShowHideLink_"+ modelName);
            anchorShowHide.addClass("inline-showHidelink");

            var iconShowHide = $("<I>");
            iconShowHide.addClass("fa fa-minus-circle");
            iconShowHide.css({
                "color": "white",
                "float": "right",
                "margin-right": "8px",
                "margin-top": "3px"
            });

            anchorShowHide.append(iconShowHide);
            anchorShowHide.click(function () {
                $("#diagramModelAnchor_"+ graphName +"\\."+ modelName).click();
                divFields.toggleClass("hidden");

                if (iconShowHide.attr('class') == 'fa fa-plus-circle') {
                    iconShowHide.removeClass('fa fa-plus-circle');
                    iconShowHide.addClass('fa fa-minus-circle');
                } else {
                    iconShowHide.removeClass('fa fa-minus-circle');
                    iconShowHide.addClass('fa fa-plus-circle');
                }

                diagram.saveBoxPositions();
                jsPlumb.repaintEverything();
            });

            // Link to delete type
            var anchorDelete = $("<A>");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.attr("id", "inlineDeleteLink_"+ modelName);
            anchorDelete.addClass("inlineDelete");
            var deleteUrl = "/schemas/" +
                            graphName +
                            "/types/" +
                            model.id +
                            "/delete/";
            anchorDelete.attr('data-deleteurl', deleteUrl);

            var iconDelete = $("<I>");
            iconDelete.addClass("fa fa-times-circle icon-style icon-delete");
            iconDelete.css({
                "color": "white",
                "float": "right",
                "margin-right": "8px",
                "margin-top": "3px"
            });

            anchorDelete.append(iconDelete);

            divTitle.append(anchorDelete);
            lengthFields = model.fields.length;
            // We check if we have fields to show the show-hide icon
            if(lengthFields > 0) {
                divTitle.append(anchorShowHide);
            }
            divFields = $("<DIV>");
            divFields.attr("id", "diagramFields_"+ modelName);
            countFields = 0;
//            for(fieldName in model.fields) {
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = model.fields[fieldIndex];
                divField = $("<DIV>");
                divField.addClass("field");
                diagram.setLabel(divField, field.label, field.primary);
                divField.attr("id", "diagramBoxField_"+ graphName +"."+ modelName +"."+ fieldName);
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
            jsPlumb.draggable("diagramBox_"+ modelName, {
                handle: ".title",
                grid: [10, 10],
                stop: function (event, ui) {
                    var $this, position, left, top;
                    $this = $(this);
                    position = $this.position();
                    left = position.left;
                    if (position.left < 0) {
                        left = "0px";
                    }
                    if (position.top < 0) {
                        top = "0px";
                    }
                    $this.animate({left: left, top: top}, "fast", function() {
                        jsPlumb.repaint(["diagramBox_"+ modelName]);
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
                diagram.removeBox(graphName, modelName);
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
            for(relationIndex = 0; relationIndex < lengthRelations; relationIndex++) {
                relation = model.relations[relationIndex];
                if ((diagram.CurrentModels.indexOf(graphName +"."+ relation.source) >= 0) &&
                    (diagram.CurrentModels.indexOf(graphName +"."+ relation.target) >= 0)) {
                    sourceId = "diagramBox_"+ relation.source;
                    if (relation.source === relation.target) {
                        // Reflexive relationships
                        targetId = "inlineShowHideLink_"+ relation.target;
                    } else {
                        targetId = "diagramBox_"+ relation.target;
                    }
                    diagram.addRelation(sourceId, targetId, relation.label);
                }
            }
        };

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
                    relStyle = "single";
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

            jsPlumb.repaintEverything();
        };

       /**
         * Save the positions of the all the boxes in a serialized way into a
         * input type hidden
         */
        diagram.saveBoxPositions = function () {
            var positions = [],
                positionsString,
                left,
                top,
                splits,
                appModel,
                modelName,
                status;
            for(var i=0; i<diagram.CurrentModels.length; i++) {
                appModel = diagram.CurrentModels[i];
                splits = appModel.split(".");
                modelName = splits[1];
                left = $("#diagramBox_"+ modelName).css("left");
                top = $("#diagramBox_"+ modelName).css("top");
                status = $("#diagramBox_"+ modelName +" > div > a").hasClass("inline-deleteLink");
                positions.push({
                    modelName: modelName,
                    left: left,
                    top: top,
                    status: status
                });
            }
            positionsString = JSON.stringify(positions);
            $.ajax({
                url: $("#id_diagram_positions_url").val(),
                dataType: 'json',
                data: {diagram_positions: positionsString},
                type: 'post',
                success: function() {
                    // $("#id_diagram_positions").val(positionsString);
                }
            });
        };

        /**
         * Load the models from the schema
         */
        diagram.loadModels = function() {
            var graph, models, modelName, position, positions, titleAnchor;
            if (diagram.Models) {
                for(graph in diagram.Models) {
                    models = diagram.Models[graph];
                    for(modelName in models) {
                        diagram.addModel(graph, modelName);
                    }
                }
            }
            var positions_val = $("#id_diagram_positions").val();
            positions = positions_val ? JSON.parse(positions_val) : [];
            for(var i=0; i<positions.length; i++) {
                position = positions[i];
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
                    $('#iconToggle', titleAnchor).addClass('fa fa-plus-circle');
                    //$("#diagramFields_"+ position.modelName).toggleClass("hidden");
                }
            }
            jsPlumb.repaintEverything();
            // We need to invoke this method again, because when we set the
            // positions of the boxes, sometimes the relationships are not
            // positioned fine.
            jsPlumb.repaintEverything();
        };

        if(!asModal) {
            diagram.loadModels();

            $('.inlineDelete').on('click', function () {
                // Navigate to the delete view
                url = $(this).data('deleteurl');

                window.location.href = url;
            });
        }
    };

    $(document).ready(init);
})(jQuery);
