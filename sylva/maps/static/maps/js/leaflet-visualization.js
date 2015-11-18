// JSHint options

/* global window:true, document:true, setTimeout:true, console:true,
 * jQuery:true, sylva:true, prompt:true, alert:true, sigma:true, clearTimeout
 */

/****************************************************************************
 * Leaflet.js visualization
 ****************************************************************************/

;(function(sylva, $, window, document, undefined) {
  var CENTER = '_center_';
  var GENERAL = '_GENERAL_';
  var MAX_TO_HEAT = 1000;

  var that = null;
  var map = null;
  var features = null;
  var featuresColor = null;
  var visibleFeatures = null;

  var Leaflet = {

    // TODO: Use 'nodetype-id' instead of 'nodetype'
    init: function() {
      that = this;

      // TODO: Remove this in a near future
      window.L_DISABLE_3D = true;

      map = L.map('map').setView([0, 0], 2);
      // TODO: Get the tiles from the 'settings.py' file
      L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      setTimeout(function () {
        map.invalidateSize();
      }, 0);

      that.addNodes();
      that.createLegend();
      that.createCollapsibles();

      // Events!
      $('.show-hide-features').on('click', that.showHideFeatures);
    },

    addNodes: function() {
      features = {};
      featuresColor = {};
      var featuresForBounding = [];
      var heatmapPopups = [];

      $.each(sylva.graph.nodes, function(index, node) {
        var nodeFeatures = [];

        $.each(node.properties, function(name, property) {
          var geoProperty;
          var isJSON = true;
          try {
            geoProperty = JSON.parse(property);
          } catch (err) {
            isJSON = false;
          }

          if (isJSON && geoProperty.hasOwnProperty('type') && (geoProperty.type === 'Point' || geoProperty.type === 'LineString' || geoProperty.type === 'Polygon')) {
            var feature = null;

            // Adjusting the visualization to the type
            if (geoProperty.type === 'Point') {
              var icon = L.MakiMarkers.icon({
                icon: null,
                color: node.color,
                size: 'l'
              });
              feature = L.geoJson(geoProperty, {
                pointToLayer: function(feature, latlng) {
                  return L.marker(latlng, {
                    icon: icon
                  });
                }
              });

            } else {
              var style = {
                color: node.color,
                opacity: 0.8
              };
              feature = L.geoJson(geoProperty, {style: style});
            }

            feature.bindPopup(node.label);

            // Checking the `features` structure
            features[node.nodetype] = features[node.nodetype] || {};
            features[node.nodetype][name] = features[node.nodetype][name] || [];

            // Pushing the GeoJSON feature and other properties
            featuresColor[node.nodetype] = node.color;
            features[node.nodetype][name].push(feature);
            featuresForBounding.push(feature);
            nodeFeatures.push(feature);
          }
        });

        // Calculating center of all spatial properties of the node
        if (nodeFeatures.length > 0) {
          var nodeFeatureGroup = L.featureGroup(nodeFeatures);
          var center = nodeFeatureGroup.getBounds().getCenter();

          var icon = L.MakiMarkers.icon({
            icon: null,
            color: node.color,
            size: 'l'
          });
          var feature = L.marker(center, {icon: icon});
          feature.bindPopup(node.label);

          features[node.nodetype][CENTER] = features[node.nodetype][CENTER] || [];
          features[node.nodetype][CENTER].push(feature);
        }
      });

      // Creating feature/layer groups and adding them to the map
      $.each(features, function(nodetype, properties) {
        $.each(properties, function(property, featuresArray) {

          // Creating regular layer
          if (featuresArray.length < MAX_TO_HEAT) {
            features[nodetype][property] = L.featureGroup(featuresArray);

          // Creating heat layer
          } else {
            // Creating the popup for the heatmaps
            heatmapPopups.push({
              bounds: L.featureGroup(featuresArray).getBounds(),
              nodetype: nodetype,
              property: property
            });

            var coorsArray = [];
            $.each(featuresArray, function (index1, feature) {

              // Simple markers (center points)
              if (typeof feature.getLatLng === 'function') {
                var latLng = feature.getLatLng();
                coorsArray.push([latLng.lat, latLng.lng]);

              // GeoJSONs
              } else {
                var pointCoordinates = feature.getLayers()[0].feature.geometry.coordinates;

                // Points
                if (typeof pointCoordinates[0] === "number") {
                  coorsArray.push(pointCoordinates.reverse());

                // Lines
                } else {
                  $.each(pointCoordinates, function (index2, lineCoordinates) {
                    if (typeof lineCoordinates[0] === "number") {
                      coorsArray.push(lineCoordinates.reverse());

                    // Areas
                    } else {
                      $.each(lineCoordinates, function (index3, areaCoordinates) {
                        coorsArray.push(areaCoordinates.reverse());
                      });
                    }
                  });
                }
              }
            });

            // Really creating heat layer
            features[nodetype][property] = L.heatLayer(coorsArray, {
              radius: 10,
              maxZoom: 20
            });
          }

          // Adding created layer (regular or heat) to the map
          if (property !== CENTER) {
            features[nodetype][property].addTo(map);
          }
        })
      });

      // More events! This one is for popups to appear in heatmap.
      map.on('click', function(event) {
        $.each(heatmapPopups, function(index, heatmapPopup) {
          if (heatmapPopup.bounds.contains(event.latlng)) {
            var showPopup = visibleFeatures[heatmapPopup.nodetype][heatmapPopup.property];
            if (showPopup)
            L.popup()
              .setLatLng(event.latlng)
              .setContent(heatmapPopup.nodetype + ' - ' + heatmapPopup.property)
              .openOn(map);
            return false;
          }
        })
      });

      // Centering the map
      var featureGroup = L.featureGroup(featuresForBounding);
      setTimeout(function() {
        map.fitBounds(featureGroup.getBounds());
      }, 0);
    },

    createLegend: function() {
      // TODO: Reduce this function
      $('#map-types').append('<h2 class="collapsible-header">'
        + gettext('Types') + '</h2>');
      $('#map-types').append($('<ul>'));
      var list = $('#map-types ul');
      list.css({
        listStyleType: 'none',
        marginTop: '-5px'
      });

      visibleFeatures = {};
      $.each(features, function(type, properties) {
        visibleFeatures[type] = {};
        visibleFeatures[type][GENERAL] = true;

        var listElement = $('<li>')
          .css({
            minHeight: '20px',
            paddingLeft: '3px',
            marginTop: '7px'
          })
          .append($('<i>')
            .addClass('fa fa-eye')
            .addClass('show-hide-features')
            .attr('data-action', 'hide')
            .attr('data-nodetype', type)
            .css({
              marginRight: '3px',
              width: '1em',
              height: '1em',
              cursor: 'pointer',
              verticalAlign: '-2px'
            }))
          .append($('<span>')
            .addClass('change-features-color')
            .attr('data-color', featuresColor[type])
            .attr('data-nodetype', type)
            .css({
              backgroundColor: featuresColor[type],
              display: 'inline-block',
              width: '16px',
              height: '16px',
              marginRight: '5px',
              verticalAlign: 'middle'
            }))
          .append($('<span>')
            .css({
              paddingLeft: '0.3em',
              verticalAlign: 'middle',
              fontSize: '115%'
            })
            .html(type)
          );

          $.each(properties, function(property, propertyList) {
            if (property !== CENTER) {
              visibleFeatures[type][property] = true;

              var propertyElement = $('<span>')
                .css({
                  display: 'block',
                  marginLeft: '8px'
                })
                .append($('<i>')
                  .addClass('fa fa-eye')
                  .addClass('show-hide-features')
                  .attr('data-action', 'hide')
                  .attr('data-nodetype', type)
                  .attr('data-property', property)
                  .css({
                    marginRight: '3px',
                    width: '1em',
                    height: '1em',
                    cursor: 'pointer',
                    verticalAlign: '-2px'
                  }))
                .append($('<span>')
                  .css({
                    paddingLeft: '0.3em',
                    verticalAlign: 'middle'
                  })
                  .html(property)
              );

              listElement.append(propertyElement);
            }
          });

        list.append(listElement);
      });

      if (Object.keys(features).length <= 0) {
        $('#map-types').hide();
      }
    },

    createCollapsibles: function() {
      var draggableSettings = {
        containment: '#map',
        cursor: 'move',
        create: function(event, ui) {
          $('#' + event.target.id).css({
            top: 10,
            left: 55
          });
        },
        start: function(event, ui) {
          $('#' + event.target.id).accordion('disable');
        },
        /* Don't need it here, in the map viz
        drag: function(event, ui) {
          $(document).scrollTop(0);
          $(document).scrollLeft(0);
        },*/
        stop: function(event, ui) {
          setTimeout(function() {
            $('#' + event.target.id).accordion('enable');
          }, 50);
        }
      };

      var collapsibleSettings = {
        collapsible: true,
        animate: 150,
        create: function(event, ui) {
          var box = $(event.target);
          var children = box.children();
          var header = children.first();
          var body = $(children[1]);
          var span = header.children().first();

          // The next lines remove jQueryUI style from the boxes.
          box.removeClass('ui-widget ui-accordion');
          header.removeClass('ui-accordion-icons ' +
            'ui-accordion-header ui-helper-reset ui-state-default');
          body.removeClass('ui-accordion-content ui-widget-content');
          body.css('height', '');
          span.remove();
        },
        activate: function(event, ui) {
          // This lines control the arrow icon.
          var span = $(event.target).children().first().children().first();
          if (span.hasClass('fa-chevron-circle-down')) {
            span.removeClass('fa-chevron-circle-down');
            span.addClass('fa-chevron-circle-right');
          } else {
            span.removeClass('fa-chevron-circle-right');
            span.addClass('fa-chevron-circle-down');
          }
        }
      };

      $('#map-types ul').hover(function() {
        $('#map-types ul').css({
          overflowY: 'auto'
        });
      }, function(){
        $('#map-types ul').css({
          overflowY: 'hidden'
        });
      });

      $('#map-types').hover(function() {
        map.dragging.disable();
        map.doubleClickZoom.disable();
        map.scrollWheelZoom.disable();
      }, function() {
        map.dragging.enable();
        map.doubleClickZoom.enable();
        map.scrollWheelZoom.enable();
      });

      $('#map-types').draggable(draggableSettings);
      $('#map-types').accordion(collapsibleSettings);

      $('.collapsible-header').each(function(i) {
        $(this).text(' ' + $(this).text());
        var icon = 'fa-chevron-circle-down';
        $(this).prepend('<span class="fa ' + icon + ' fa-fw" style="display: inline;"></span>');
      });
    },

    showHideFeatures: function() {
      var nodetype = $(this).attr('data-nodetype');
      var property = $(this).attr('data-property');

      // Hide or show the sub-elements
      if (typeof property === 'undefined') {
        var action = $(this).attr('data-action');
        var iElements = $(this).siblings().children('i');

        $.each(iElements, function(index, iElement) {
          var iAction = $(iElement).attr('data-action');
          if (action === iAction) {
            that.showHideFeaturesIndividually($(iElement));
          }
        });

      // Hide or show a sub-element
      } else {
        that.showHideFeaturesIndividually($(this));
      }
    },

    showHideFeaturesIndividually: function(iElement) {
      var nodetype = iElement.attr('data-nodetype');
      var property = iElement.attr('data-property');
      var action = iElement.attr('data-action');

      if (action == "hide") {
        iElement.attr('data-action', 'show');
        iElement.removeClass('fa-eye');
        iElement.addClass('fa-eye-slash');

        if (typeof property !== 'undefined') {
          map.removeLayer(features[nodetype][property]);

        } else {
          property = GENERAL;
        }
        visibleFeatures[nodetype][property] = false;

      } else {
        iElement.attr('data-action', 'hide');
        iElement.removeClass('fa-eye-slash');
        iElement.addClass('fa-eye');

        if (typeof property !== 'undefined') {
          map.addLayer(features[nodetype][property]);

        } else {
          property = GENERAL;
        }
        visibleFeatures[nodetype][property] = true;
      }

      /* The next bock will 'show or hide' an element if all it's
       * sub-elements are 'shown or hidden'.
       */
      var or = false;
      var and = true;
      $.each(visibleFeatures[nodetype], function(type, value) {
        if (type !== GENERAL) {
          or = or || value;
          and = and && value;
        }
      });

      var current = visibleFeatures[nodetype][property];
      var general = visibleFeatures[nodetype][GENERAL];
      if (or === and && current !== general) {
        var iElementUncle = iElement.parent().siblings('i');
        that.showHideFeaturesIndividually($(iElementUncle[0]));
      }
    }

  };

  // Reveal module.
  window.sylva.Leaflet = Leaflet;

})(sylva, jQuery, window, document);