/* Adapted from https://github.com/versae/qbe */
if (!diagram) {
    var diagram = {};
}
diagram.Container = "diagram";


(function($) {
    init = function() {
        diagram.Defaults = {};
        diagram.Defaults["foreign"] = {
            label: null,
            labelStyle: null,
            paintStyle: {
                strokeStyle: '#96D25C',
                lineWidth: 2
            },
            backgroundPaintStyle: {
                lineWidth: 4,
                strokeStyle: '#70A249'
            },
            makeOverlays: function() {
                return [
                    new jsPlumb.Overlays.PlainArrow({
                        foldback: 0,
                        fillStyle: '#96D25C',
                        strokeStyle: '#70A249',
                        location: 0.99,
                        width: 10,
                        length: 10})
                ];
            }
        };
        diagram.Defaults["many"] = {
            label: null,
            labelStyle: {
                fillStyle: "white",
                padding: 0.25,
                font: "12px sans-serif", 
                color: "#C55454",
                borderStyle: "#C55454", 
                borderWidth: 3
            },
            paintStyle: {
                strokeStyle: '#DB9292',
                lineWidth: 2
            },
            backgroundPaintStyle: {
                lineWidth: 4,
                strokeStyle: '#C55454'
            },
            makeOverlays: function() {
                return [
                    new jsPlumb.Overlays.PlainArrow({
                        foldback: 0,
                        fillStyle: '#DB9292',
                        strokeStyle: '#C55454',
                        location: 0.75,
                        width: 10,
                        length: 10}),
                    new jsPlumb.Overlays.PlainArrow({
                        foldback: 0,
                        fillStyle: '#DB9292',
                        strokeStyle: '#C55454',
                        location: 0.25,
                        width: 10,
                        length: 10})
                ];
            }
        }

        jsPlumb.Defaults.DragOptions = {cursor: 'pointer', zIndex: 2000};
        jsPlumb.Defaults.Container = diagram.Container;

        /**
         * Adds a new model box with its fields
         */
        diagram.addBox = function (appName, modelName) {
            var model, root, divBox, divTitle, fieldName, field, divField, divFields, divManies, primaries, countFields, anchorDelete;
            primaries = [];
            model = diagram.Models[appName][modelName];
            root = $("#"+ diagram.Container);
            divBox = $("<DIV>");
            divBox.attr("id", "diagramBox_"+ modelName);
            divBox.css({
                "left": (parseInt(Math.random() * 55 + 1) * 10) + "px",
                "top": (parseInt(Math.random() * 25 + 1) * 10) + "px"
            });
            divBox.addClass("body");
            divTitle = $("<DIV>");
            divTitle.addClass("title");
            diagram.setLabel(divTitle, model.name, false);
            anchorDelete = $("<A>");
            anchorDelete.html("x");
            anchorDelete.attr("href", "javascript:void(0);");
            anchorDelete.addClass("inline-deletelink");
            anchorDelete.click(function () {
                $("#diagramModelAnchor_"+ appName +"\\\."+ modelName).click();
            });
            divTitle.append(anchorDelete);
            divFields = $("<DIV>");
            countFields = 0;
            lengthFields = model.fields.length;
//            for(fieldName in model.fields) {
            for(var fieldIndex = 0; fieldIndex < lengthFields; fieldIndex++) {
                field = model.fields[fieldIndex];
                divField = $("<DIV>");
                divField.addClass("field");
                diagram.setLabel(divField, field.label, field.primary);
                divField.attr("id", "diagramBoxField_"+ appName +"."+ modelName +"."+ fieldName);
                if (field.type == "ForeignKey") {
                    divField.addClass("foreign");
                    divField.click(diagram.addRelated);
                    divBox.prepend(divField);
                } else if (field.type == "ManyToManyField") {
                    divField.addClass("many");
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
            divBox.draggable({
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
                    });
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
        };

        /**
         * Load the models from the schema
         */
        diagram.loadModels = function() {
            var graph, models, modelName;
            if (diagram.Models) {
                for(graph in diagram.Models) {
                    models = diagram.Models[graph];
                    for(modelName in models) {
                        diagram.addBox(graph, modelName);
                    }
                }
            }
        }
        diagram.loadModels();
    };
    $(document).ready(init);
})(jQuery);

diagram.Models = {
    "Sessions": {
        "Session": {
            "collapse": true,
            "fields": {
                "session_key": {
                    "label": "Session key",
                    "type": "CharField",
                    "name": "session_key",
                    "primary": true,
                    "blank": false
                },
                "expire_date": {
                    "label": "Expire date",
                    "type": "DateTimeField",
                    "name": "expire_date",
                    "primary": false,
                    "blank": false
                },
                "session_data": {
                    "label": "Session data",
                    "type": "TextField",
                    "name": "session_data",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "session_key",
            "relations": [],
            "name": "Session",
            "is_auto": false
        }
    },
    "Admin": {
        "LogEntry": {
            "collapse": true,
            "fields": {
                "action_flag": {
                    "label": "Action flag",
                    "type": "PositiveSmallIntegerField",
                    "name": "action_flag",
                    "primary": false,
                    "blank": false
                },
                "action_time": {
                    "label": "Action time",
                    "type": "DateTimeField",
                    "name": "action_time",
                    "primary": false,
                    "blank": true
                },
                "change_message": {
                    "label": "Change message",
                    "type": "TextField",
                    "name": "change_message",
                    "primary": false,
                    "blank": true
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                },
                "content_type": {
                    "target": {
                        "field": "id",
                        "model": "ContentType",
                        "name": "Contenttypes"
                    },
                    "name": "content_type",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Content type"
                },
                "object_repr": {
                    "label": "Object repr",
                    "type": "CharField",
                    "name": "object_repr",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "object_id": {
                    "label": "Object id",
                    "type": "TextField",
                    "name": "object_id",
                    "primary": false,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "content_type",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "ContentType",
                    "name": "Contenttypes"
                }
            }],
            "name": "LogEntry",
            "is_auto": false
        }
    },
    "Artworks": {
        "Virgin": {
            "collapse": false,
            "fields": {
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "apparition_date": {
                    "label": "Apparition date",
                    "type": "DateField",
                    "name": "apparition_date",
                    "primary": false,
                    "blank": true
                },
                "fm_apparition_place": {
                    "label": "Filemaker apparition place",
                    "type": "TextField",
                    "name": "fm_apparition_place",
                    "primary": false,
                    "blank": true
                },
                "apparition_place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "apparition_place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Apparition place"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "apparition_place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }],
            "name": "Virgin",
            "is_auto": false
        },
        "Serie": {
            "collapse": false,
            "fields": {
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "CharField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [],
            "name": "Serie",
            "is_auto": false
        },
        "Artwork": {
            "collapse": false,
            "fields": {
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                },
                "inscription": {
                    "label": "Inscription",
                    "type": "TextField",
                    "name": "inscription",
                    "primary": false,
                    "blank": true
                },
                "fm_original_place": {
                    "label": "Filemaker original place",
                    "type": "TextField",
                    "name": "fm_original_place",
                    "primary": false,
                    "blank": true
                },
                "creators": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "through": {
                            "field": "id",
                            "model": "Artwork_creators",
                            "name": "Artworks"
                        },
                        "name": "Creators"
                    },
                    "name": "creators",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Creators"
                },
                "fm_descriptors": {
                    "label": "Filemaker descriptors",
                    "type": "TextField",
                    "name": "fm_descriptors",
                    "primary": false,
                    "blank": true
                },
                "creation_year_end": {
                    "label": "Creation year ending",
                    "type": "IntegerField",
                    "name": "creation_year_end",
                    "primary": false,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "CharField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                },
                "fm_current_place": {
                    "label": "Filemaker current place",
                    "type": "TextField",
                    "name": "fm_current_place",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "virgins": {
                    "target": {
                        "field": "id",
                        "model": "Virgin",
                        "through": {
                            "field": "id",
                            "model": "ArtworkVirgin",
                            "name": "Artworks"
                        },
                        "name": "Artworks"
                    },
                    "name": "virgins",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Virgins"
                },
                "serie": {
                    "target": {
                        "field": "id",
                        "model": "Serie",
                        "name": "Artworks"
                    },
                    "name": "serie",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Serie"
                },
                "input_date": {
                    "label": "Input date",
                    "type": "DateTimeField",
                    "name": "input_date",
                    "primary": false,
                    "blank": true
                },
                "references": {
                    "target": {
                        "field": "id",
                        "model": "BibliographicReference",
                        "through": {
                            "field": "id",
                            "model": "ArtworkBibliography",
                            "name": "Artworks"
                        },
                        "name": "Base"
                    },
                    "name": "references",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "References"
                },
                "inventory": {
                    "label": "Inventory number",
                    "type": "CharField",
                    "name": "inventory",
                    "primary": false,
                    "blank": true
                },
                "current_place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "current_place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Current place"
                },
                "creation_year_start": {
                    "label": "Creation year beginning",
                    "type": "IntegerField",
                    "name": "creation_year_start",
                    "primary": false,
                    "blank": true
                },
                "images": {
                    "target": {
                        "field": "id",
                        "model": "Image",
                        "through": {
                            "field": "id",
                            "model": "Artwork_images",
                            "name": "Artworks"
                        },
                        "name": "Base"
                    },
                    "name": "images",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Images"
                },
                "fm_inventory": {
                    "label": "Filemaker inventory number",
                    "type": "TextField",
                    "name": "fm_inventory",
                    "primary": false,
                    "blank": true
                },
                "original_place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "original_place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Original place"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "size": {
                    "label": "Size",
                    "type": "CharField",
                    "name": "size",
                    "primary": false,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "original_place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "current_place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "serie",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Serie",
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "virgins",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Virgin",
                    "through": {
                        "field": "id",
                        "model": "ArtworkVirgin",
                        "name": "Artworks"
                    },
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "images",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Image",
                    "through": {
                        "field": "id",
                        "model": "Artwork_images",
                        "name": "Artworks"
                    },
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "references",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "BibliographicReference",
                    "through": {
                        "field": "id",
                        "model": "ArtworkBibliography",
                        "name": "Artworks"
                    },
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "creators",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "through": {
                        "field": "id",
                        "model": "Artwork_creators",
                        "name": "Artworks"
                    },
                    "name": "Creators"
                }
            }],
            "name": "Artwork",
            "is_auto": false
        },
        "ArtworkVirgin": {
            "collapse": true,
            "fields": {
                "virgin": {
                    "target": {
                        "field": "id",
                        "model": "Virgin",
                        "name": "Artworks"
                    },
                    "name": "virgin",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Virgin"
                },
                "episode": {
                    "label": "Episode",
                    "type": "CharField",
                    "name": "episode",
                    "primary": false,
                    "blank": true
                },
                "artwork": {
                    "target": {
                        "field": "id",
                        "model": "Artwork",
                        "name": "Artworks"
                    },
                    "name": "artwork",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Artwork"
                },
                "miraculous": {
                    "label": "Miraculous",
                    "type": "NullBooleanField",
                    "name": "miraculous",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "ethnic": {
                    "label": "Ethnic",
                    "type": "CharField",
                    "name": "ethnic",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "main_theme": {
                    "label": "Main theme",
                    "type": "NullBooleanField",
                    "name": "main_theme",
                    "primary": false,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "artwork",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Artwork",
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "virgin",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Virgin",
                    "name": "Artworks"
                }
            }],
            "name": "ArtworkVirgin",
            "is_auto": false
        },
        "ArtworkBibliography": {
            "collapse": true,
            "fields": {
                "source": {
                    "label": "Source",
                    "type": "CharField",
                    "name": "source",
                    "primary": false,
                    "blank": true
                },
                "bibliography": {
                    "target": {
                        "field": "id",
                        "model": "BibliographicReference",
                        "name": "Base"
                    },
                    "name": "bibliography",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Bibliographic reference"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "artwork": {
                    "target": {
                        "field": "id",
                        "model": "Artwork",
                        "name": "Artworks"
                    },
                    "name": "artwork",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Artwork"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "artwork",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Artwork",
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "bibliography",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "BibliographicReference",
                    "name": "Base"
                }
            }],
            "name": "ArtworkBibliography",
            "is_auto": false
        },
        "Artwork_creators": {
            "collapse": true,
            "fields": {
                "creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Creator"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "artwork": {
                    "target": {
                        "field": "id",
                        "model": "Artwork",
                        "name": "Artworks"
                    },
                    "name": "artwork",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Artwork"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "artwork",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Artwork",
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }],
            "name": "Artwork_creators",
            "is_auto": true
        },
        "Artwork_images": {
            "collapse": true,
            "fields": {
                "image": {
                    "target": {
                        "field": "id",
                        "model": "Image",
                        "name": "Base"
                    },
                    "name": "image",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Image"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "artwork": {
                    "target": {
                        "field": "id",
                        "model": "Artwork",
                        "name": "Artworks"
                    },
                    "name": "artwork",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Artwork"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "artwork",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Artwork",
                    "name": "Artworks"
                }
            }, {
                "arrows": "",
                "source": "image",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Image",
                    "name": "Base"
                }
            }],
            "name": "Artwork_images",
            "is_auto": true
        }
    },
    "Django_descriptors": {
        "Descriptor": {
            "collapse": false,
            "fields": {
                "description": {
                    "label": "Description",
                    "type": "TextField",
                    "name": "description",
                    "primary": false,
                    "blank": true
                },
                "parent": {
                    "target": {
                        "field": "id",
                        "model": "Descriptor",
                        "name": "Django_descriptors"
                    },
                    "name": "parent",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Parent"
                },
                "path": {
                    "label": "Path",
                    "type": "TextField",
                    "name": "path",
                    "primary": false,
                    "blank": false
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "parent",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Descriptor",
                    "name": "Django_descriptors"
                }
            }, {
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }],
            "name": "Descriptor",
            "is_auto": false
        },
        "DescribedItem": {
            "collapse": true,
            "fields": {
                "descriptor": {
                    "target": {
                        "field": "id",
                        "model": "Descriptor",
                        "name": "Django_descriptors"
                    },
                    "name": "descriptor",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Descriptor"
                },
                "object_id": {
                    "label": "Object id",
                    "type": "PositiveIntegerField",
                    "name": "object_id",
                    "primary": false,
                    "blank": false
                },
                "content_type": {
                    "target": {
                        "field": "id",
                        "model": "ContentType",
                        "name": "Contenttypes"
                    },
                    "name": "content_type",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Content type"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "value": {
                    "label": "Value",
                    "type": "CharField",
                    "name": "value",
                    "primary": false,
                    "blank": true
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "descriptor",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Descriptor",
                    "name": "Django_descriptors"
                }
            }, {
                "arrows": "",
                "source": "content_type",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "ContentType",
                    "name": "Contenttypes"
                }
            }, {
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }],
            "name": "DescribedItem",
            "is_auto": false
        }
    },
    "Sites": {
        "Site": {
            "collapse": false,
            "fields": {
                "domain": {
                    "label": "Domain name",
                    "type": "CharField",
                    "name": "domain",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "name": {
                    "label": "Display name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [],
            "name": "Site",
            "is_auto": false
        }
    },
    "Postgis": {
        "GeometryColumns": {
            "collapse": true,
            "fields": {
                "f_table_schema": {
                    "label": "F table schema",
                    "type": "CharField",
                    "name": "f_table_schema",
                    "primary": false,
                    "blank": false
                },
                "f_table_catalog": {
                    "label": "F table catalog",
                    "type": "CharField",
                    "name": "f_table_catalog",
                    "primary": false,
                    "blank": false
                },
                "srid": {
                    "label": "Srid",
                    "type": "IntegerField",
                    "name": "srid",
                    "primary": true,
                    "blank": false
                },
                "coord_dimension": {
                    "label": "Coord dimension",
                    "type": "IntegerField",
                    "name": "coord_dimension",
                    "primary": false,
                    "blank": false
                },
                "f_table_name": {
                    "label": "F table name",
                    "type": "CharField",
                    "name": "f_table_name",
                    "primary": false,
                    "blank": false
                },
                "type": {
                    "label": "Type",
                    "type": "CharField",
                    "name": "type",
                    "primary": false,
                    "blank": false
                },
                "f_geometry_column": {
                    "label": "F geometry column",
                    "type": "CharField",
                    "name": "f_geometry_column",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "srid",
            "relations": [],
            "name": "GeometryColumns",
            "is_auto": false
        },
        "SpatialRefSys": {
            "collapse": true,
            "fields": {
                "srid": {
                    "label": "Srid",
                    "type": "IntegerField",
                    "name": "srid",
                    "primary": true,
                    "blank": false
                },
                "auth_name": {
                    "label": "Auth name",
                    "type": "CharField",
                    "name": "auth_name",
                    "primary": false,
                    "blank": false
                },
                "proj4text": {
                    "label": "Proj4text",
                    "type": "CharField",
                    "name": "proj4text",
                    "primary": false,
                    "blank": false
                },
                "auth_srid": {
                    "label": "Auth srid",
                    "type": "IntegerField",
                    "name": "auth_srid",
                    "primary": false,
                    "blank": false
                },
                "srtext": {
                    "label": "Srtext",
                    "type": "CharField",
                    "name": "srtext",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "srid",
            "relations": [],
            "name": "SpatialRefSys",
            "is_auto": false
        }
    },
    "Flatpages": {
        "FlatPage": {
            "collapse": true,
            "fields": {
                "content": {
                    "label": "Content",
                    "type": "TextField",
                    "name": "content",
                    "primary": false,
                    "blank": true
                },
                "sites": {
                    "target": {
                        "field": "id",
                        "model": "Site",
                        "through": {
                            "field": "id",
                            "model": "FlatPage_sites",
                            "name": "Flatpages"
                        },
                        "name": "Sites"
                    },
                    "name": "sites",
                    "blank": false,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Sites"
                },
                "registration_required": {
                    "label": "Registration required",
                    "type": "BooleanField",
                    "name": "registration_required",
                    "primary": false,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "CharField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                },
                "url": {
                    "label": "Url",
                    "type": "CharField",
                    "name": "url",
                    "primary": false,
                    "blank": false
                },
                "enable_comments": {
                    "label": "Enable comments",
                    "type": "BooleanField",
                    "name": "enable_comments",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "template_name": {
                    "label": "Template name",
                    "type": "CharField",
                    "name": "template_name",
                    "primary": false,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "sites",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Site",
                    "through": {
                        "field": "id",
                        "model": "FlatPage_sites",
                        "name": "Flatpages"
                    },
                    "name": "Sites"
                }
            }],
            "name": "FlatPage",
            "is_auto": false
        },
        "FlatPage_sites": {
            "collapse": true,
            "fields": {
                "flatpage": {
                    "target": {
                        "field": "id",
                        "model": "FlatPage",
                        "name": "Flatpages"
                    },
                    "name": "flatpage",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Flatpage"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "site": {
                    "target": {
                        "field": "id",
                        "model": "Site",
                        "name": "Sites"
                    },
                    "name": "site",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Site"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "flatpage",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "FlatPage",
                    "name": "Flatpages"
                }
            }, {
                "arrows": "",
                "source": "site",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Site",
                    "name": "Sites"
                }
            }],
            "name": "FlatPage_sites",
            "is_auto": true
        }
    },
    "Contenttypes": {
        "ContentType": {
            "collapse": true,
            "fields": {
                "model": {
                    "label": "Python model class name",
                    "type": "CharField",
                    "name": "model",
                    "primary": false,
                    "blank": false
                },
                "app_label": {
                    "label": "App label",
                    "type": "CharField",
                    "name": "app_label",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [],
            "name": "ContentType",
            "is_auto": false
        }
    },
    "Base": {
        "Image": {
            "collapse": false,
            "fields": {
                "url": {
                    "label": "Url",
                    "type": "URLField",
                    "name": "url",
                    "primary": false,
                    "blank": true
                },
                "image": {
                    "label": "Image",
                    "type": "ImageField",
                    "name": "image",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "CharField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [],
            "name": "Image",
            "is_auto": false
        },
        "GeospatialReference": {
            "collapse": false,
            "fields": {
                "date": {
                    "label": "Date",
                    "type": "DateTimeField",
                    "name": "date",
                    "primary": false,
                    "blank": true
                },
                "description": {
                    "label": "Description",
                    "type": "TextField",
                    "name": "description",
                    "primary": false,
                    "blank": true
                },
                "address": {
                    "label": "Address",
                    "type": "CharField",
                    "name": "address",
                    "primary": false,
                    "blank": true
                },
                "geometry": {
                    "label": "Geometry",
                    "type": "MultiPolygonField",
                    "name": "geometry",
                    "primary": false,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "CharField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                },
                "point": {
                    "label": "Point",
                    "type": "PointField",
                    "name": "point",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [],
            "name": "GeospatialReference",
            "is_auto": false
        },
        "BibliographicReference": {
            "collapse": false,
            "fields": {
                "isbn": {
                    "label": "Isbn",
                    "type": "CharField",
                    "name": "isbn",
                    "primary": false,
                    "blank": true
                },
                "authors": {
                    "label": "Authors",
                    "type": "TextField",
                    "name": "authors",
                    "primary": false,
                    "blank": true
                },
                "url": {
                    "label": "Url",
                    "type": "URLField",
                    "name": "url",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "title": {
                    "label": "Title",
                    "type": "TextField",
                    "name": "title",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [],
            "name": "BibliographicReference",
            "is_auto": false
        }
    },
    "Auth": {
        "Group": {
            "collapse": false,
            "fields": {
                "permissions": {
                    "target": {
                        "field": "id",
                        "model": "Permission",
                        "through": {
                            "field": "id",
                            "model": "Group_permissions",
                            "name": "Auth"
                        },
                        "name": "Auth"
                    },
                    "name": "permissions",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Permissions"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "permissions",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Permission",
                    "through": {
                        "field": "id",
                        "model": "Group_permissions",
                        "name": "Auth"
                    },
                    "name": "Auth"
                }
            }],
            "name": "Group",
            "is_auto": false
        },
        "User": {
            "collapse": false,
            "fields": {
                "username": {
                    "label": "Username",
                    "type": "CharField",
                    "name": "username",
                    "primary": false,
                    "blank": false
                },
                "first_name": {
                    "label": "First name",
                    "type": "CharField",
                    "name": "first_name",
                    "primary": false,
                    "blank": true
                },
                "last_name": {
                    "label": "Last name",
                    "type": "CharField",
                    "name": "last_name",
                    "primary": false,
                    "blank": true
                },
                "is_active": {
                    "label": "Active",
                    "type": "BooleanField",
                    "name": "is_active",
                    "primary": false,
                    "blank": true
                },
                "email": {
                    "label": "E-mail address",
                    "type": "EmailField",
                    "name": "email",
                    "primary": false,
                    "blank": true
                },
                "is_superuser": {
                    "label": "Superuser status",
                    "type": "BooleanField",
                    "name": "is_superuser",
                    "primary": false,
                    "blank": true
                },
                "is_staff": {
                    "label": "Staff status",
                    "type": "BooleanField",
                    "name": "is_staff",
                    "primary": false,
                    "blank": true
                },
                "last_login": {
                    "label": "Last login",
                    "type": "DateTimeField",
                    "name": "last_login",
                    "primary": false,
                    "blank": false
                },
                "groups": {
                    "target": {
                        "field": "id",
                        "model": "Group",
                        "through": {
                            "field": "id",
                            "model": "User_groups",
                            "name": "Auth"
                        },
                        "name": "Auth"
                    },
                    "name": "groups",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Groups"
                },
                "user_permissions": {
                    "target": {
                        "field": "id",
                        "model": "Permission",
                        "through": {
                            "field": "id",
                            "model": "User_user_permissions",
                            "name": "Auth"
                        },
                        "name": "Auth"
                    },
                    "name": "user_permissions",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "User permissions"
                },
                "password": {
                    "label": "Password",
                    "type": "CharField",
                    "name": "password",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "date_joined": {
                    "label": "Date joined",
                    "type": "DateTimeField",
                    "name": "date_joined",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "groups",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Group",
                    "through": {
                        "field": "id",
                        "model": "User_groups",
                        "name": "Auth"
                    },
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "user_permissions",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Permission",
                    "through": {
                        "field": "id",
                        "model": "User_user_permissions",
                        "name": "Auth"
                    },
                    "name": "Auth"
                }
            }],
            "name": "User",
            "is_auto": false
        },
        "User_user_permissions": {
            "collapse": true,
            "fields": {
                "permission": {
                    "target": {
                        "field": "id",
                        "model": "Permission",
                        "name": "Auth"
                    },
                    "name": "permission",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Permission"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "permission",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Permission",
                    "name": "Auth"
                }
            }],
            "name": "User_user_permissions",
            "is_auto": true
        },
        "Group_permissions": {
            "collapse": true,
            "fields": {
                "group": {
                    "target": {
                        "field": "id",
                        "model": "Group",
                        "name": "Auth"
                    },
                    "name": "group",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Group"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "permission": {
                    "target": {
                        "field": "id",
                        "model": "Permission",
                        "name": "Auth"
                    },
                    "name": "permission",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Permission"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "group",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Group",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "permission",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Permission",
                    "name": "Auth"
                }
            }],
            "name": "Group_permissions",
            "is_auto": true
        },
        "Message": {
            "collapse": true,
            "fields": {
                "message": {
                    "label": "Message",
                    "type": "TextField",
                    "name": "message",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }],
            "name": "Message",
            "is_auto": false
        },
        "Permission": {
            "collapse": true,
            "fields": {
                "codename": {
                    "label": "Codename",
                    "type": "CharField",
                    "name": "codename",
                    "primary": false,
                    "blank": false
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "content_type": {
                    "target": {
                        "field": "id",
                        "model": "ContentType",
                        "name": "Contenttypes"
                    },
                    "name": "content_type",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Content type"
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "content_type",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "ContentType",
                    "name": "Contenttypes"
                }
            }],
            "name": "Permission",
            "is_auto": false
        },
        "User_groups": {
            "collapse": true,
            "fields": {
                "group": {
                    "target": {
                        "field": "id",
                        "model": "Group",
                        "name": "Auth"
                    },
                    "name": "group",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Group"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "group",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Group",
                    "name": "Auth"
                }
            }],
            "name": "User_groups",
            "is_auto": true
        }
    },
    "Creators": {
        "WorkingHistory": {
            "collapse": false,
            "fields": {
                "start_year": {
                    "label": "Start year",
                    "type": "IntegerField",
                    "name": "start_year",
                    "primary": false,
                    "blank": true
                },
                "place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Place"
                },
                "creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Creator"
                },
                "end_year": {
                    "label": "End year",
                    "type": "IntegerField",
                    "name": "end_year",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "fm_place": {
                    "label": "Filemaker place",
                    "type": "TextField",
                    "name": "fm_place",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }],
            "name": "WorkingHistory",
            "is_auto": false
        },
        "School": {
            "collapse": false,
            "fields": {
                "affiliation": {
                    "label": "Affiliation",
                    "type": "CharField",
                    "name": "affiliation",
                    "primary": false,
                    "blank": true
                },
                "start_year": {
                    "label": "Start year",
                    "type": "IntegerField",
                    "name": "start_year",
                    "primary": false,
                    "blank": true
                },
                "place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Place"
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                },
                "end_year": {
                    "label": "End year",
                    "type": "IntegerField",
                    "name": "end_year",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "fm_place": {
                    "label": "Filemaker place",
                    "type": "TextField",
                    "name": "fm_place",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }],
            "name": "School",
            "is_auto": false
        },
        "CreatorBibliography": {
            "collapse": true,
            "fields": {
                "source": {
                    "label": "Source",
                    "type": "CharField",
                    "name": "source",
                    "primary": false,
                    "blank": true
                },
                "bibliography": {
                    "target": {
                        "field": "id",
                        "model": "BibliographicReference",
                        "name": "Base"
                    },
                    "name": "bibliography",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Bibliographic reference"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Creator"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "bibliography",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "BibliographicReference",
                    "name": "Base"
                }
            }],
            "name": "CreatorBibliography",
            "is_auto": false
        },
        "Creator": {
            "collapse": false,
            "fields": {
                "user": {
                    "target": {
                        "field": "id",
                        "model": "User",
                        "name": "Auth"
                    },
                    "name": "user",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "User"
                },
                "fm_bibliography": {
                    "label": "Filemaker bibliography",
                    "type": "TextField",
                    "name": "fm_bibliography",
                    "primary": false,
                    "blank": true
                },
                "school": {
                    "target": {
                        "field": "id",
                        "model": "School",
                        "name": "Creators"
                    },
                    "name": "school",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "School"
                },
                "gender": {
                    "label": "Gender",
                    "type": "CharField",
                    "name": "gender",
                    "primary": false,
                    "blank": true
                },
                "name": {
                    "label": "Name",
                    "type": "CharField",
                    "name": "name",
                    "primary": false,
                    "blank": false
                },
                "activity_end_year": {
                    "label": "Activity end year",
                    "type": "IntegerField",
                    "name": "activity_end_year",
                    "primary": false,
                    "blank": true
                },
                "activity_start_year": {
                    "label": "Activity start year",
                    "type": "IntegerField",
                    "name": "activity_start_year",
                    "primary": false,
                    "blank": true
                },
                "notes": {
                    "label": "Notes",
                    "type": "TextField",
                    "name": "notes",
                    "primary": false,
                    "blank": true
                },
                "fm_birth_place": {
                    "label": "Filemaker birth place",
                    "type": "TextField",
                    "name": "fm_birth_place",
                    "primary": false,
                    "blank": true
                },
                "death_year": {
                    "label": "Death year",
                    "type": "IntegerField",
                    "name": "death_year",
                    "primary": false,
                    "blank": true
                },
                "masters": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "through": {
                            "field": "id",
                            "model": "Creator_masters",
                            "name": "Creators"
                        },
                        "name": "Creators"
                    },
                    "name": "masters",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Masters"
                },
                "birth_place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "birth_place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Birth place"
                },
                "input_date": {
                    "label": "Input date",
                    "type": "DateTimeField",
                    "name": "input_date",
                    "primary": false,
                    "blank": true
                },
                "death_place": {
                    "target": {
                        "field": "id",
                        "model": "GeospatialReference",
                        "name": "Base"
                    },
                    "name": "death_place",
                    "blank": true,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Death place"
                },
                "images": {
                    "target": {
                        "field": "id",
                        "model": "Image",
                        "through": {
                            "field": "id",
                            "model": "Creator_images",
                            "name": "Creators"
                        },
                        "name": "Base"
                    },
                    "name": "images",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "Images"
                },
                "references": {
                    "target": {
                        "field": "id",
                        "model": "BibliographicReference",
                        "through": {
                            "field": "id",
                            "model": "CreatorBibliography",
                            "name": "Creators"
                        },
                        "name": "Base"
                    },
                    "name": "references",
                    "blank": true,
                    "type": "ManyToManyField",
                    "primary": false,
                    "label": "References"
                },
                "fm_descriptors": {
                    "label": "Filemaker descriptors",
                    "type": "TextField",
                    "name": "fm_descriptors",
                    "primary": false,
                    "blank": true
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "fm_death_place": {
                    "label": "Filemaker death place",
                    "type": "TextField",
                    "name": "fm_death_place",
                    "primary": false,
                    "blank": true
                },
                "birth_year": {
                    "label": "Birth year",
                    "type": "IntegerField",
                    "name": "birth_year",
                    "primary": false,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "birth_place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "death_place",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "GeospatialReference",
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "school",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "School",
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "user",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "User",
                    "name": "Auth"
                }
            }, {
                "arrows": "",
                "source": "masters",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "through": {
                        "field": "id",
                        "model": "Creator_masters",
                        "name": "Creators"
                    },
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "references",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "BibliographicReference",
                    "through": {
                        "field": "id",
                        "model": "CreatorBibliography",
                        "name": "Creators"
                    },
                    "name": "Base"
                }
            }, {
                "arrows": "",
                "source": "images",
                "type": "ManyToManyField",
                "target": {
                    "field": "id",
                    "model": "Image",
                    "through": {
                        "field": "id",
                        "model": "Creator_images",
                        "name": "Creators"
                    },
                    "name": "Base"
                }
            }],
            "name": "Creator",
            "is_auto": false
        },
        "Creator_masters": {
            "collapse": true,
            "fields": {
                "to_creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "to_creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "To creator"
                },
                "from_creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "from_creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "From creator"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "from_creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "to_creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }],
            "name": "Creator_masters",
            "is_auto": true
        },
        "Creator_images": {
            "collapse": true,
            "fields": {
                "image": {
                    "target": {
                        "field": "id",
                        "model": "Image",
                        "name": "Base"
                    },
                    "name": "image",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Image"
                },
                "id": {
                    "label": "Id",
                    "type": "AutoField",
                    "name": "id",
                    "primary": true,
                    "blank": true
                },
                "creator": {
                    "target": {
                        "field": "id",
                        "model": "Creator",
                        "name": "Creators"
                    },
                    "name": "creator",
                    "blank": false,
                    "type": "ForeignKey",
                    "primary": false,
                    "label": "Creator"
                }
            },
            "primary": "id",
            "relations": [{
                "arrows": "",
                "source": "creator",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Creator",
                    "name": "Creators"
                }
            }, {
                "arrows": "",
                "source": "image",
                "type": "ForeignKey",
                "target": {
                    "field": "id",
                    "model": "Image",
                    "name": "Base"
                }
            }],
            "name": "Creator_images",
            "is_auto": true
        }
    }
};
