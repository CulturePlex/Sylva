// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, prompt:true, alert:true, FileReader:true, Processing:true,
sigma:true, clearTimeout */


/****************************************************************************
 * Sigma.js visualization
 ****************************************************************************/

;(function(sylva, sigma, $, window, document, undefined) {

  // The grey color.
  var grey = '#EEE';
  // Layout algorithm state.
  var isDrawing = false;
  // setTimeout id.
  var timeout_id = 0;
  // True when the "Analytics" button is clicked.
  var isAnalyticsMode = false;
  // True when the "Fullscreen" button is clicked.
  var isFullscreenByButton = false;
  // True when the nodes degrees are calculated.
  var degreesCalculated = false;
  // It saves the link in the Sylva logo when Sylva goes in "Analytics" mode.
  var linkLogo;
  // It's used when the user select a diferent edges shape than the original.
  var defaultEdgeSaved = false;

  var Sigma = {

    init: function() {

      var that = this;
      // Node info.
      var $tooltip;
      // Graph size.
      var size = sylva.size;
      // Node sizes variables.
      var minNodeSize = 1;
      var degreeMinNodeSize = 2;
      var maxNodeSize = 8;
      var analyticsMaxNodeSize = 8;
      var mediumGraphSize = 20;
      var bigGraphSize = 50;
      var defaultMultiplier = 1;
      var degreeMultiplier = 2;
      var sizeMultiplier = defaultMultiplier;
      // An array with the IDs of the visible nodes.
      var visibleNodesIds = [];
      // An array with the IDs of the visible rels.
      var visibleRelsIds = [];
      // The width and border of the analytics sidebar in analytics mode.
      var analyticsSidebarWidth = 0;
      var analyticsSidebarBorder = 2;
      // It's used for keep the last dragged analytics control on top.
      var highestZIndex = 200;
      // It's used for check if a ColorPicker for relatinships exists.
      relColorPicker = null;

      for (var key in sylva.nodetypes) {
        visibleNodesIds = visibleNodesIds.concat(sylva.nodetypes[key].nodes);
      }

      if (sylva.collapsibles == 0) {
        sylva.collapsibles = [
          'graph-node-types',
          'graph-rel-types',
          'graph-layout'
        ];

        sylva.positions['graph-node-types'] = ['15px', '15px', true];
        sylva.positions['graph-rel-types'] = ['15px', '150px', false];
        sylva.positions['graph-layout'] = ['15px', '380px', true];
      }

      // Instanciate Sigma.js and customize rendering.
      var sigInst = new sigma();
      sigInst.addRenderer({
        type: 'canvas',
        container: $('#sigma-container')[0]
      });

      var camera = sigInst.cameras[0];

      if (size >= mediumGraphSize && size < bigGraphSize) {
        maxNodeSize = 6;
      } else if (size >= bigGraphSize) {
        maxNodeSize = 4;
      }

      sigInst.settings({
        drawLabels: false,
        minNodeSize: minNodeSize,
        maxNodeSize: maxNodeSize * sizeMultiplier
      });

      sigInst.graph.read(sylva.graph);

      // Create the node legend.
      $('#graph-node-types').append('<h2 class="collapsible-header">'
        + gettext('Types') + '</h2>');
      $('#graph-node-types').append($('<ul>'));
      var list = $('#graph-node-types ul');
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(sylva.nodetypes, function(nodetypeId, nodetype) {
        list.append($('<li>')
          .css({
            minHeight: "20px",
            paddingLeft: "3px"
          })
          .append($('<i>')
            .addClass("icon-eye-open")
            .addClass("show-hide-nodes")
            .attr("data-action", "hide")
            .attr("data-nodetype-id", nodetypeId)
            .css({
              marginRight: "3px",
              width: "1em",
              height: "1em",
              cursor: "pointer",
              verticalAlign: "-2px"
            }))
          .append($('<span>')
            .addClass("change-nodes-color")
            .attr("data-color", nodetype.color)
            .attr("data-nodetype-id", nodetypeId)
            .css({
              backgroundColor: nodetype.color,
              display: "inline-block",
              width: "16px",
              height: "16px",
              marginRight: "5px",
              verticalAlign: "middle",
              cursor: "pointer"
            }))
          .append($('<span>')
            .css({
              paddingLeft: "0.3em",
              verticalAlign: "middle"
            })
            .text(nodetype.name)
          )
        );
      });

      // Create the relationship legend.
      $('#graph-rel-types').append('<h2 class="collapsible-header">'
        + gettext('Allowed relationships') + '</h2>');
      $('#graph-rel-types').append($('<ul>'));
      var list = $('#graph-rel-types ul');
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(sylva.reltypes, function(reltypeId, reltype) {
        list.append($('<li>')
          .css({
            minHeight: "20px",
            paddingLeft: "3px"
          })
          .append($('<i>')
            .addClass("icon-eye-open")
            .addClass("show-hide-rels")
            .attr("data-action", "hide")
            .attr("data-reltype-id", reltypeId)
            .css({
              marginRight: "3px",
              width: "1em",
              height: "1em",
              cursor: "pointer",
              verticalAlign: "-2px"
            }))
          .append($('<span>')
            .addClass("change-rels-color")
            .attr("data-color", reltype.color)
            .attr("data-color-mode", reltype.colorMode)
            .attr("data-reltype-id", reltypeId)
            .css({
              backgroundColor: reltype.color,
              display: "inline-block",
              width: "16px",
              height: "16px",
              marginRight: "5px",
              verticalAlign: "middle",
              cursor: "pointer"
            }))
          .append($('<span>')
            .css({
              paddingLeft: "0.3em",
              verticalAlign: "middle"
            })
            .html(reltype.htmlFullName)
          )
        );
      });

      var nodeOvered = null;
      var mouseMovedOnNode = false;
      var mouseMovedOnStage = false;
      var isOverNode = false;
      var centeredNodeForGreify = null;
      var isMouseOverCanvas = false;
      var zoomWheel = false;
      var currentNodeX = 0;
      var currentNodeY = 0;

      $('.sigma-mouse').on('mouseover', function() {
        console.log('MOUSEOVERCANVAS');
        isMouseOverCanvas = true;
      });

      $('.sigma-mouse').on('mouseout', function() {
        console.log('MOUSEOUTCANVAS');
        isMouseOverCanvas = false;
      });

      var treatZoomWheel = function(event) {
        if (zoomWheel) {
          event.preventDefault();

          var zoom = sigma.utils.getDelta(event.originalEvent) > 0;
          var pos = camera.cameraPosition(currentNodeX, currentNodeY, true);

          zooming(zoom, pos);
        }
      };

      $('#main').on('mousewheel', treatZoomWheel);

      var nodeMouseDown = function(event) {
        console.log('DOWN!');
        var dom = $('.sigma-mouse')[0];
        currentNodeX = sigma.utils.getX(event) - dom.offsetWidth / 2;
        currentNodeY = sigma.utils.getY(event) - dom.offsetHeight / 2;

        $('.sigma-mouse').off('mousedown', nodeMouseDown);
        $('#main').on('mousemove', nodeMouseMove);
        $('#main').on('mouseup', nodeMouseUp);

        sigInst.unbind('outNode', treatOutNode);

        mouseMovedOnNode = false;
        zoomWheel = true;

        $('#main').css('user-select', 'none');

        // Deactivate drag graph.
        sigInst.settings({mouseEnabled: false, enableHovering: false});
        sigInst.refresh();
      };

      var nodeMouseUp = function(event) {
        console.log('UP!');

        $('.sigma-mouse').on('mousedown', nodeMouseDown);
        $('#main').off('mousemove', nodeMouseMove);
        $('#main').off('mouseup', nodeMouseUp);

        var near = false;

        var offset = $('.sigma-mouse').offset()
        var nodeX = nodeOvered['renderer1:x'];
        var nodeY = nodeOvered['renderer1:y'];
        var x = event.pageX - offset.left;
        var y = event.pageY - offset.top;
        x = nodeX - x;
        y = nodeY - y;

        if (x >= -5 && x <= 5 && y >= -5 && y <= 5) {
          near = true;
        }

        if (!near) {
          treatOutNode();
        }
        sigInst.bind('outNode', treatOutNode);

        zoomWheel = false;

        if (mouseMovedOnNode) {
          mouseMovedOnNode = false;
        } else {
          centeredNodeForGreify = nodeOvered;
          grayfyNonNeighborhoodOnly(nodeOvered);
          if (isAnalyticsMode) {
            sylva.Utils.updateNodeLegend(nodeOvered, '#node-info');
            updateSizes();
          }
        }

        $('#main').css('user-select', 'all');

        // Activate drag graph.
        sigInst.settings({mouseEnabled: true, enableHovering: true});
        sigInst.refresh();
      };

      var nodeMouseMove = function(event) {
        console.log(nodeOvered.label + ' MOVE!');

        that.stop();

        var dom = $('.sigma-mouse')[0];
        var cos = Math.cos(camera.angle);
        var sin = Math.sin(camera.angle);

        mouseMovedOnNode = true;
        currentNodeX = sigma.utils.getX(event) - dom.offsetWidth / 2;
        currentNodeY = sigma.utils.getY(event) - dom.offsetHeight / 2;

        if (size > 1) {
          var offset = $('.sigma-mouse').offset()
          var x = event.pageX - offset.left;
          var y = event.pageY - offset.top;

          var nodes = sigInst.graph.nodes();
          var ref = [];
          for (var i = 0; i < 2; i++) {
            var n = nodes[i];
            var aux = {
              x: n.x * cos + n.y * sin,
              y: n.y * cos - n.x * sin,
              renX: n['renderer1:x'],
              renY: n['renderer1:y']
            };
            ref.push(aux);
          }

          // Applying linear interpolation.
          x = ((x - ref[0].renX) / (ref[1].renX - ref[0].renX)) *
            (ref[1].x - ref[0].x) + ref[0].x;
          y = ((y - ref[0].renY) / (ref[1].renY - ref[0].renY)) *
            (ref[1].y - ref[0].y) + ref[0].y;

          // Rotating the coordinates.
          nodeOvered.x = x * cos - y * sin;
          nodeOvered.y = y * cos + x * sin;

          sigInst.refresh();
        }
      };

      var stageMouseDown = function(event) {
        console.log('DOWN! - STAGE');

        $('.sigma-mouse').off('mousedown', stageMouseDown);
        $('.sigma-mouse').on('mousemove', stageMouseMove);
        $('.sigma-mouse').on('mouseup', stageMouseUp);

        mouseMovedOnStage = false;

        $('#main').css('user-select', 'none');

        sigInst.unbind('overNode', treatOverNode);
      };

      var stageMouseUp = function(event) {
        console.log('UP! - STAGE');

        $('.sigma-mouse').on('mousedown', stageMouseDown);
        $('.sigma-mouse').off('mousemove', stageMouseMove);
        $('.sigma-mouse').off('mouseup', stageMouseUp);

        sigInst.bind('overNode', treatOverNode);

        $('#main').css('user-select', 'all');

        if (mouseMovedOnStage) {
          mouseMovedOnStage = false;
        } else if (centeredNodeForGreify) {
          centeredNodeForGreify = null;
          ungrayfyAllNodes();
          if (isAnalyticsMode) {
            sylva.Utils.cleanNodeLegend('#node-info');
            updateSizes();
          }
        }
      };

      var stageMouseMove = function(event) {
        console.log('MOVE! - STAGE');

        mouseMovedOnStage = true;
      };

      var treatOverNode = function(event) {
        console.log('ALMOST OVERNODE!');
        if (!isOverNode) {
          console.log('OVERNODE!');

          nodeOvered = event.data.node;

          // Binding mouse node events.
          $('.sigma-mouse').on('mousedown', nodeMouseDown);

          // Unbinding stage mouse events.
          $('.sigma-mouse').off('mousedown', stageMouseDown);

          isOverNode = true;
        }
      };

      var treatOutNode = function(event) {
        console.log('ALMOST OUTNODE!');
        if (isOverNode) {
          console.log('OUTNODE!');

          // Unbinding mouse node events.
          $('.sigma-mouse').off('mousedown', nodeMouseDown);

          // Binding stage mouse events.
          $('.sigma-mouse').on('mousedown', stageMouseDown);

          isOverNode = false;
        }
      };

      sigInst.bind('overNode', treatOverNode);
      sigInst.bind('outNode', treatOutNode);

      $('.sigma-mouse').on('mousedown', stageMouseDown);

      var graphToIds = function(graph) {
        ids = {
          'nodes': [],
          'edges': []
        };

        for (var i = 0; i < graph['nodes'].length; i++) {
          ids['nodes'].push(graph['nodes'][i].id);
        }

        for (var i = 0; i < graph['edges'].length; i++) {
          ids['edges'].push(graph['edges'][i].id);
        }

        return ids;
      };

      var grayfyNonNeighborhoodOnly = function(center) {
        console.log("GRAYFING!")
        neighborhood = sigInst.graph.neighborhood(center.id);
        neighborhoodIds = graphToIds(neighborhood);

        sigInst.graph.nodes().forEach(function(n) {
          if (neighborhoodIds['nodes'].indexOf(n.id) >= 0) {
            n.color = sylva.nodetypes[n.nodetypeId].color;
          } else {
            n.color = grey;
          }
        });

        sigInst.graph.edges().forEach(function(e) {
          if (neighborhoodIds['edges'].indexOf(e.id) >= 0) {
            e.color = sylva.reltypes[e.reltypeId].color;
          } else {
            e.color = grey;
          }
        });

        // Re-draw graph.
        sigInst.refresh();
      };

      var ungrayfyAllNodes = function() {
        console.log("UNGRAYFING!")
        sigInst.graph.nodes().forEach(function(n) {
          n.color = sylva.nodetypes[n.nodetypeId].color
        });

        sigInst.graph.edges().forEach(function(e) {
          e.color = sylva.reltypes[e.reltypeId].color;
        });

        // Re-draw graph.
        sigInst.refresh();
      };

      // Bind pause button.
      $('#sigma-pause').on('click', function() {
        if (isDrawing === true) {
          that.stop();
        } else {
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          that.start(drawHidden);

          // If graph-layout isn't 'label' or FA2 set in FA2.
          var option = $('#sigma-graph-layout').find('option:selected');
          var type = option.attr('id');
          if ((type != 'label') && (type != 'force-atlas-2')) {
            option.prop('selected', false);

            option = $('#force-atlas-2');
            option.prop('selected', 'selected');
            type = option.attr('id');

            disableOptions(option, type);
            $('#sigma-graph-layout-order').hide();
          }

          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          redrawLayout(type, order, drawHidden);
        }
      });

      $('#sigma-export-image').on('mouseover', function() {
        that.stop();
      });

      // Hide/show nodes by type.
      $('.show-hide-nodes').on('click', function() {
        var nodetypeId = $(this).attr('data-nodetype-id');
        var nodesId = sylva.nodetypes[nodetypeId].nodes;
        var nodesNumber = nodesId.length;
        var action = $(this).attr('data-action');
        var hidden;

        if (action == "hide") {
          $(this).attr('data-action', 'show');
          $(this).removeClass('icon-eye-open');
          $(this).addClass('icon-eye-close');
          hidden = true;
          for(var i = 0; i < nodesId.length; i++) {
            var index = visibleNodesIds.indexOf(nodesId[i]);
            visibleNodesIds.splice(index, 1);
          }
        } else {
          $(this).attr('data-action', 'hide');
          $(this).removeClass('icon-eye-close');
          $(this).addClass('icon-eye-open');
          hidden = false;
          visibleNodesIds = visibleNodesIds.concat(nodesId);
        }

        sigInst.graph.nodes(nodesId).forEach(function(n) {
          n.hidden = hidden;
        });

        var drawHidden = $('#sigma-hidden-layout').prop('checked');
        if (drawHidden && visibleNodesIds.length > 0) {
          var type = $('#sigma-graph-layout').find('option:selected').attr('id');
          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          redrawLayout(type, order, drawHidden);
        } else {
          sigInst.refresh();
        }
      });

      // Hide/show rels by type.
      $('.show-hide-rels').on('click', function() {
        var reltypeId = $(this).attr('data-reltype-id');
        var relsId = sylva.reltypes[reltypeId].relationships;
        var relsNumber = relsId.length;
        var action = $(this).attr('data-action');
        var hidden;

        if (action == "hide") {
          $(this).attr('data-action', 'show');
          $(this).removeClass('icon-eye-open');
          $(this).addClass('icon-eye-close');
          hidden = true;
          for(var i = 0; i < relsId.length; i++) {
            var index = visibleRelsIds.indexOf(relsId[i]);
            visibleRelsIds.splice(index, 1);
          }
        } else {
          $(this).attr('data-action', 'hide');
          $(this).removeClass('icon-eye-close');
          $(this).addClass('icon-eye-open');
          hidden = false;
          visibleRelsIds = visibleRelsIds.concat(relsId);
        }

        sigInst.graph.edges(relsId).forEach(function(e) {
          e.hidden = hidden;
        });

        sigInst.refresh();
      });

      // TODO: If same color in nodes and rels don't send anything

      // Change the color of the nodes and the legend.
      var changeNodesColor = function(nodetypeId, color, span) {
        var nodesId = sylva.nodetypes[nodetypeId].nodes;
        var currentColor = $(span).css('background-color');
        currentColor = new RGBColor(currentColor).toHex().toUpperCase();
        if (currentColor != color) {
          sigInst.graph.nodes(nodesId).forEach(function(n) {
            n.color = color;
          });
          sigInst.graph.edges().forEach(function(e) {
            var colorMode = sylva.reltypes[e.reltypeId].colorMode;
            if (colorMode == 'target') {
              e.color = sigInst.graph.nodes(e.target).color;
            } else if (colorMode == 'source') {
              e.color = sigInst.graph.nodes(e.source).color;
            } else if (colorMode == 'avg') {
              var target = sigInst.graph.nodes(e.target).color;
              var source = sigInst.graph.nodes(e.source).color;
              e.color = $.xcolor.average(target, source).getHex();
            }
          });
          $(span).css({
            backgroundColor: color
          });
          sigInst.refresh();
        }
      };

      /* Change the color of the nodes and the legend when the user is
       * selecting it in the widget.
       */
      var changeNodeColorWidget = function(span, hex) {
        var nodetypeId = $(span).attr('data-nodetype-id');
        var newColor = '#' + hex;
        changeNodesColor(nodetypeId, newColor, span);
      };

      /* Restore the color of the nodes and the legend when the user click out
       * of the widget.
       */
      var hideNodeColorWidget = function(span, picker) {
        if ($(picker).is(':visible')) {
          var nodetypeId = $(span).attr('data-nodetype-id');
          var oldColor = $(span).attr('data-color');
          $(span).colpickSetColor(oldColor.substr(1));
          changeNodesColor(nodetypeId, oldColor, span);
        }
      };

      // TODO: When change nodes color, also change the edges depending of the
      // edge configuration, change the relationship color box.

      /* Change the color of the nodes and the legend and submit to server.
       * Also, restore the color if the request fails.
       */
      var submitNodeColorWidget = function(span, hex) {
        var nodetypeId = $(span).attr('data-nodetype-id');
        var newColor = '#' + hex;
        var oldColor = $(span).attr('data-color');
        changeNodesColor(nodetypeId, newColor, span);
        $(span).attr('data-color', newColor);
        sylva.nodetypes[nodetypeId].color = newColor;
        $(span).colpickHide();
        params = {
          'nodetypeId': nodetypeId,
          'color': newColor
        };
        var jqxhr = $.ajax({
          url: sylva.edit_nodetype_color_ajax_url,
          type: 'POST',
          data: params,
          dataType: 'json'
        });
        jqxhr.error(function() {
          changeNodesColor(nodetypeId, oldColor, span);
          $(span).attr('data-color', oldColor);
          sylva.nodetypes[nodetypeId].color = oldColor;
          alert(gettext("Oops! Something went wrong with the server."));
        });
      };

      // Change nodes color.
      $('.change-nodes-color').each(function(i, span) {
        var currentColor = $(span).attr('data-color');
        $(span).colpick({
          colorScheme: 'light',
          layout: 'hex',
          submitText: 'Ok',
          color: currentColor.substr(1),  // Colpick doesn't need the '#' char.
          onChange: function(hsb, hex, rgb, el, bySetColor) {
            changeNodeColorWidget(span, hex.toUpperCase());
          },
          onHide: function(picker) {
            hideNodeColorWidget(span, picker);
          },
          onSubmit: function(hsb, hex, rgb, el, bySetColor) {
            submitNodeColorWidget(span, hex.toUpperCase());
          }
        });
      });

      // var changeNodesColor = function(nodetypeId, color, span) {
      var changeRelsColor = function(reltypeId, color, span) {
        var relsId = sylva.reltypes[reltypeId].relationships;
        var currentColor = $(span).css('background-color');
        currentColor = new RGBColor(currentColor).toHex().toUpperCase();
        if (currentColor != color) {
          sigInst.graph.edges(relsId).forEach(function(e) {
            e.color = color;
          });
          $(span).css({
            backgroundColor: color
          });
          sigInst.refresh();
        }
      };

      var changeRelColorWidget = function(span, type, color) {
        var reltypeId = $(span).attr('data-reltype-id');
        var relId = sylva.reltypes[reltypeId].relationships[0];
        var rel = sigInst.graph.edges(relId);
        if (type == 'target') {
          color = sigInst.graph.nodes(rel.target).color;
        } else if (type == 'source') {
          color = sigInst.graph.nodes(rel.source).color;
        } else if (type == 'avg') {
          var target = sigInst.graph.nodes(rel.target).color;
          var source = sigInst.graph.nodes(rel.source).color;
          color = $.xcolor.average(target, source).getHex();
        } else {
          color = '#' + color;
        }
        changeRelsColor(reltypeId, color, span);
      };

      var hideRelColorWidget = function(span) {
        var reltypeId = $(span).attr('data-reltype-id');
        var oldColor = $(span).attr('data-color');
        changeRelsColor(reltypeId, oldColor, span);
      };

      var submitRelColorWidget = function(span, type) {
        var reltypeId = $(span).attr('data-reltype-id');
        var newColor = $(span).css('background-color');
        newColor = new RGBColor(newColor).toHex().toUpperCase();
        var oldColor = $(span).attr('data-color');
        var oldColorMode = $(span).attr('data-color-mode');
        changeRelsColor(reltypeId, newColor, span);
        var newColorMode = type;
        $(span).attr('data-color', newColor);
        $(span).attr('data-color-mode', newColorMode);
        sylva.reltypes[reltypeId].color = newColor;
        sylva.reltypes[reltypeId].colorMode = newColorMode;
        params = {
          'reltypeId': reltypeId,
          'color': newColor,
          'colorMode': newColorMode
        };
        var jqxhr = $.ajax({
          url: sylva.edit_reltype_color_ajax_url,
          type: 'POST',
          data: params,
          dataType: 'json'
        });
        jqxhr.error(function() {
          changeRelsColor(reltypeId, oldColor, span);
          $(span).attr('data-color', oldColor);
          $(span).attr('data-color-mode', oldColorMode);
          sylva.reltypes[reltypeId].color = oldColor;
          sylva.reltypes[reltypeId].colorMode = oldColorMode;
          alert(gettext("Oops! Something went wrong with the server."));
        });
      };

      var improveRelColorWidget = function(span, container) {
        var currentColor = $(span).css('background-color');
        currentColor = new RGBColor(currentColor).toHex().toUpperCase();
        var type = 'custom';
        container.colpick({
          showEvent: 'change',
          submit: false,
          colorScheme: 'light',
          layout: 'hex',
          submitText: 'Ok',
          color: currentColor.substr(1),  // Colpick doesn't need the '#' char.
          onChange: function(hsb, hex, rgb, el, bySetColor) {
            changeRelColorWidget(span, type, hex.toUpperCase());
          }
        });

        relColorPicker = container.next();
        container.css({
          borderBottomLeftRadius: 0,
          borderBottomRightRadius: 0
        });
        relColorPicker.css({
          borderTopLeftRadius: 0,
          borderTopRightRadius: 0
        });

        // If already existed the widget.
        container.colpickSetColor(currentColor.substr(1), false);
      };

      var restoreRelColorWidget = function(container) {
        if (relColorPicker) {
          container.css({
            borderBottomLeftRadius: '5px',
            borderBottomRightRadius: '5px'
          });
          container.colpickHide();
          relColorPicker = null;
        }
      };

      // Change rels color.
      $('.change-rels-color').each(function(i, span) {
        $(span).on('click', function(event) {
          var reltypeId = $(span).attr('data-reltype-id');
          var currentColor = $(span).attr('data-color');
          var currentColorMode = $(span).attr('data-color-mode')

          var offset = $(span).offset()
          var left = offset.left;
          var top = offset.top + $(span).height();

          var container = $('<div class="change-rels-color-float">');
          container.css({
            left: left,
            top: top
          });

          var colorModeSelect = $('<select id="rels-color-mode">');
          var optionTarget = $('<option id="target">');
          optionTarget.text(gettext('Target'));
          colorModeSelect.append(optionTarget);
          var optionSource = $('<option id="source">');
          optionSource.text(gettext('Source'));
          colorModeSelect.append(optionSource);
          var optionAvg = $('<option id="avg">');
          optionAvg.text(gettext('Average'));
          colorModeSelect.append(optionAvg);
          var optionCustom = $('<option id="custom">');
          optionCustom.text(gettext('Custom'));
          colorModeSelect.append(optionCustom);

          switch (currentColorMode) {
            case 'target':
              optionTarget.prop('disabled', 'disabled');
              optionTarget.prop('selected', 'selected');
              break;
            case 'source':
              optionSource.prop('disabled', 'disabled');
              optionSource.prop('selected', 'selected');
              break;
            case 'avg':
              optionAvg.prop('disabled', 'disabled');
              optionAvg.prop('selected', 'selected');
              break;
            case 'custom':
              optionCustom.prop('disabled', 'disabled');
              optionCustom.prop('selected', 'selected');
              break;
            default:
              break;
          }

          var button = $('<a class="link" style="width: 22px">');
          button.html('<span>Ok</span>');

          container.append(colorModeSelect);
          container.append(button);

          colorModeSelect.on('change', function(event) {
            var option = $(this).find('option:selected');
            var type = option.attr('id');

            disableOptions(option, type);

            if (type == 'custom') {
              improveRelColorWidget(span, container);
            } else {
              changeRelColorWidget(span, type, null);
              restoreRelColorWidget(container);
              event.stopPropagation()
            }

          });

          button.on('click', function() {
            var type = colorModeSelect.find('option:selected').attr('id');
            submitRelColorWidget(span, type);
            restoreRelColorWidget(container);
            container.remove();
          });

          $('body').on('mousedown', function() {
            restoreRelColorWidget(container);
            hideRelColorWidget(span);
            container.remove();
          });

          container.on('mousedown', function(event){
              event.stopPropagation();
          });

          $('body').append(container);

          if (currentColorMode == 'custom') {
            improveRelColorWidget(span, container);
            colorModeSelect.trigger('change');
          }
        });
      });

      // Save as a PNG image.
      $('#sigma-export-image').on('click', function() {
        var $canvas = $('<canvas id="sigma_export_image">');
        var width = $('#sigma-container').children().first().width();
        var height = $('#sigma-container').children().first().height();
        $canvas.attr('width', width);
        $canvas.attr('height', height);
        $('#sigma-container').append($canvas);
        var canvas = $canvas[0];
        var ctx = canvas.getContext('2d');
        ctx.globalCompositeOperation = 'source-over';
        ctx.drawImage($('.sigma-scene')[0], 0, 0);
        var img_data = canvas.toDataURL('image/png');
        $(this).attr('href', img_data.replace('image/png', 'image/octet-stream'));
        $canvas.remove();
      });

      $('#sigma-node-info').change(function () {
        if ($(this).prop('checked')) {
          sigma.canvas.hovers.def = sigma.canvas.hovers.info;
        } else {
          sigma.canvas.hovers.def = sigma.canvas.hovers.defBackup;
        }
      });

      $('#sigma-hidden-layout').change(function () {
        if (visibleNodesIds.length < size) {
          var type = $('#sigma-graph-layout').find('option:selected').attr('id');
          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          redrawLayout(type, order, drawHidden);
        }
      });

      // Go analytics mode.
      $('#sigma-go-analytics').on('click', function() {
        goAnalyticsMode();
      });

      // Exit analytics mode.
      $('#sigma-exit-analytics').on('click', function() {
        exitAnalyticsMode();
      });

      // Go fullscreen mode.
      $('#sigma-go-fullscreen').on('click', function() {
        goFullscreenMode();
      });

      // Exit fullscreen mode.
      $('#sigma-exit-fullscreen').on('click', function() {
        exitFullscreenMode();
      });

      var goFullscreenMode = function() {
        var elem = $('body')[0];
        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) {
          elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) {
          elem.webkitRequestFullscreen();
        } else if (elem.webkitRequestFullScreen) {
          elem.webkitRequestFullScreen();
        }
        $('#sigma-go-fullscreen').hide();
        $('#sigma-exit-fullscreen').show();
      };

      var exitFullscreenMode = function() {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        }
        $('#sigma-exit-fullscreen').hide();
        $('#sigma-go-fullscreen').show();
      };

      var isFullscreenMode = function() {
        return (document.fullScreenElement && document.fullScreenElement !== null)
          || (document.mozFullScreen || document.webkitIsFullScreen);
      }

      var handleFullscreenMode = function() {
        if (isFullscreenByButton) {
          isFullscreenByButton = false;
          exitFullscreenMode();
        } else {
          isFullscreenByButton = true;
          goFullscreenMode();
        }
      };

      // Listeners for handle the "fullscreen" events.
      $(document).on('fullscreenchange', handleFullscreenMode);
      $(document).on('mozfullscreenchange', handleFullscreenMode);
      $(document).on('webkitfullscreenchange', handleFullscreenMode);

      /* Update some sizes in analytics mode. This function will be called
       * when changes in the size of the screen occurr, e.g., when the user
       * open the developers tools in analytics mode.
       */
      var updateSizes = function() {
        var height = Math.max(document.documentElement.clientHeight,
          window.innerHeight || 0);
        var width = Math.max(document.documentElement.clientWidth,
          window.innerWidth || 0);
        var headerHeight =  $('div.inside.clearfix').height() + 2;
        if (analyticsSidebarWidth == 0) {
          analyticsSidebarWidth = width * 0.20;
        } else if (analyticsSidebarWidth > width * 0.33) {
          analyticsSidebarWidth = width * 0.33;
        } else if (analyticsSidebarWidth < width * 0.15) {
          analyticsSidebarWidth = width * 0.15;
        }

        $('#main').width(width);

        $('header').width(width);

        $('div.inside.clearfix').width(width);

        $('#body').height(height - headerHeight);
        $('#body').width(width);

        $('#canvas-container').width(width - analyticsSidebarWidth);

        // The new width will be: screenWidth - leftWhiteSpace - canvasInfo- rightWhiteSpace - sigmaWrapperBorder - (safeSpace between canvasInfo and canvas)
        // The new height will be: screenHeight - header - whiteSpace - graphControls - (border + padding from canvasInfo) - whiteSpace
        $('#sigma-wrapper').width(width - analyticsSidebarWidth);
        $('#sigma-wrapper').height(height - headerHeight);

        $('#analytics').width(analyticsSidebarWidth - analyticsSidebarBorder);
        $('#analytics').height(height - headerHeight);

        $('#analytics').resizable('option', 'minWidth', width * 0.15);
        $('#analytics').resizable('option', 'maxWidth', width * 0.33);

        $('#graph-controls').css({
          left: width - analyticsSidebarWidth - $('#graph-controls').width() - 20
        });

        var renderer = sigInst.renderers[0];
        var container = $(renderer.container);
        renderer.resize(container.width(), container.height());
        sigInst.refresh();
      };

      /* Update some sizes and styles in analytics mode, but only needed when
       * the analytics mode is activated.
       */
      var updateStyles = function() {
        $('header').css({
          paddingLeft: 0,
          paddingRight: 0
        });

        $('nav.menu').css({
          marginTop: '-30px'
        });

        $('#body').css({
          margin: '-14px 0 0 0',
          padding: 0
        });

        $('#sigma-wrapper').css({
          float: 'left',
          marginTop: 0
        });

        $('#canvas-container').css({
          display: 'inline'
        });

        $('#graph-node-types').css({
          position: 'absolute',
          zIndex: '100',
          border: 'none',
          padding: '10px',
          marginRight: 0,
          height: 'auto',
          width: 'auto',
          marginTop: 0,
          borderRadius: '10px',
          backgroundColor: 'rgba(214, 231, 223, 0.5)'
        });

        $('#graph-node-types ul').css({
          maxHeight: '279px',
          overflowY: 'hidden'
        });

        // TODO: Fix the 'clip/ellipsis' thing
        $('#graph-node-types ul').hover(function() {
          $('#graph-node-types ul').css({
            overflowY: 'auto'
          });
          $('#graph-node-types ul li').css({
            textOverflow: 'clip'
          });
        }, function(){
          $('#graph-node-types ul').css({
            overflowY: 'hidden'
          });
          $('#graph-node-types ul li').css({
            textOverflow: 'ellipsis'
          });
        });

        $('#graph-rel-types').css({
          position: 'absolute',
          zIndex: '101',
          border: 'none',
          padding: '10px',
          marginRight: 0,
          height: 'auto',
          width: 'auto',
          marginTop: 0,
          borderRadius: '10px',
          backgroundColor: 'rgba(214, 231, 223, 0.5)'
        });

        $('#graph-rel-types ul').css({
          maxHeight: '279px',
          overflowY: 'hidden',
        });

        $('#graph-rel-types ul').hover(function() {
          $('#graph-rel-types ul').css({
            overflowY: 'auto'
          });
          $('#graph-rel-types ul li').css({
            textOverflow: 'clip'
          });
        }, function(){
          $('#graph-rel-types ul').css({
            overflowY: 'hidden'
          });
          $('#graph-rel-types ul li').css({
            textOverflow: 'ellipsis'
          });
        });

        $('#graph-controls').css({
          position: 'absolute',
          height: 'auto',
          padding: '10px',
        });

        $('#graph-layout').css({
          position: 'absolute',
          zIndex: '102',
          border: 'none',
          overflow: 'auto',
          padding: '10px',
          marginRight: 0,
          borderRadius: '10px',
          backgroundColor: 'rgba(214, 231, 223, 0.5)'
        });

        $('.collapsible-header').css({
          cursor: 'pointer',
          display: 'inline-block'
        });

        $('.collapsible-header').each(function(i) {
          $(this).text(' ' + $(this).text());
          $(this).prepend('<span class="icon-caret-down icon-fixed-width" style="display: inline;"></span>');
        });

        $('#sigma-zoom-in').parent().css({
          marginLeft: '0'
        });
      };

      // Restore the sizes and styles when exit analytics mode.
      var restoreSizesAndStyles = function() {
        $('.collapsible-header').css({
          cursor: ''
        });

        $('.collapsible-header').each(function(i) {
          $(this).children().first().remove();
          $(this).html($(this).html().substring(1));
        });

        $('#sigma-zoom-in').parent().css({
          float: 'right',
          marginLeft: ''
        });

        $('#graph-controls').removeAttr('style');
        $('#graph-node-types').removeAttr('style');
        $('#graph-node-types ul').removeAttr('style');
        $('#sigma-wrapper').removeAttr('style');
        $('#canvas-container').removeAttr('style');
        $('#body').removeAttr('style');
        $('nav.menu').removeAttr('style');
        $('div.inside.clearfix').removeAttr('style');
        $('header').removeAttr('style');
        $('#main').removeAttr('style');

        sigInst.renderers[0].resize();
        sigInst.refresh();
      };

      var updateBoxPositions = function(key, ui) {
        var box = $('#' + key);
        var top = box.css('top');
        var left = box.css('left');

        if (ui) {
          var collapsed = false;
          if (ui.newPanel.hasOwnProperty('selector')) {
            collapsed = true;
          }
          sylva.positions[key] = [top, left, collapsed];
        } else {
          sylva.positions[key][0] = top;
          sylva.positions[key][1] = left;
        }

        var params = {
          'collapsibles': sylva.collapsibles,
          'positions': sylva.positions
        };

        var jqxhr = $.ajax({
          url: sylva.graph_analytics_boxes_edit_position,
          type: 'POST',
          data: JSON.stringify(params),
          dataType: 'json'
        });
        jqxhr.error(function() {
          alert(gettext("Oops! Something went wrong with the server."));
        });
      };

      /* Perform the 'real' analytics action. Also perform "sytle" actions
       * that can't be undone with the "restoreSizesAndStyles()" method.
       */
      var goAnalyticsMode = function() {
        isAnalyticsMode = true;

        $('#sigma-go-analytics').hide();
        $('#graph-node-info').hide();
        $('nav.main li').hide();
        $('header.global > h2').hide();
        $('div.graph-item').hide();
        $('div#footer').hide();

        $('#link-logo').on('click', false);
        $('#link-logo').addClass('disabled');
        linkLogo = $('#link-logo').attr('href');
        $('#link-logo').removeAttr('href');
        $('div.inside.clearfix').append($('nav.menu'));

        $('.analytics-mode').show();

        if ($('#sigma-node-info').is(':checked')) {
          sigma.canvas.hovers.def = sigma.canvas.hovers.defBackup;
        }

        try {
          if ($('#analytics').resizable('option', 'disabled')) {
            $('#analytics').resizable('enable');
          }
        } catch (e) {
          $('#analytics').resizable({
            ghost: true,
            handles: 'w',
            minWidth: '250',
            maxWidth: '250',
            stop: function(event, ui) {
              analyticsSidebarWidth = ui.size.width + analyticsSidebarBorder;
              updateSizes();
            }
          });
        }

        var draggableSettings = {
          containment: '#body',
          cursor: 'move',
          zIndex: 9999,
          create: function(event, ui) {
            $('#' + event.target.id).css({
              top: sylva.positions[event.target.id][0],
              left: sylva.positions[event.target.id][1]
            });
          },
          stop: function(event, ui) {
            highestZIndex++;
            $('#' + event.target.id).css({
              zIndex: highestZIndex
            });

            updateBoxPositions(event.target.id);
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

            header.removeClass('ui-accordion ui-accordion-icons ui-accordion-header ui-helper-reset');
            body.removeClass('ui-accordion ui-accordion-content ui-accordion-content');
            body.css('height', '');
            span.remove();
          },
          activate: function(event, ui) {
            var span = $(event.target).children().first().children().first();
            if (span.hasClass('icon-caret-down')) {
              span.removeClass('icon-caret-down');
              span.addClass('icon-caret-right');
              span.css({
                marginRight: '5px'
              });
            } else {
              span.removeClass('icon-caret-right');
              span.addClass('icon-caret-down');
              span.css({
                marginRight: ''
              });
            }

            updateBoxPositions(event.target.id, ui)
          }
        };

        for (var i = 0; i < sylva.collapsibles.length; i++) {
          var name = sylva.collapsibles[i];
          $('#' + name).draggable(draggableSettings);

          if (sylva.positions[name][2]) {
            $('#' + name).accordion(collapsibleSettings);
          } else {
            $('#' + name).accordion($.extend({}, collapsibleSettings, {
              active: sylva.positions[name][2]
            }));
          }
        }

        sigInst.settings({
          maxNodeSize: analyticsMaxNodeSize * sizeMultiplier
        });

        if (centeredNodeForGreify) {
          sylva.Utils.updateNodeLegend(centeredNodeForGreify, '#node-info');
          updateSizes();
        }

        updateStyles();
        updateSizes();
        $(window).on('resize', updateSizes);

        reCenter();
      };

      /* Perform the cancelation of the analytics mode. Also perform the
       * "remove" of some "sytles" that can't be done with the
       * "restoreSizesAndStyles()" method.
       */
      var exitAnalyticsMode = function() {
        isAnalyticsMode = false;

        $(window).off('resize', updateSizes);

        if (isFullscreenMode()) {
          exitFullscreenMode();
        }

        $('#sigma-go-analytics').show();
        $('#graph-node-info').show();
        $('nav.main li').show();
        $('header.global > h2').show();
        $('div.graph-item').show();
        $('div#footer').show();

        $('#link-logo').off('click');
        $('#link-logo').removeClass('disabled');
        $('#link-logo').attr('href', linkLogo);
        $('header').prepend($('nav.menu'));

        $('.analytics-mode').hide();

        if ($('#sigma-node-info').is(':checked')) {
          sigma.canvas.hovers.def = sigma.canvas.hovers.info;
        }

        sigInst.settings({
          maxNodeSize: maxNodeSize * sizeMultiplier
        });

        $('#analytics').resizable('disable');
        $('#graph-node-types').draggable('destroy');
        $('#graph-rel-types').draggable('destroy');
        $('#graph-layout').draggable('destroy');
        $('#graph-node-types').accordion('destroy');
        $('#graph-rel-types').accordion('destroy');
        $('#graph-layout').accordion('destroy');

        sylva.Utils.cleanNodeLegend('#node-info');

        restoreSizesAndStyles();
        reCenter();
      };

      var calculateNodesDegrees = function() {
        var nodes = [];
        for (var key in sylva.nodetypes) {
          nodes = nodes.concat(sylva.nodetypes[key].nodes);
        }

        var totalDegrees = sigInst.graph.degree(nodes);
        var inDegrees = sigInst.graph.degree(nodes, 'in');
        var outDegrees = sigInst.graph.degree(nodes, 'out');

        sigInst.graph.nodes().forEach(function(n) {
          var index = nodes.indexOf(n.id);
          n.defaultSize = 1;
          n.totalDegree = totalDegrees[index];
          n.inDegree = inDegrees[index];
          n.outDegree = outDegrees[index];
        });
      };

      var gridLayout = function(sortFunc, drawHidden) {
        if (!degreesCalculated) {
          calculateNodesDegrees();
        }

        var nodes = [];
        if (drawHidden) {
          nodes = visibleNodesIds;
        } else {
          for (var key in sylva.nodetypes) {
            nodes = nodes.concat(sylva.nodetypes[key].nodes);
          }
        }

        var sorted = sigInst.graph.nodes(nodes);
        if (sortFunc) {
          sorted.sort(sortFunc);
        }

        var side = Math.ceil(Math.sqrt(sorted.length));

        sorted.forEach(function(n, i) {
          if (!(n.hidden && drawHidden)) {
            n.gridX = 100 * (i % side);
            n.gridY = 100 * Math.floor(i / side);
          }
        });
      };

      var circularLayout = function(sortFunc, drawHidden) {
        var i = 0;
        var number = size;
        if (drawHidden) {
          number = visibleNodesIds.length;
        }

        var sorted = sigInst.graph.nodes();
        if (sortFunc) {
          sorted.sort(sortFunc);
        }

        sorted.forEach(function(n) {
          if (!(n.hidden && drawHidden)) {
            var angle = Math.PI * 2 * i / number - Math.PI / 2;
            n.circularX = Math.cos(angle);
            n.circularY = Math.sin(angle);
            i++;
          }
        });
      };

      var disableOptions = function(option, type) {
        var parentId = option.parent().attr('id');
        option.prop('disabled', 'disabled');
        $('#' + parentId + ' option').each(function() {
          var id = $(this).attr('id');
          if ((id != 'label') && (id != type)) {
            $(this).prop('disabled', false);
          }
        });
      };

      // Control graph layout.
      $('#sigma-graph-layout').change(function() {
        var option = $(this).find('option:selected');
        var type = option.attr('id');

        disableOptions(option, type);

        if (type != 'label') {
          if (type != 'force-atlas-2') {
            $('#sigma-graph-layout-order').show();
          } else {
            $('#sigma-graph-layout-order').hide();
          }

          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          redrawLayout(type, order, drawHidden);
        }
      });

      var redrawLayout = function(type, order, drawHidden) {
        var xPos = '';
        var yPos = '';

        switch (type) {
          case 'label':
          case 'force-atlas-2':
            if (visibleNodesIds.length == 0) {
              return;
            }
            that.stop();
            that.start(drawHidden);
            that.addTimeout(timeout);
            return;
            break;
          case 'grid':
            that.stop();
            var sortFunc = layoutSort(order);
            gridLayout(sortFunc, drawHidden);
            xPos = 'gridX';
            yPos = 'gridY';
            break;
          case 'circular':
            that.stop();
            var sortFunc = layoutSort(order);
            circularLayout(sortFunc, drawHidden);
            xPos = 'circularX';
            yPos = 'circularY';
            break;
          default:
            break;
        }

        sigma.plugins.animate(sigInst, {x: xPos, y: yPos}, {duration: 500});
      };

      var layoutSort = function(order) {
        switch (order) {
          case 'label':
          case 'def':
            return null;
            break;
          case 'tdd':
            return function(a, b) {
              return b.totalDegree - a.totalDegree;
            };
            break;
          case 'tda':
            return function(a, b) {
              return a.totalDegree - b.totalDegree;
            };
            break;
          case 'idd':
            return function(a, b) {
              return b.inDegree - a.inDegree;
            };
            break;
          case 'ida':
            return function(a, b) {
              return a.inDegree - b.inDegree;
            };
            break;
          case 'odd':
            return function(a, b) {
              return b.outDegree - a.outDegree;
            };
            break;
          case 'oda':
            return function(a, b) {
              return a.outDegree - b.outDegree;
            };
            break;
          default:
            break;
          }
      };

      $('#sigma-graph-layout-order').change(function() {
        var option = $(this).find('option:selected');
        var order = option.attr('id');

        disableOptions(option, order);

        var layoutType = $('#sigma-graph-layout').find('option:selected').attr('id');
        var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
        var drawHidden = $('#sigma-hidden-layout').prop('checked');
        redrawLayout(layoutType, order, drawHidden);
      });

      // Control node size.
      var nodeSizeSelect = $('#sigma-node-size');
      nodeSizeSelect.change(function() {
        var option = $(this).find('option:selected');
        var type = option.attr('id');

        disableOptions(option, type);

        if (!degreesCalculated) {
          calculateNodesDegrees();
        }

        var animationSize = '';

        var auxMinNodeSize = sigInst.settings('minNodeSize');
        var auxMaxNodeSize = sigInst.settings('maxNodeSize') / sizeMultiplier;
        switch (type) {
          case 'label':
            break;
          case 'same':
            animationSize = 'defaultSize';
            sizeMultiplier = defaultMultiplier;
            break;
          case 'total-degree':
            animationSize = 'totalDegree';
            auxMinNodeSize = degreeMinNodeSize;
            sizeMultiplier = degreeMultiplier;
            break;
          case 'in-degree':
            animationSize = 'inDegree';
            auxMinNodeSize = degreeMinNodeSize;
            sizeMultiplier = degreeMultiplier;
            break;
          case 'out-degree':
            animationSize = 'outDegree';
            auxMinNodeSize = degreeMinNodeSize;
            sizeMultiplier = degreeMultiplier;
            break;
          default:
            break;
        }
        sigInst.settings({
          minNodeSize: auxMinNodeSize,
          maxNodeSize: auxMaxNodeSize * sizeMultiplier
        });
        sigInst.refresh();
        sigma.plugins.animate(sigInst, {size: animationSize}, {duration: 500});
      });

      // Control edges shape.
      $('#sigma-edge-shape').change(function() {
        var option = $(this).find('option:selected');
        var type = option.attr('id');

        disableOptions(option, type);

        switch (type) {
          case 'label':
            break;
          case 'straight':
            if (defaultEdgeSaved) {
              sigma.canvas.edges.def = sigma.canvas.edges.defBackup;
            } else {
              return;
            }
            break;
          case 'arrow':
            if (!defaultEdgeSaved) {
              sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
              defaultEdgeSaved = true;
            }
            sigma.canvas.edges.def = sigma.canvas.edges.arrow;
            break;
          case 'curve':
            if (!defaultEdgeSaved) {
              sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
              defaultEdgeSaved = true;
            }
            sigma.canvas.edges.def = sigma.canvas.edges.curve;
            break;
          case 'curved-arrow':
            if (!defaultEdgeSaved) {
              sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
              defaultEdgeSaved = true;
            }
            sigma.canvas.edges.def = sigma.canvas.edges.curvedArrow;
            break;
          default:
            break;
        }
        sigInst.refresh();
      });

      var zooming = function(zoomIn, position) {
        var _settings = sigInst.settings;
        var _target = $('#sigma-container');

        var pos,
          count,
          ratio,
          newRatio;

        ratio = zoomIn ?
          1 / _settings('zoomingRatio') :
          _settings('zoomingRatio');

        // Deal with min / max:
        newRatio = Math.max(
          _settings('zoomMin'),
          Math.min(
            _settings('zoomMax'),
            camera.ratio * ratio
          )
        );
        ratio = newRatio / camera.ratio;

        // Check that the new ratio is different from the initial one:
        if (newRatio !== camera.ratio) {
          count = sigma.misc.animation.killAll(camera);

          sigma.misc.animation.camera(
            camera,
            {
              x: position.x * (1 - ratio) + camera.x,
              y: position.y * (1 - ratio) + camera.y,
              ratio: newRatio
            },
            {
              easing: count ? 'quadraticOut' : 'quadraticInOut',
              duration: _settings('mouseZoomDuration')
            }
          );
        }

      };

      $('#sigma-zoom-in').on('click', function(event) {
        zooming(true, {x: 0, y: 0});
      });

      $('#sigma-zoom-out').on('click', function(event) {
        zooming(false, {x: 0, y: 0});
      });

      $('#sigma-zoom-home').on('click', function(event) {
        reCenter();
      });

      var reCenter = function() {
        var count = sigma.misc.animation.killAll(camera);

        sigma.misc.animation.camera(
          camera,
          {
            x: 0,
            y: 0,
            ratio: 1
          },
          {
            easing: count ? 'quadraticOut' : 'quadraticInOut',
            duration: sigInst.settings('mouseZoomDuration')
          });
      };

      sigInst.startForceAtlas2();
      isDrawing = true;

      var timeout;
      if (size <= 20) {
        timeout = 10000;
      } else if (size <= 50) {
        timeout = 15000;
      } else if (size <= 100) {
        timeout = 20000;
      } else {
        timeout = 30000;
      }
      that.addTimeout(timeout);

      sigInst.refresh();
    },

    // Start layout algorithm.
    start: function(drawHidden) {
      var sigInst = sigma.instances(0);
      if (sigInst) {
        sigInst.startForceAtlas2(drawHidden);
      } else {
        Sigma.init();
      }
      isDrawing = true;
      $('#sigma-pause').removeClass('icon-play');
      $('#sigma-pause').addClass('icon-pause');

      // TODO: Watch if this is the right place for the next line.
      sigma.canvas.hovers.defBackup = sigma.canvas.hovers.def;
    },

    // Stop layout algorithm.
    stop: function() {
      this.removeTimeout();
      var sigInst = sigma.instances(0);
      if (sigInst) {
        sigInst.stopForceAtlas2();
        isDrawing = false;
        $('#sigma-pause').removeClass('icon-pause');
        $('#sigma-pause').addClass('icon-play');
      }
    },

    // Stop layout algorithm after `timeout` ms.
    addTimeout: function(timeout) {
      var that = this;
      timeout_id = setTimeout(function() {
        that.stop();
      }, timeout);
    },

    // Clear setTimeout.
    removeTimeout: function() {
      clearTimeout(timeout_id);
    }

  };

  // Reveal module.
  window.sylva.Sigma = Sigma;

})(sylva, sigma, jQuery, window, document);
