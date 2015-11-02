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

  var that = null;
  var map = null;
  var features = null;
  var visibleFeatures = null;

  var Leaflet = {

    init: function() {
      that = this;

      map = L.map('map').setView([0, 0], 2);
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
      var featuresForBounding = [];

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
            var feature = L.geoJson(geoProperty).addTo(map);
            feature.bindPopup(node.label);

            // Checking the `features` structure
            features[node.nodetype] = features[node.nodetype] || {};
            features[node.nodetype][name] = features[node.nodetype][name] || [];

            // Pushing the feature
            features[node.nodetype][name].push(feature);
            featuresForBounding.push(feature);
            nodeFeatures.push(feature);
          }
        });

        // Calculating center of all spatial properties of the node
        if (nodeFeatures.length > 0) {
          var nodeFeatureGroup = L.featureGroup(nodeFeatures);
          var center = nodeFeatureGroup.getBounds().getCenter();

          var feature = L.marker(center);
          feature.bindPopup(node.label);

          features[node.nodetype][CENTER] = features[node.nodetype][CENTER] || [];
          features[node.nodetype][CENTER].push(feature);
        }
      });

      // TODO: Delete this
      sylva.features = features;

      // Centering the map
      var featureGroup = L.featureGroup(featuresForBounding);
      setTimeout(function() {
        map.fitBounds(featureGroup.getBounds());
      }, 0);
    },

    createLegend: function() {
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
                  marginLeft: '7px'
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
          var header =  children.first();
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
          $.each(features[nodetype][property], function (index, feature) {
            map.removeLayer(feature);
          });

        } else {
          property = GENERAL;
        }
        visibleFeatures[nodetype][property] = false;

      } else {
        iElement.attr('data-action', 'hide');
        iElement.removeClass('fa-eye-slash');
        iElement.addClass('fa-eye');

        if (typeof property !== 'undefined') {
          $.each(features[nodetype][property], function (index, feature) {
            map.addLayer(feature);
          });

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
