// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, prompt:true, alert:true, FileReader:true, Processing:true,
sigma:true, clearTimeout */


/****************************************************************************
 * Sigma.js visualization
 ****************************************************************************/

;(function(sylva, sigma, $, window, document, undefined) {

  // The that variable, substituion of this.
  var that = null;
  // The sigma instance and its camera.
  var sigInst = null;
  var camera = null;
  // It saves the link in the Sylva logo when Sylva goes in "Analytics" mode.
  var linkLogo = null;
  // The size of the graphs in nodes.
  var size = 0;
  // Timeout for stop layout algorithm.
  var timeout = 0;
  // setTimeout id.
  var timeout_id = 0;
  // Arrays with the IDs of the visible elments.
  var visibleNodeIds = [];
  var visibleRelIds = [];
  // It's used for check if a ColorPicker for relatinships exists.
  var relColorPicker = null;
  // A variable for containing the Tool object of Paper.js.
  var paperTool = null;
  // Layout algorithm state.
  var isDrawing = false;
  // True when the "Analytics" button is clicked.
  var isAnalyticsMode = false;
  // True when the "Fullscreen" button is clicked.
  var isFullscreenByButton = false;
  // True when the nodes degrees are calculated.
  var degreesCalculated = false;
  // It's used when the user select a diferent edge shape than the original.
  var defaultEdgeShapeSaved = false;
  // It saves the selected state of a node when is edited in the modal form.
  var wasDeletedNodeSelected = false;
  // The gray color.
  var gray = '#EEE';
  // It's used for keep the last dragged analytics control on top.
  var highestZIndex = 102;
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
  // For some animations we need the same time that the 'fast' jQuery, 200ms.
  var fast = 200;
  // The width and border of the analytics sidebar in analytics mode.
  var analyticsSidebarWidth = 0;
  var analyticsSidebarBorder = 0;
  // Variables for treat Sigma events, like for drag&drop feature and more.
  var nodeOvered = null;
  var mouseMovedOnNode = false;
  var mouseMovedOnStage = false;
  var nodeInfoShowed = false;
  var isMouseOverCanvas = false;
  var isZoomWheelPossible = false;
  var colorWidgetOpened = false;
  var selectedSelectingTool = '';
  var canSaveBoxes = true;
  var currentNodeX = 0;
  var currentNodeY = 0;

  var Sigma = {

    init: function() {

      that = this;
      sylva.selectedNodes = sylva.nodeIds;
      size = sylva.size;

      // Creating visible elements arrays.
      for (var key in sylva.nodetypes) {
        visibleNodeIds = visibleNodeIds.concat(sylva.nodetypes[key].nodes);
      }
      for (var key in sylva.reltypes) {
        visibleRelIds = visibleRelIds.concat(
          sylva.reltypes[key].relationships);
      }

      /* If there is no info about collapsible/draggable elements in server,
       * the client will do it.
       */
      if (sylva.collapsibles.length == 0) {
        that.createCollapsiblesStructures();
      }

      sigInst = new sigma();
      sigInst.addRenderer({
        type: 'canvas',
        container: $('#sigma-container')[0]
      });
      camera = sigInst.cameras[0];

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

      that.createLegend('node', sylva.nodetypes, 'Types', 'name');
      that.createLegend('rel', sylva.reltypes, 'Allowed relationships',
        'htmlFullName');

      /* The edges need to be colored if they colorMode attribute isn't custom
       * and their color attribut isn't their real color.
       */
      that.coloringEdges();


      /* *****
       * Main mouse events.
       ***** */

      $('.sigma-mouse').on('mouseover', function() {
        isMouseOverCanvas = true;
      });

      $('.sigma-mouse').on('mouseout', function() {
        isMouseOverCanvas = false;
      });

      $('#main').on('mousewheel', that.treatZoomWheel);

      sigInst.bind('overNode', that.treatOverNode);
      sigInst.bind('outNode', that.treatOutNode);

      $('.sigma-mouse').on('mousedown', that.stageMouseDown);


      /* *****
       * Analytics mode events.
       ***** */

      $('#sigma-go-analytics').on('click', function() {
        that.goAnalyticsMode();
      });

      $('#sigma-exit-analytics').on('click', function() {
        that.exitAnalyticsMode();
      });

      $('#sigma-go-fullscreen').on('click', function() {
        that.goFullscreenMode();
      });

      $('#sigma-exit-fullscreen').on('click', function() {
        that.exitFullscreenMode();
      });

      $(document).on('fullscreenchange', that.handleFullscreenMode);
      $(document).on('mozfullscreenchange', that.handleFullscreenMode);
      $(document).on('webkitfullscreenchange', that.handleFullscreenMode);


      /* *****
       * Buttons and and other features events.
       ***** */

      $('#sigma-pause').on('click', that.clickOnPause);

      $('#sigma-export-image').on('mouseover', that.stop);

      $('.show-hide-nodes').on('click', that.showHideNodes);

      $('.show-hide-rels').on('click', that.showHideRels);

      $('.change-nodes-color').each(that.setNodesColorWidget);

      $('.change-rels-color').each(that.setRelsColorWidget);
      // Save as a PNG image.
      $('#sigma-export-image').on('click', that.exportImage);

      // Show node info in 'Not analytics mode'.
      $('#sigma-node-info').change(function () {
        if ($(this).prop('checked')) {
          sigma.canvas.hovers.def = sigma.canvas.hovers.info;
        } else {
          sigma.canvas.hovers.def = sigma.canvas.hovers.defBackup;
        }
      });

      // Draw the layout considering the hidden nodes or not.
      $('#sigma-hidden-layout').change(function () {
        if (visibleNodeIds.length < size) {
          var type = $('#sigma-graph-layout').find('option:selected').attr('id');
          var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          that.redrawLayout(type, degreeOrder, order, drawHidden);
        }
      });

      $('#sigma-graph-layout').change(that.controlGraphLayout);

      $('#sigma-graph-layout-degree-order').change(that.controlGraphLayoutDegreeOrder);

      $('#sigma-graph-layout-order').change(that.controlGraphLayoutOrder);

      $('#sigma-node-size').change(that.controlNodeSize);

      $('#sigma-edge-shape').change(that.controlEdgeShape);

      $('#sigma-zoom-in').on('click', function(event) {
        that.zooming(true, {x: 0, y: 0});
      });

      $('#sigma-zoom-out').on('click', function(event) {
        that.zooming(false, {x: 0, y: 0});
      });

      $('#sigma-zoom-home').on('click', function(event) {
        that.reCenter();
      });

      // Selecting tool.
      $('#sigma-filter-rectangle').on('click', function() {
        that.enableDisableSelectingTool('rectangle');
      });

      $('#sigma-filter-free-hand').on('click', function() {
        that.enableDisableSelectingTool('freeHand');
      });

      $('#sigma-filter-neighbors').on('click', function() {
        that.enableDisableSelectingTool('neighbors');
      });

      $('#sigma-filter-click').on('click', function() {
        that.enableDisableSelectingTool('click');
      });

      sigInst.startForceAtlas2();
      isDrawing = true;

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

      sigma.canvas.hovers.defBackup = sigma.canvas.hovers.def;
      sigInst.refresh();
    },


    /* *****
     * Functions for control the sigma instance.
     ***** */

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
    },

    // Stop layout algorithm.
    stop: function() {
      that.removeTimeout();
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
      timeout_id = setTimeout(function() {
        that.stop();
      }, timeout);
    },

    // Clear setTimeout.
    removeTimeout: function() {
      clearTimeout(timeout_id);
    },


    /* *****
     * Functions for show information.
     ***** */

    // Create the legend for nodes and relationships.
    createLegend: function(kind, types, header, label) {
      $('#graph-' + kind + '-types').append('<h2 class="collapsible-header">'
        + gettext(header) + '</h2>');
      $('#graph-' + kind + '-types').append($('<ul>'));
      var list = $('#graph-' + kind + '-types ul');
      list.css({
        listStyleType: 'none',
        marginTop: '5px'
      });
      $.each(types, function(typeId, type) {
        if (kind == 'rel') {
          type[label] = type.sourceName +
                    ' <span style="font-style: italic;">' +
                    type.name + '</span> ' + type.targetName
        }

        list.append($('<li>')
          .css({
            minHeight: '20px',
            paddingLeft: '3px'
          })
          .append($('<i>')
            .addClass('icon-eye-open')
            .addClass('show-hide-' + kind + 's')
            .attr('data-action', 'hide')
            .attr('data-' + kind + 'type-id', typeId)
            .css({
              marginRight: '3px',
              width: '1em',
              height: '1em',
              cursor: 'pointer',
              verticalAlign: '-2px'
            }))
          .append($('<span>')
            .addClass('change-' + kind + 's-color')
            .attr('data-color', type.color)
            .attr('data-color-mode', type.colorMode)
            .attr('data-' + kind + 'type-id', typeId)
            .css({
              backgroundColor: type.color,
              display: 'inline-block',
              width: '16px',
              height: '16px',
              marginRight: '5px',
              verticalAlign: 'middle',
              cursor: 'pointer'
            }))
          .append($('<span>')
            .css({
              paddingLeft: '0.3em',
              verticalAlign: 'middle'
            })
            .html(type[label])
          )
        );
      });
    },

    // Update node legend frame.
    updateNodeInfo: function(node, selector) {
      if (nodeInfoShowed) {
        that.cleanNodeInfo(selector);
      }
      nodeInfoShowed = true;
      var nodeEditURL = sylva.nodeEditURL.replace(/nodes\/0\/edit/, 'nodes/' + node.id + '/edit');
      var nodeViewURL = sylva.nodeViewURL.replace(/nodes\/0\/view/, 'nodes/' + node.id + '/view');
      var title = (node.label.length < 22) ? node.label : node.label.substring(0, 16) + "...";
      var properties = '';

      for (var key in node.properties) {
        var property = (node.properties[key].length < 22) ? node.properties[key] : node.properties[key].substring(0, 30) + "...";
        properties = properties + '<span style="font-style: italic;">' + key + '</span>: ' + property + '<br>';
      }

      $(selector).html(
        '<h2 style="padding-top: 40px;" title="' + node.label + '" style="font-size: 18px;">' + title + '</h2>' +
        properties +
        '<a href="' + nodeViewURL + '">' +
          '<i style="margin-top: 5px; "class="sylva-icon-nodes16"></i> ' + gettext('View node data') +
        '</a>' +
        '<br>' +
        '<a id="edit-node-modal-link" data-url="' + nodeEditURL + '">' +
          '<i class="sylva-icon-edit-node16"></i> ' + gettext('Edit node data') +
        '</a>'
      );

      $('#edit-node-modal-link').on('click', that.prepareEditNodeModal);
    },

    // Clean node legend frame.
    cleanNodeInfo: function(selector) {
      nodeInfoShowed = false;
      $('#edit-node-modal-link').off('click', that.prepareEditNodeModal);
      $(selector).html('');
    },


    /* *****
     * Functions for interact with the graph representation.
     ***** */

    /* It performs zoom with the wheel mouse when the mouse events are
     * disabled.
     */
    treatZoomWheel: function(event) {
      if (isZoomWheelPossible) {
        event.preventDefault();

        var zoom = sigma.utils.getDelta(event.originalEvent) > 0;
        var pos = camera.cameraPosition(currentNodeX, currentNodeY, true);

        that.zooming(zoom, pos);
      }
    },

    nodeMouseDown: function(event) {
      $('#main').css('user-select', 'none');

      // This is for treating the select node by click feature
      if (selectedSelectingTool == 'click' || selectedSelectingTool == 'neighbors') {
        $('#main').on('mouseup', that.nodeMouseUp);
        sigInst.unbind('outNode', that.treatOutNode);

      } else {
        var dom = $('.sigma-mouse')[0];
        currentNodeX = sigma.utils.getX(event) - dom.offsetWidth / 2;
        currentNodeY = sigma.utils.getY(event) - dom.offsetHeight / 2;

        $('.sigma-mouse').off('mousedown', that.nodeMouseDown);
        $('#main').on('mousemove', that.nodeMouseMove);
        $('#main').on('mouseup', that.nodeMouseUp);

        sigInst.unbind('outNode', that.treatOutNode);

        mouseMovedOnNode = false;
        isZoomWheelPossible = true;

        // Deactivate drag graph.
        that.setUsualSigmaSettings(false, false);
      }

    },

    nodeMouseUp: function(event) {
      // Activate drag graph if it was desactivated.
      that.setUsualSigmaSettings(true, true);

      $('#main').css('user-select', 'all');

      var offset = $('.sigma-mouse').offset()
      var nodeX = nodeOvered['renderer1:x'];
      var nodeY = nodeOvered['renderer1:y'];
      var x = event.pageX - offset.left;
      var y = event.pageY - offset.top;
      x = nodeX - x;
      y = nodeY - y;

      sigInst.bind('outNode', that.treatOutNode);
      $('#main').off('mouseup', that.nodeMouseUp);

      // This is for treating the select node by click feature.
      if (selectedSelectingTool == 'click') {
        that.selectDeselectNode(nodeOvered);

      } else if(selectedSelectingTool == 'neighbors') {
        neighborhoodIds = that.obtaingNeighborhood(nodeOvered);
        sylva.selectedNodes = neighborhoodIds['nodes'];
        that.grayfyNonListedNodes(sylva.selectedNodes, neighborhoodIds['edges']);
        that.enableDisableSelectingTool('neighbors');

      } else {
        $('.sigma-mouse').on('mousedown', that.nodeMouseDown);
        $('#main').off('mousemove', that.nodeMouseMove);

        isZoomWheelPossible = false;

        if (mouseMovedOnNode) {
          mouseMovedOnNode = false;
        } else {
          if (isAnalyticsMode) {
            that.updateNodeInfo(nodeOvered, '#node-info');
            that.updateSizes(true);
          }
        }
      }
    },

    nodeMouseMove: function(event) {
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
    },

    stageMouseDown: function(event) {
      $('#main').css('user-select', 'none');

      if (selectedSelectingTool != 'click' && selectedSelectingTool != 'neighbors') {
        $('.sigma-mouse').off('mousedown', that.stageMouseDown);
        $('.sigma-mouse').on('mousemove', that.stageMouseMove);
        $('.sigma-mouse').on('mouseup', that.stageMouseUp);

        mouseMovedOnStage = false;

        sigInst.unbind('overNode', that.treatOverNode);
      }
    },

    stageMouseUp: function(event) {
      $('.sigma-mouse').on('mousedown', that.stageMouseDown);
      $('.sigma-mouse').off('mousemove', that.stageMouseMove);
      $('.sigma-mouse').off('mouseup', that.stageMouseUp);

      sigInst.bind('overNode', that.treatOverNode);
      $('#main').css('user-select', 'all');
      if (mouseMovedOnStage) {
        mouseMovedOnStage = false;
      } else if (colorWidgetOpened) {
        colorWidgetOpened = false;
      } else if (nodeInfoShowed && isAnalyticsMode) {
          that.cleanNodeInfo('#node-info');
          that.updateSizes(true);
      } else if (sylva.selectedNodes.length < size) {
        that.ungrayfyAllNodes();
      }
    },

    stageMouseMove: function(event) {
      mouseMovedOnStage = true;
    },

    treatOverNode: function(event) {
      if (!nodeOvered) {
        nodeOvered = event.data.node;

        // Binding mouse node events.
        $('.sigma-mouse').on('mousedown', that.nodeMouseDown);

        // Unbinding stage mouse events.
        $('.sigma-mouse').off('mousedown', that.stageMouseDown);
      }
    },

    treatOutNode: function(event) {
      if (nodeOvered) {
        // Unbinding mouse node events.
        $('.sigma-mouse').off('mousedown', that.nodeMouseDown);

        // Binding stage mouse events.
        $('.sigma-mouse').on('mousedown', that.stageMouseDown);

        nodeOvered = null;
      }
    },


    /* *****
     * Functions for control the colors of the graph.
     ***** */

    /* It will grayfy all the given nodes. If you also pass a list
     * relationships it will take the rels from there, if not, it will calcule
     * it.
     */
    grayfyNonListedNodes: function(nodeList, relList) {
      sigInst.graph.nodes().forEach(function(n) {
        if (nodeList.indexOf(n.id) >= 0) {
          n.color = sylva.nodetypes[n.nodetypeId].color;
        } else {
          n.color = gray;
          n.type = 'gray';
        }
      });

      if (relList != null) {
        sigInst.graph.edges().forEach(function(e) {
          if (relList.indexOf(e.id) >= 0) {
            e.color = sylva.reltypes[e.reltypeId].color;
          } else {
            e.color = gray;
            e.type = 'gray';
          }
        });

      } else {
        sigInst.graph.edges().forEach(function(e) {
          if (nodeList.indexOf(e.source) >= 0 && nodeList.indexOf(e.target) >= 0) {
            e.color = sylva.reltypes[e.reltypeId].color;
            delete e['type'];
          } else {
            e.color = gray;
            e.type = 'gray';
          }
        });
      }

      // Re-draw graph.
      sigInst.refresh();
    },

    ungrayfyAllNodes: function() {
      sigInst.graph.nodes().forEach(function(n) {
        n.color = sylva.nodetypes[n.nodetypeId].color
        delete n['type'];
      });

      sigInst.graph.edges().forEach(function(e) {
        e.color = sylva.reltypes[e.reltypeId].color;
        delete e['type'];
      });

      // Re-draw graph.
      sigInst.refresh();
    },

    // Change the color of the nodes, the rels (it it's needed) and the legend.
    changeNodesColor: function(nodetypeId, color, span) {
      var nodesId = sylva.nodetypes[nodetypeId].nodes;
      var currentColor = $(span).css('background-color');
      currentColor = new RGBColor(currentColor).toHex().toUpperCase();
      if (currentColor != color) {
        sigInst.graph.nodes(nodesId).forEach(function(n) {
          if (n.type && n.type == 'gray') {
            n.colorBackup = color;
          } else {
            n.color = color;
          }
        });
        $(span).css({
          backgroundColor: color
        });

        that.coloringEdges();
        sigInst.refresh();
      }
    },

    /* Change the color of the nodes and the legend when the user is
     * selecting it in the widget.
     */
    changeNodeColorWidget: function(span, hex) {
      var nodetypeId = $(span).attr('data-nodetype-id');
      var newColor = '#' + hex;
      that.changeNodesColor(nodetypeId, newColor, span);
    },

    /* Restore the color of the nodes and the legend when the user click out
     * of the widget.
     */
    hideNodeColorWidget: function(span, picker) {
      if ($(picker).is(':visible')) {
        var nodetypeId = $(span).attr('data-nodetype-id');
        var oldColor = $(span).attr('data-color');
        $(span).colpickSetColor(oldColor.substr(1));
        that.changeNodesColor(nodetypeId, oldColor, span);

        setTimeout(function() {
          colorWidgetOpened = false;
        }, 300);
      }
    },

    /* Change the color of the nodes and the legend and submit to server.
     * Also, restore the color if the request fails.
     */
    submitNodeColorWidget: function(span, hex) {
      var nodetypeId = $(span).attr('data-nodetype-id');
      var newColor = '#' + hex;
      var oldColor = $(span).attr('data-color');
      $(span).colpickHide();
      if (newColor != oldColor) {
        that.changeNodesColor(nodetypeId, newColor, span);
        $(span).attr('data-color', newColor);
        sylva.nodetypes[nodetypeId].color = newColor;
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
          that.changeNodesColor(nodetypeId, oldColor, span);
          $(span).attr('data-color', oldColor);
          sylva.nodetypes[nodetypeId].color = oldColor;
          alert(gettext("Oops! Something went wrong with the server."));
        });
      }

      colorWidgetOpened = false;
    },

    // Change the color of the rels and the legend.
    changeRelsColor: function(reltypeId, color, span) {
      var relsId = sylva.reltypes[reltypeId].relationships;
      var currentColor = $(span).css('background-color');
      currentColor = new RGBColor(currentColor).toHex().toUpperCase();
      if (currentColor != color) {
        sigInst.graph.edges(relsId).forEach(function(e) {
          if (e.type && e.type == 'gray') {
            e.colorBackup = color;
          } else {
            e.color = color;
          }
        });
        $(span).css({
          backgroundColor: color
        });
        sigInst.refresh();
      }
    },

    /* Change the color of the rels and the legend when the user is
     * selecting it in the widget.
     */
    changeRelColorWidget: function(span, type, color) {
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
      that.changeRelsColor(reltypeId, color, span);
    },

    /* Restore the color of the rels and the legend when the user click out
     * of the widget.
     */
    hideRelColorWidget: function(span) {
      var reltypeId = $(span).attr('data-reltype-id');
      var oldColor = $(span).attr('data-color');
      that.changeRelsColor(reltypeId, oldColor, span);

      setTimeout(function() {
        colorWidgetOpened = false;
      }, 300);
    },

    /* Change the color of the nodes and the legend and submit to server.
     * Also, restore the color if the request fails.
     */
    submitRelColorWidget: function(span, type) {
      var reltypeId = $(span).attr('data-reltype-id');
      var newColor = $(span).css('background-color');
      newColor = new RGBColor(newColor).toHex().toUpperCase();
      var newColorMode = type;
      var oldColor = $(span).attr('data-color');
      var oldColorMode = $(span).attr('data-color-mode');
      if (newColor != newColor || newColorMode != oldColorMode) {
        that.changeRelsColor(reltypeId, newColor, span);
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
          that.changeRelsColor(reltypeId, oldColor, span);
          $(span).attr('data-color', oldColor);
          $(span).attr('data-color-mode', oldColorMode);
          sylva.reltypes[reltypeId].color = oldColor;
          sylva.reltypes[reltypeId].colorMode = oldColorMode;
          alert(gettext("Oops! Something went wrong with the server."));
        });
      }

      colorWidgetOpened = false;
    },

    // Add the 'colorPicker' widget to the 'selectColor' widget of the rels.
    improveRelColorWidget: function(span, container) {
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
          that.changeRelColorWidget(span, type, hex.toUpperCase());
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
    },

    // Remove the 'colorPicker' widget to the 'selectColor' widget of the rels.
    restoreRelColorWidget: function(container) {
      if (relColorPicker) {
        container.css({
          borderBottomLeftRadius: '5px',
          borderBottomRightRadius: '5px'
        });
        container.colpickHide();
        relColorPicker = null;
      }
    },

    coloringEdges: function() {
      sigInst.graph.edges().forEach(function(e) {
        var colorMode = sylva.reltypes[e.reltypeId].colorMode;
        var spanRel = $('span.change-rels-color[data-reltype-id='
          + e.reltypeId + ']');
        var relColor = '';
        if (colorMode == 'target') {
          relColor = sigInst.graph.nodes(e.target).color;
        } else if (colorMode == 'source') {
          relColor = sigInst.graph.nodes(e.source).color;
        } else if (colorMode == 'avg') {
          var target = sigInst.graph.nodes(e.target).color;
          var source = sigInst.graph.nodes(e.source).color;
          relColor = $.xcolor.average(target, source).getHex();
        }
        if (e.type && e.type == 'gray') {
          e.colorBackup = relColor;
        } else {
          e.color = relColor;
        }
        spanRel.css({
          backgroundColor: relColor
        });
        spanRel.attr('data-color', relColor);
      });
    },


    /* *****
     * Functions for control the Analytics and Fullscreen mode.
     ***** */

    goFullscreenMode: function() {
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
    },

    exitFullscreenMode: function() {
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
    },

    isFullscreenMode: function() {
      return (document.fullScreenElement && document.fullScreenElement !== null)
        || (document.mozFullScreen || document.webkitIsFullScreen);
    },

    handleFullscreenMode: function() {
      if (isFullscreenByButton) {
        isFullscreenByButton = false;
        that.exitFullscreenMode();
      } else {
        isFullscreenByButton = true;
        that.goFullscreenMode();
      }
    },

    /* Update some sizes in analytics mode. This function will be called
     * when changes in the size of the screen occurr, e.g., when the user
     * open the developers tools in analytics mode.
     * The parameter is used when you don't want that this function to
     * update the position of the floating boxes.
     */
    updateSizes: function(noUpdateBoxesPositions) {
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

      $('#sigma-wrapper').width(width - analyticsSidebarWidth);
      $('#sigma-wrapper').height(height - headerHeight);

      $('#analytics').width(analyticsSidebarWidth - analyticsSidebarBorder);
      $('#analytics').height(height - headerHeight);

      $('#analytics').resizable('option', 'minWidth', width * 0.15);
      $('#analytics').resizable('option', 'maxWidth', width * 0.33);

      $('#graph-controls-and-info').css({
        left: width - analyticsSidebarWidth - $('#graph-controls-and-info').width() - 20
      });

      var renderer = sigInst.renderers[0];
      var container = $(renderer.container);
      renderer.resize(container.width(), container.height());
      sigInst.refresh();

      if (!noUpdateBoxesPositions) {
        that.putBoxesInsideCanvas();
      }

      paper.setup($('.sigma-mouse')[0]);
    },

    /* Update some sizes and styles in analytics mode, but only needed when
     * the analytics mode is activated.
     */
    updateStyles: function() {
      $('header').css({
        paddingLeft: 0,
        paddingRight: 0
      });

      $('body').css({
        overflow: 'hidden'
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
        overflow: 'hidden'
      });

      $('#graph-node-types ul li').css({
        whiteSpace: 'nowrap'
      });

      // Control the scroll bar of the node legend.
      $('#graph-node-types ul').hover(function() {
        $('#graph-node-types ul').css({
          overflowY: 'auto'
        });
      }, function(){
        $('#graph-node-types ul').css({
          overflowY: 'hidden'
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
        overflow: 'hidden'
      });

      $('#graph-rel-types ul li').css({
        whiteSpace: 'nowrap'
      });

      // Control the scrollbar of the rel legend.
      $('#graph-rel-types ul').hover(function() {
        $('#graph-rel-types ul').css({
          overflowY: 'auto'
        });
      }, function(){
        $('#graph-rel-types ul').css({
          overflowY: 'hidden'
        });
      });

      $('#graph-controls-and-info').css({
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

      // Add the proper text to the collapsible boxes.
      $('.collapsible-header').each(function(i) {
        $(this).text(' ' + $(this).text());
        var parentId = $(this).parent().attr('id');
        var collapsed = sylva.positions[parentId].collapsed;
        var icon = 'icon-caret-down';
        if (collapsed) {
          icon = 'icon-caret-right';
        }
        $(this).prepend('<span class="' + icon + ' icon-fixed-width" style="display: inline;"></span>');
      });

      $('#sigma-zoom-in').parent().css({
        marginLeft: '0'
      });
    },

    // Restore the sizes and styles when exit analytics mode.
    restoreSizesAndStyles: function() {
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

      $('#graph-controls-and-info').removeAttr('style');
      $('#graph-node-types').removeAttr('style');
      $('#graph-node-types ul').removeAttr('style');
      $('#sigma-wrapper').removeAttr('style');
      $('#canvas-container').removeAttr('style');
      $('#body').removeAttr('style');
      $('nav.menu').removeAttr('style');
      $('div.inside.clearfix').removeAttr('style');
      $('header').removeAttr('style');
      $('#main').removeAttr('style');
      $('body').removeAttr('style');

      sigInst.renderers[0].resize();
      sigInst.refresh();
    },

    // Saves the boxes position and state in the server.
    updateBoxPositions: function(key, ui) {
      if (canSaveBoxes) {
        var box = $('#' + key);
        var top = box.css('top');
        var left = box.css('left');

        if (ui) {
          var collapsed = true;
          if (ui.newPanel.hasOwnProperty('selector')) {
            collapsed = false;
          }
          sylva.positions[key] = {
            top: top,
            left: left,
            collapsed: collapsed
          };
        } else {
          sylva.positions[key].top = top;
          sylva.positions[key].left = left;
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
      }
    },

    /* Perform the 'real' analytics action. Also perform 'sytle' actions
     * that can't be undone with the 'restoreSizesAndStyles()' method.
     */
    goAnalyticsMode: function() {
      isAnalyticsMode = true;
      $('#id_analytics').val('true');
      $('#searchBox').attr('onsubmit', 'return sylva.Sigma.search()');

      analyticsSidebarBorder = parseInt($('#analytics').css(
        'border-left-width'), 10);

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

      // Makes the analytics column resizable.
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

            /* The next line is needed instead of call that.updateSizes(),
             * because some elements need to be resized apart from our Sigma
             * instance and its elements, like Highcharts.
             */
            $(window).trigger('resize');
            that.putBoxesInsideCanvas();
          }
        });
      }

      var draggableSettings = {
        containment: '#sigma-wrapper',
        cursor: 'move',
        create: function(event, ui) {
          $('#' + event.target.id).css({
            top: sylva.positions[event.target.id].top,
            left: sylva.positions[event.target.id].left
          });
        },
        start: function(event, ui) {
          $('#' + event.target.id).accordion('disable');
          highestZIndex++;
          $('#' + event.target.id).css({
            zIndex: highestZIndex,
          });
        },
        drag: function( event, ui ) {
          $(document).scrollTop(0);
          $(document).scrollLeft(0);
        },
        stop: function(event, ui) {
          setTimeout(function() {
            $('#' + event.target.id).accordion('enable');
          }, 50);
          that.updateBoxPositions(event.target.id);
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
          highestZIndex++;
          $('#' + event.target.id).css({
            zIndex: highestZIndex,
          });

          // This lines control the arrow icon.
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

          that.updateBoxPositions(event.target.id, ui);
        }
      };

      // Makes boxes draggable and collapsible.
      for (var i = 0; i < sylva.collapsibles.length; i++) {
        var name = sylva.collapsibles[i];
        $('#' + name).draggable(draggableSettings);

        if (sylva.positions[name].collapsed) {
          $('#' + name).accordion($.extend({}, collapsibleSettings, {
            active: sylva.positions[name].collapsed
          }));
        } else {
          $('#' + name).accordion(collapsibleSettings);
        }
      }

      sigInst.settings({
        maxNodeSize: analyticsMaxNodeSize * sizeMultiplier
      });

      that.updateStyles();
      that.updateSizes();
      $(window).on('resize', that.updateSizes);

      that.reCenter();
    },

    /* Perform the cancelation of the analytics mode. Also perform the
     * 'remove' of some 'sytles' that can't be done with the
     * 'restoreSizesAndStyles()' method.
     */
    exitAnalyticsMode: function() {
      isAnalyticsMode = false;
      $('#id_analytics').val('');
      $('#searchBox').removeAttr('onsubmit');

      $(window).off('resize', that.updateSizes);

      if (that.isFullscreenMode()) {
        that.exitFullscreenMode();
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

      for (var i = 0; i < sylva.collapsibles.length; i++) {
        var name = sylva.collapsibles[i];
        $('#' + name).draggable('destroy');
        $('#' + name).accordion('destroy');
      }

      that.cleanNodeInfo('#node-info');

      that.restoreSizesAndStyles();
      that.reCenter();
    },


    /* *****
     * Functions for control the graph layout.
     ***** */

    // Performs the 'grid layout algorithm'.
    gridLayout: function(sortFunc, drawHidden) {
      if (!degreesCalculated) {
        that.calculateNodesDegrees();
      }

      var nodes = [];
      if (drawHidden) {
        nodes = visibleNodeIds;
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
    },

    // Performs the 'ciruclar layout algorithm'.
    circularLayout: function(sortFunc, drawHidden) {
      var i = 0;
      var number = size;
      if (drawHidden) {
        number = visibleNodeIds.length;
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
    },

    // Returns a function for order the nodes for use some layouts.
    layoutSort: function(degreeOrder, order) {
      var completeOrder = degreeOrder + order;
      switch (completeOrder) {
        case 'ntd':
          return function(a, b) {
            return a.nodetypeId - b.nodetypeId;
          };
          break;
        case 'nta':
          return function(a, b) {
            return b.nodetypeId - a.nodetypeId;
          };
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
    },

    redrawLayout: function(type, degreeOrder, order, drawHidden) {
      var xPos = '';
      var yPos = '';

      switch (type) {
        case 'force-atlas-2':
          if (visibleNodeIds.length == 0) {
            return;
          }
          that.stop();
          that.start(drawHidden);
          that.addTimeout(timeout);
          $('#sigma-pause').parent().show();
          return;
          break;
        case 'grid':
          that.stop();
          $('#sigma-pause').parent().hide();
          var sortFunc = that.layoutSort(degreeOrder, order);
          that.gridLayout(sortFunc, drawHidden);
          xPos = 'gridX';
          yPos = 'gridY';
          break;
        case 'circular':
          that.stop();
          $('#sigma-pause').parent().hide();
          var sortFunc = that.layoutSort(degreeOrder, order);
          that.circularLayout(sortFunc, drawHidden);
          xPos = 'circularX';
          yPos = 'circularY';
          break;
        default:
          break;
      }

      sigma.plugins.animate(sigInst, {x: xPos, y: yPos}, {duration: 500});
    },


    /* *****
     * Functions for use visualization controls, like buttons.
     ***** */

    clickOnPause: function() {
      if (isDrawing === true) {
        that.stop();
      } else {
        var drawHidden = $('#sigma-hidden-layout').prop('checked');
        that.start(drawHidden);

        // If graph-layout isn't 'label' or FA2 set in FA2.
        var option = $('#sigma-graph-layout').find('option:selected');
        var type = option.attr('id');
        if (type != 'force-atlas-2') {
          option.prop('selected', false);

          option = $('#force-atlas-2');
          option.prop('selected', 'selected');
          type = option.attr('id');

          that.disableOptions(option, type);
          $('#sigma-graph-layout-degree-order').parent().hide();
        }

        var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
        var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
        var drawHidden = $('#sigma-hidden-layout').prop('checked');
        that.redrawLayout(type, degreeOrder, order, drawHidden);
      }
    },

    showHideNodes: function() {
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
          var index = visibleNodeIds.indexOf(nodesId[i]);
          visibleNodeIds.splice(index, 1);
        }
      } else {
        $(this).attr('data-action', 'hide');
        $(this).removeClass('icon-eye-close');
        $(this).addClass('icon-eye-open');
        hidden = false;
        visibleNodeIds = visibleNodeIds.concat(nodesId);
      }

      sigInst.graph.nodes(nodesId).forEach(function(n) {
        n.hidden = hidden;
      });

      var drawHidden = $('#sigma-hidden-layout').prop('checked');
      if (drawHidden && visibleNodeIds.length > 0) {
        var type = $('#sigma-graph-layout').find('option:selected').attr('id');
        var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
        var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
        that.redrawLayout(type, degreeOrder, order, drawHidden);
      } else {
        sigInst.refresh();
      }
    },

    showHideRels: function() {
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
          var index = visibleRelIds.indexOf(relsId[i]);
          visibleRelIds.splice(index, 1);
        }
      } else {
        $(this).attr('data-action', 'hide');
        $(this).removeClass('icon-eye-close');
        $(this).addClass('icon-eye-open');
        hidden = false;
        visibleRelIds = visibleRelIds.concat(relsId);
      }

      sigInst.graph.edges(relsId).forEach(function(e) {
        e.hidden = hidden;
      });

      sigInst.refresh();
    },

    // Creates a widget for change the color of the nodes.
    setNodesColorWidget: function(i, span) {
      var currentColor = $(span).attr('data-color');
      $(span).colpick({
        colorScheme: 'light',
        layout: 'hex',
        submitText: 'Ok',
        color: currentColor.substr(1),  // Colpick doesn't need the '#' char.
        onChange: function(hsb, hex, rgb, el, bySetColor) {
          that.changeNodeColorWidget(span, hex.toUpperCase());
        },
        onShow: function(picker) {
          colorWidgetOpened = true;
        },
        onHide: function(picker) {
          that.hideNodeColorWidget(span, picker);
        },
        onSubmit: function(hsb, hex, rgb, el, bySetColor) {
          that.submitNodeColorWidget(span, hex.toUpperCase());
        }
      });
    },

    // Creates a widget for change the color of the rels.
    setRelsColorWidget: function(i, span) {
      $(span).on('click', function(event) {
        colorWidgetOpened = true;

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

          that.disableOptions(option, type);

          if (type == 'custom') {
            that.improveRelColorWidget(span, container);
          } else {
            that.changeRelColorWidget(span, type, null);
            that.restoreRelColorWidget(container);
            event.stopPropagation()
          }
        });

        button.on('click', function() {
          var type = colorModeSelect.find('option:selected').attr('id');
          that.submitRelColorWidget(span, type);
          that.restoreRelColorWidget(container);
          container.remove();
        });

        var auxHideRelColorWidget = function() {
          that.restoreRelColorWidget(container);
          that.hideRelColorWidget(span);
          container.remove();
          $('body').off('mousedown', auxHideRelColorWidget);
        }

        $('body').on('mousedown', auxHideRelColorWidget);

        container.on('mousedown', function(event){
            event.stopPropagation();
        });

        $('body').append(container);

        if (currentColorMode == 'custom') {
          that.improveRelColorWidget(span, container);
          colorModeSelect.trigger('change');
        }
      });
    },

    exportImage: function() {
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
    },

    // Changes the graph layout.
    controlGraphLayout: function() {
      var option = $(this).find('option:selected');
      var type = option.attr('id');

      that.disableOptions(option, type);

      if (type != 'force-atlas-2') {
        $('#sigma-graph-layout-degree-order').parent().show();
      } else {
        $('#sigma-graph-layout-degree-order').parent().hide();
      }

      var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
      var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
      var drawHidden = $('#sigma-hidden-layout').prop('checked');
      that.redrawLayout(type, degreeOrder, order, drawHidden);
    },

    // Changes the order of the nodes in a graph layout: Type / Degree.
    controlGraphLayoutDegreeOrder: function() {
      var option = $(this).find('option:selected');
      var degreeOrder = option.attr('id');

      that.disableOptions(option, degreeOrder);

      var layoutType = $('#sigma-graph-layout').find('option:selected').attr('id');
      var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
      var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
      var drawHidden = $('#sigma-hidden-layout').prop('checked');
      that.redrawLayout(layoutType, degreeOrder, order, drawHidden);
    },

    // Changes the order of the nodes in a graph layout: Desc / Asc.
    controlGraphLayoutOrder: function() {
      var option = $(this).find('option:selected');
      var order = option.attr('id');

      that.disableOptions(option, order);

      var layoutType = $('#sigma-graph-layout').find('option:selected').attr('id');
      var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
      var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
      var drawHidden = $('#sigma-hidden-layout').prop('checked');
      that.redrawLayout(layoutType, degreeOrder, order, drawHidden);
    },

    // Changes the size of the nodes.
    controlNodeSize: function() {
      var option = $(this).find('option:selected');
      var type = option.attr('id');

      that.disableOptions(option, type);

      if (!degreesCalculated) {
        that.calculateNodesDegrees();
      }

      var animationSize = '';

      var auxMinNodeSize = sigInst.settings('minNodeSize');
      var auxMaxNodeSize = sigInst.settings('maxNodeSize') / sizeMultiplier;
      switch (type) {
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
    },

    // Changes the shape of the rels.
    controlEdgeShape: function() {
      var option = $(this).find('option:selected');
      var type = option.attr('id');

      that.disableOptions(option, type);

      switch (type) {
        case 'straight':
          if (defaultEdgeShapeSaved) {
            sigma.canvas.edges.def = sigma.canvas.edges.defBackup;
          } else {
            return;
          }
          break;
        case 'arrow':
          if (!defaultEdgeShapeSaved) {
            sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
            defaultEdgeShapeSaved = true;
          }
          sigma.canvas.edges.def = sigma.canvas.edges.arrow;
          break;
        case 'curve':
          if (!defaultEdgeShapeSaved) {
            sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
            defaultEdgeShapeSaved = true;
          }
          sigma.canvas.edges.def = sigma.canvas.edges.curve;
          break;
        case 'curved-arrow':
          if (!defaultEdgeShapeSaved) {
            sigma.canvas.edges.defBackup = sigma.canvas.edges.def;
            defaultEdgeShapeSaved = true;
          }
          sigma.canvas.edges.def = sigma.canvas.edges.curvedArrow;
          break;
        default:
          break;
      }
      sigInst.refresh();
    },


    /* ****
     * Utils functions.
     ***** */

     // Performs the real zoom operation of the canva's graph representation.
     zooming: function(zoomIn, position) {
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
    },

    // Set the graph in the middle of the canvas.
    reCenter: function() {
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
    },

    // Returns only the ids of the nodes and the rels from a given graph.
    graphToIds: function(graph) {
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
    },

    /* Disables the selected option and a option with id as 'label' of a select
     * html element.
     */
    disableOptions: function(option, type) {
      var parentId = option.parent().attr('id');
      option.prop('disabled', 'disabled');
      $('#' + parentId + ' option').each(function() {
        var id = $(this).attr('id');
        if (id != type) {
          $(this).prop('disabled', false);
        }
      });
    },

    /* Creates the initial state of the draggable and collapsible boxes
     * (position and collapsed state) if they come without state from the
     * server.
     */
    createCollapsiblesStructures: function() {
      sylva.collapsibles = [
        'graph-node-types',
        'graph-rel-types',
        'graph-layout'
      ];

      sylva.positions['graph-node-types'] = {
        top :'15px',
        left: '15px',
        collapsed: false
      };
      sylva.positions['graph-rel-types'] = {
        top :'15px',
        left: '150px',
        collapsed: true
      };
      sylva.positions['graph-layout'] = {
        top :'15px',
        left: '380px',
        collapsed: false
      };
    },

    // It calculates the three degrees of each node: total, in and out.
    calculateNodesDegrees: function() {
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
    },

    /* It moves the draggable graph controls inside the canvas if they are
     * outside in any monent.
     */
    putBoxesInsideCanvas: function() {
      canSaveBoxes = false;
      for (var i = 0; i < sylva.collapsibles.length; i++) {
        var name = sylva.collapsibles[i];
        $('#' + name).simulate('drag', {dx: -1, dy: -1});
        $('#' + name).simulate('drag', {dx: 1, dy: 1});
      }
      setTimeout(function() {
        canSaveBoxes = true;
      }, 300);
    },

    // It returns the neighbors of a given node.
    obtaingNeighborhood: function(center) {
      var neighborhood = sigInst.graph.neighborhood(center.id);
      var neighborhoodIds = that.graphToIds(neighborhood);

      return neighborhoodIds;
    },

    // Translate coordinates from Sigma to the regular canvas.
    translateCoordinates: function(node) {
      return {
        x: node['renderer1:x'],
        y: node['renderer1:y']
      };
    },

    // Select or deselect only
    selectDeselectNode: function(node) {
      var index = sylva.selectedNodes.indexOf(node.id);

      if (index  >= 0) {
        sylva.selectedNodes.splice(index, 1);
      } else {
        sylva.selectedNodes.push(node.id);
      }

      that.grayfyNonListedNodes(sylva.selectedNodes);
    },

    // It manages the buttons of the selecting tools.
    enableDisableSelectingTool: function(type) {
      that.stop();

      var selectingToolDict = {
        'rectangle': 'sigma-filter-rectangle',
        'freeHand': 'sigma-filter-free-hand',
        'neighbors': 'sigma-filter-neighbors',
        'click': 'sigma-filter-click'
      };

      if (selectedSelectingTool == '') {
        // Activate a tool.
        selectedSelectingTool = type;
        $('#' + selectingToolDict[type]).addClass('active');

        if (type != 'click' && type != 'neighbors') {
          that.activateSelectingAreaTool(type);
        }

      } else if(selectedSelectingTool == type) {
        // Deactivate a tool.
        selectedSelectingTool = '';
        $('#' + selectingToolDict[type]).removeClass('active');

        if (type != 'click' && type != 'neighbors') {
          that.deactivateSelectingAreaTool(type);
        }

      } else {
        // Deactivate a tool and activate another.
        if(selectedSelectingTool != 'click' && selectedSelectingTool != 'neighbors') {
          that.deactivateSelectingAreaTool(type);
        }

        $('#' + selectingToolDict[selectedSelectingTool]).removeClass('active');
        selectedSelectingTool = type;
        $('#' + selectingToolDict[type]).addClass('active');

        if (type != 'click' && type != 'neighbors') {
          that.activateSelectingAreaTool(type);
        }
      }
    },

    /* It manages the activation and behavior of the two selecting tools that
     * use areas: rectangle and free hand.
     */
    activateSelectingAreaTool: function(type) {
        that.setUsualSigmaSettings(false, false);
        $('.sigma-mouse').css({
          cursor: 'crosshair'
        });

        paperTool = new paper.Tool();
        if (type == 'freeHand') {
          paperTool.minDistance = 20;
        }

        var path;
        var origin;

        paperTool.onMouseDown = function(event) {
          if (path) {
            path.removeSegments();
          }
          path = new paper.Path();
          path.fillColor = new paper.Color(0, 0, 125, 0.075);
          path.fullySelected = true;

          origin = event.point;
        };

        paperTool.onMouseDrag = function(event) {
          var point = event.point;

          if (type == 'rectangle') {
            path.removeSegments();

            path.add(origin);
            path.add([point.x, origin.y]);
            path.add(point);
            path.add([origin.x, point.y]);
            path.add(origin);
          } else if ('freeHand') {
            path.add(event.point);
          }

          paper.view.draw();
        };

        paperTool.onMouseUp = function(event) {
          sylva.selectedNodes = [];
          sigInst.graph.nodes().forEach(function(n) {
            var point = new paper.Point(n['renderer1:x'], n['renderer1:y']);
            if (path.contains(point)) {
              sylva.selectedNodes.push(n.id);
            }
          });

          that.grayfyNonListedNodes(sylva.selectedNodes);
          $('.sigma-mouse').css({
            cursor: ''
          });

          path.removeSegments();
          paperTool.remove();
          that.enableDisableSelectingTool(type);
        };
    },

    /* It manages the deactivation of the two selecting tools that use areas:
     * rectangle and free hand.
     */
    deactivateSelectingAreaTool: function(type) {
      paperTool.remove();

      that.setUsualSigmaSettings(true, true);

      $('.sigma-mouse').css({
        cursor: ''
      });
    },

    /* It is special selection tool: use the result of the regular search for
     * select nodes.
     */
    search: function() {
      var searchBox = $('#searchBox');
      var ipnuts = searchBox.find('input');
      $('#id_q').css({
        backgroundImage: 'url(' + sylva.searchLoadingImage + ')'
      });

      var params = {};
      for (var i = 0; i < ipnuts.length; i++) {
        params[$(ipnuts[i]).attr('name')] = $(ipnuts[i]).attr('value');
      }

      var jqxhr = $.ajax({
        url: searchBox.attr('action'),
        type: 'POST',
        data: params,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        $('#id_q').val('');
        $('#id_q').trigger('blur');

        sylva.selectedNodes = data.nodeIds;
        that.grayfyNonListedNodes(sylva.selectedNodes);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
      });
      jqxhr.complete(function() {
        $('#id_q').removeAttr('style');
      });

      return false;
    },

    // A shortcut for change the most usual Sigma's settings.
    setUsualSigmaSettings: function(mouse, hover) {
      sigInst.settings({
        mouseEnabled: mouse,
        enableHovering: hover
      });
      sigInst.refresh();
    },

    // It creates the black-alpha layer behind the modals.
    createOverlay: function() {
      var overlay = $('<div id="overlay" class="modal-overlay">');
      $('body').append(overlay);
    },

    // It destroys the black-alpha layer behind the modals.
    destroyOverlay: function() {
      $('#overlay').remove();
    },

    // The common behaviour for opening the modals.
    openNodeModal: function(dialog) {
      dialog.container.fadeIn('fast');
      dialog.data.fadeIn('fast');
    },

    // The common behaviour for closing the modals.
    closeNodeModal: function(dialog) {
      dialog.container.fadeOut('fast');
      dialog.data.fadeOut('fast');

      /* The next lines will destroy the modal instance completely and the
       * orginal data that SimpeModal saved.
       */
      setTimeout(function() {
        $.modal.close();
        if ($('#edit-node-modal').length) {
          $('#edit-node-modal').remove();
        } else if ($('#delete-node-modal').length) {
          $('#delete-node-modal').remove();
        } else {
          $('#loading-node-modal').remove();
        }
      }, fast);
    },

    // It closes the modal and destroys the overlay layer.
    closeModalLib: function() {
      $.modal.close();
      setTimeout(function() {
        that.destroyOverlay();
      }, fast);
    },

    /* It creates a mini-modal with for display it while we are getting the
     * data for the form modals.
     */
    showLoadingModal: function(crateOverlay) {
      // Creating the HTML to show.
      var modalLoading = $('<div id="loading-node-modal" style="display:none">');
      $('body').append(modalLoading);
      modalLoading.text('Loading...');

      var modalPadding = 10;

      // The creation of the loading modal.
      if (crateOverlay) {
        that.createOverlay();
      }
      $('#' + modalLoading.attr('id')).modal({
        // Options.
        modal: true,
        escClose: false,

        // Styles.
        containerCss: {
          backgroundColor: '#FFFFFF',
          borderRadius: modalPadding,
          padding: modalPadding,
          display: 'inline-block'
        },

        // Events.
        onOpen: function(dialog) {
          that.openNodeModal(dialog);
        },
        onClose: function(dialog) {
          that.closeNodeModal(dialog);
        },
      });
    },

    /* It will handle the event when the users'll click in the 'edit node'
     * link. It will get HTML to show, but won't show it.
     */
    prepareEditNodeModal: function(event) {
      that.showLoadingModal(true);

      var url = $(event.target).attr('data-url');
      var params = {
        'asModal': true
      };

      // Performing the request with the created variables.
      var jqxhr = $.ajax({
        url: url,
        type: 'GET',
        data: params,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        $.modal.close(); // Closing the loading modal.
        setTimeout(function() {
          that.showEditNodeModal(data.html);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });
    },

    /* It displays the 'edit node' form in a modal and prepares it for use it
     * as a modal.
     */
    showEditNodeModal: function(data) {
      // Setting the form into the HTML.
      var modalForm = $('<div id="edit-node-modal" style="display: none;">');
      $('body').append(modalForm); // This line need to be executed here, so the internal JS will be executed.
      modalForm.append(data);

      // Getting the URL for delete the node.
      var deleteUrl = $('#delete-url').attr('data-url');

      // Hidding "Add node" links.
      $('.add-node').hide();

      // Binding the 'events' for the four actions.
      $('#submit-save').attr('onclick',
        'return sylva.Sigma.saveEditNodeModal(this)');
      $('#submit-save-as-new').attr('onclick',
        'return sylva.Sigma.saveEditNodeModal(this)');
      $('#submit-delete').on('click', function() {
        $.modal.close();
        setTimeout(function() {
          that.prepareDeleteNodeModal(deleteUrl);
        }, fast);
      });
      $('#submit-cancel').on('click', function() {
        // The next is the way to completely close the modal.
        that.closeModalLib();
      });

      // Getting HTML elemetns as variables.
      var scrollWrapper = $('#modal-content-scrollable-wrapper');
      var scrollContent = $('#modal-content-scrollable');
      var contentControls = $('#modal-content-controls');
      scrollWrapper.addClass('modal-content-scrollable-wrapper');
      contentControls.addClass('modal-content-controls');


      // Size variables for the modal library.
      var windowHeight = Math.max(document.documentElement.clientHeight,
          window.innerHeight || 0);
      var windowWidth = Math.max(document.documentElement.clientWidth,
          window.innerWidth || 0);
      var modalPadding = 10;

      // Calculating the width of the form.
      var widths = scrollContent.children().map(function(){
        return $(this).outerWidth(true);
      });
      var modalWidth = 0;
      $.each(widths, function() {
        modalWidth += this;
      });

      // Creating the modal.
      $('#' + modalForm.attr('id')).modal({
        // Options.
        modal: true,
        escClose: false,

        // Styles.
        maxHeight: windowHeight - (modalPadding * 2),
        maxWidth: windowWidth - (modalPadding * 2),
        containerCss: {
          backgroundColor: '#FFFFFF',
          borderRadius: modalPadding,
          padding: modalPadding,
          display: 'inline-block'
        },

        // Events.
        onOpen: function(dialog) {
          that.openNodeModal(dialog);
        },
        onClose: function(dialog) {
          that.closeNodeModal(dialog);
        },
        onShow: function(dialog) {
          var scrollHeigth = dialog.wrap.height() - contentControls.height();

          // It's the content who controls the scrollbars.
          dialog.wrap.css({
            overflow: 'hidden'
          });

          scrollContent.css({
            width: modalWidth
          });

          scrollWrapper.css({
            height: scrollHeigth,
          });

          scrollWrapper.on('mouseover', function() {
            scrollWrapper.css({
              overflow: 'auto'
            });
            /* The next lines are for show de horizontal scrollbar only when
             * it's needed.
             */
            if (windowWidth >= (modalWidth + modalPadding)) {
              scrollWrapper.css({
                overflowX: 'hidden'
              });
            }
          });

          scrollWrapper.on('mouseout', function() {
            scrollWrapper.css({
              overflow: 'hidden'
            });
          });
        }
      });
    },

    /* This function handles the 'Save' and 'Save as new' options from the
     * 'edit node modal'.
     */
    saveEditNodeModal: function(button) {
      // Closing the 'edit node' modal and showing the loading one.
      $.modal.close();
      setTimeout(function() {
        that.showLoadingModal();
      }, fast);

      // Obtaining the parameters.
      var url = $('#save-url').attr('data-url');
      var serializedForm = $('#edit-node-form').serialize() + '&asModal=true';

      if (button.id == 'submit-save-as-new') {
        serializedForm += '&as-new=true';
      }

      // Performing the request with the created variables.
      var jqxhr = $.ajax({
        url: url,
        type: 'POST',
        data: serializedForm,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        /* Here we need a double 'setTimeout()' because the previous one, also
         * inside this function maybe isn't finished when the AJAX request
         * starts.
         */
        setTimeout(function() {
          $.modal.close(); // Closing the loading modal.
          setTimeout(function() {
            that.performModalServerResponse(data);
          }, fast);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });

      // False is needed, that way the form isn't sended.
      return false;
    },

    /* It will handle the event when the users'll click in the 'Remove'
     * button. It will get HTML to show, but won't show it.
     */
    prepareDeleteNodeModal: function(url) {
      that.showLoadingModal(false);

      var params = 'asModal=true';

      // Performing the request with the created variables.
      var jqxhr = $.ajax({
        url: url,
        type: 'GET',
        data: params,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        $.modal.close(); // Closing the loading modal.
        setTimeout(function() {
          that.showDeleteNodeModal(data.html);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });
    },

    /* It displays the 'remove node' form in a modal and prepares it for use it
     * as a modal.
     */
    showDeleteNodeModal: function(data) {
      // Setting the form into the HTML.
      var modalForm = $('<div id="delete-node-modal" style="display: none;">');
      $('body').append(modalForm);
      modalForm.append(data);

      // Removing style.
      $('#content2').css({
        minHeight: '100px',
        overflow: 'hidden'
      });
      // Binding the 'events' for the two actions.
      $('#submit-delete').attr('onclick',
        'return sylva.Sigma.continueDeleteNodeModal()');
      $('#submit-cancel').removeAttr('href');
      $('#submit-cancel').on('click', function() {
        that.closeModalLib();
      });

      // Size variables for the modal library.
      var modalPadding = 10;

      // Creating the modal.
      $('#' + modalForm.attr('id')).modal({
        // Options.
        modal: true,
        escClose: false,

        // Styles.
        containerCss: {
          backgroundColor: '#FFFFFF',
          borderRadius: modalPadding,
          padding: modalPadding,
          display: 'inline-block'
        },

        // Events.
        onOpen: function(dialog) {
          that.openNodeModal(dialog);
        },
        onClose: function(dialog) {
          that.closeNodeModal(dialog);
        }
      });
    },

    /* This function handles the 'Continue' options from the
     * 'delete node modal'.
     */
    continueDeleteNodeModal: function() {
     // Closing the 'delete node' modal and showing the loading one.
      $.modal.close();
      setTimeout(function() {
        that.showLoadingModal();
      }, fast);

      // Obtaining the parameters.
      var url = $('#delete-url').attr('data-url');
      var serializedForm = $('#delete-node-form').serialize() + '&asModal=true';

      // Performing the request with the created variables.
      var jqxhr = $.ajax({
        url: url,
        type: 'POST',
        data: serializedForm,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        /* Here we need a double 'setTimeout()' because the previous one, also
         * inside this function maybe isn't finished when the AJAX request
         * starts.
         */
        setTimeout(function() {
          $.modal.close(); // Closing the loading modal.
          setTimeout(function() {
            that.performModalServerResponse(data);
          }, fast);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });

      // False is needed for the form is not sending.
      return false;
    },

    // It acts depending of what the server returns from the modal forms.
    performModalServerResponse: function(response) {
      if (response.type == 'html') {
        // If it's 'html' it's a form with errors.

        if(response.action == 'edit') {
          that.showEditNodeModal(response.html);
        } else {
          that.showDeleteNodeModal(response.html);
        }
      } else {
        // If it is not, is a final reponse.

        that.destroyOverlay(); // Exiting, so destroying the overlay layer.

        switch (response.action) {
          case 'edit':
            that.deleteNodeFromModal(response);
            that.addNodeFromModal(response);
            break;
          case 'new':
            that.addNodeFromModal(response);
            break;
          case 'delete':
            that.deleteNodeFromModal(response);
            break;
          case 'nothing':
          default:
            break;
        }

        // Redraw the Sigma's layout because of the changes.
        if (response.action != 'nothing') {
          var type = $('#sigma-graph-layout').find('option:selected').attr('id');
          var degreeOrder = $('#sigma-graph-layout-degree-order').find('option:selected').attr('id');
          var order = $('#sigma-graph-layout-order').find('option:selected').attr('id');
          var drawHidden = $('#sigma-hidden-layout').prop('checked');
          that.redrawLayout(type, degreeOrder, order, drawHidden);
        }
      }
    },

    deleteNodeFromModal: function(response) {
      // Obtaining the node.
      var node = null;
      if (response.action == 'edit') {
        // Saving the coordinates.
        var oldNode = sigInst.graph.nodes(response.nodeId);
        response.node.x = oldNode.x;
        response.node.y = oldNode.y;

        node = response.node;
      } else {
        node = sigInst.graph.nodes(response.nodeId);
      }

      /* Deleting the node from the 'selectedNodes' array. It will be added in
       * 'addNodeFromModal'
       */
      var index = sylva.selectedNodes.indexOf(response.nodeId);
      if (index >= 0) {
        wasDeletedNodeSelected = true;
        sylva.selectedNodes.splice(index, 1);
      } else {
        wasDeletedNodeSelected = false;
      }

      /* Deleting the node from the nodes array of the nodetype. It will be
       * added in 'addNodeFromModal'.
       */
      var nodetypeArray = sylva.nodetypes[node.nodetypeId].nodes;
      var index = nodetypeArray.indexOf(response.nodeId);
      nodetypeArray.splice(index, 1);
      sylva.nodetypes[node.nodetypeId].nodes = nodetypeArray;

      /* Deleting the node from the array of visible nodes. It will be added in
       * 'addNodeFromModal'.
       */
      index = visibleNodeIds.indexOf(response.nodeId);
      if (index >= 0) {
        visibleNodeIds.splice(index, 1);
      }

      /* Deleting the relationships from the relationships arrays of the
       * reltypes, because they will be added in 'addNodeFromModal'. Also we
       * are deleting them from the array of visible relationships.
       */
      for (var i = 0; i < response.oldRelationshipIds.length; i++) {
        var rel = sigInst.graph.edges(response.oldRelationshipIds[i]);
        var reltypeArray = sylva.reltypes[rel.reltypeId].relationships;
        var index = reltypeArray.indexOf(response.oldRelationshipIds[i]);
        reltypeArray.splice(index, 1);
        sylva.reltypes[rel.reltypeId].relationships = reltypeArray;

        index = visibleRelIds.indexOf(response.oldRelationshipIds[i]);
        if (index >= 0) {
          visibleRelIds.splice(index, 1);
        }
      }

      // Cleaning the info box.
      that.cleanNodeInfo('#node-info');

      /* Deleting the node from the graph, because it will be added in
       * 'addNodeFromModal'. Also this delete the envolved relationships.
       */
      sigInst.graph.dropNode(response.nodeId);

      // Finishing touches.
      size -= 1;
      sylva.size -= 1;
      if (response.action == 'delete') {
        that.calculateNodesDegrees();
        sigInst.refresh();
      }
    },

    addNodeFromModal: function(response) {
      // Adding the node to the 'selectedNodes' array.
      var selectedAsEdit = response.action == 'edit' && wasDeletedNodeSelected;
      var selectedAsNew = response.action == 'new' &&
        sylva.size == sylva.selectedNodes.length;
      if (selectedAsEdit || selectedAsNew) {
        sylva.selectedNodes.push(response.nodeId);
      }

      // Adding the node to the nodes array of the nodetype.
      sylva.nodetypes[response.node.nodetypeId].nodes.push(response.nodeId);

      // Setting the visibility of the node (hidden or not).
      var visibilityButton = $('.show-hide-nodes[data-nodetype-id="' + response.node.nodetypeId + '"]');
      if (visibilityButton.attr('data-action') == 'hide') {
        response.node.hidden = false;
        visibleNodeIds.push(response.nodeId);
      } else {
        response.node.hidden = true;
      }

      // Adding the node to the graph.
      sigInst.graph.addNode(response.node);

      /* Adding the relationships to the graph. Also here we are setting the
       * visibility of the relationships (hidden or not). Finally, we are
       * adding the relationships to the relationships arrays of the reltypes.
       */
      for (var i = 0; i < response.relationships.length; i++) {
        var rel = response.relationships[i];
        var visibilityButton = $('.show-hide-rels[data-reltype-id="' + rel.reltypeId + '"]');
        if (visibilityButton.attr('data-action') == 'hide') {
          rel.hidden = false;
          visibleRelIds.push(rel.id);
        } else {
          rel.hidden = true;
        }
        sylva.reltypes[rel.reltypeId].relationships.push(rel);
        sigInst.graph.addEdge(rel);
      }

      // Updating the info box.
      that.updateNodeInfo(response.node, '#node-info');

      // Finishing touches.
      size += 1;
      sylva.size += 1;
      that.calculateNodesDegrees();
      sigInst.refresh();
      that.grayfyNonListedNodes(sylva.selectedNodes);
    }

  };

  // Reveal module.
  window.sylva.Sigma = Sigma;

})(sylva, sigma, jQuery, window, document);
