// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true,
clearTimeout */


/****************************************************************************
 * Sigma.js visualization
 ****************************************************************************/

;(function(sylva, sigma, $, window, document, undefined) {

  // Layout algorithm state.
  var isDrawing = false;
  // setTimeout id.
  var timeout_id = 0;
  // True when the "Go fullscreen" button is clicked.
  var isFullscreenByButton = false;

  var Sigma = {

    init: function() {
      var that = this;
      // Node info.
      var $tooltip;
      // Graph size.
      var size = sylva.size;
      // Objects for play with them for show and hide nodes.
      var nodesHidden = {}  // Hidden nodes by selecting theirs types.
      var nodesToShow = [];  // For show the nodes after the "outnodes" event.
      // It saves the link in the Sylva logo when Sylva goes in fullscreen mode.
      var linkLogo;

      // Instanciate Sigma.js and customize rendering.
      var sigInst = sigma.init(document.getElementById('sigma-container')).drawingProperties({
        defaultLabelColor: '#000',
        defaultLabelSize: 14,
        defaultLabelBGColor: '#fff',
        defaultLabelHoverColor: '#000',
        labelThreshold: 15,
        defaultEdgeType: 'curve'
      }).graphProperties({
        minNodeSize: 0.5,
        maxNodeSize: 5,
        minEdgeSize: 3,
        maxEdgeSize: 3
      }).mouseProperties({
        maxRatio: 32
      });

      // Add nodes.
      $.each(sylva.nodes, function(nodetypeId, nodes) {
        for (var n in nodes) {
          sigInst.addNode(n, {
            x: Math.random(),
            y: Math.random(),
            color: sylva.nodetypes[nodetypeId].color,
            nodetypeId: nodetypeId
          });
        }
      });

      // Add edges.
      for (var e in sylva.edges) {
        sigInst.addEdge(sylva.edges[e].id, sylva.edges[e].source, sylva.edges[e].target);
      }

      // Create the legend.
      $('#node-type-legend').empty();
      var list = $('#node-type-legend').append($('<ul>'));
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

      // Show node info and hide the rest of nodes and edges.
      sigInst.bind('overnodes', function(event) {
        var nodes = event.content;
        var nodePK = nodes[0];  // node primary key
        var nodetypeId = sigInst.getNodes(nodePK).attr.nodetypeId
        var neighbors = {};
        var isOrphan = true;

        // Converts obj properties into a string.
        var attributesToString = function(obj) {
          var str = [];
          for (var prop in obj) {
            if (obj.hasOwnProperty(prop)) {
              str.push('<li>' + prop + ': ' + obj[prop] + '</li>');
            }
          }
          return str.join('');
        };

        var showInfo = $('#sigma-node-info').prop('checked');
        if (showInfo) {
          // Show node info popup.
          var plusLeft = 212;
          var plusTop = 61;
          if (isFullscreenByButton) {
            plusLeft = -8;
            plusTop = 4;
          }
          sigInst.iterNodes(function(node) {
            $tooltip =
              $('<div class="node-info"></div>')
                .append('<ul>' + attributesToString(sylva.nodes[nodetypeId][nodePK]) + '</ul>')
                .css({
                  'left': node.displayX + plusLeft,
                  'top': node.displayY + plusTop
                });
            $('#sigma-container').append($tooltip);
          }, [nodePK]);
        }

        var showRelatedNodes = $('#sigma-related-nodes').prop('checked');
        if (showRelatedNodes) {
          // Hide edges and nodes.
          sigInst.iterEdges(function(e) {
            if (nodes.indexOf(e.source) >= 0 || nodes.indexOf(e.target) >= 0) {
              neighbors[e.source] = true;
              neighbors[e.target] = true;
              isOrphan = false;
            }
          });
          if (isOrphan) {
            neighbors[nodePK] = true;
          }
          var nodesHiddenAsArray = Object.keys(nodesHidden);
          sigInst.iterNodes(function(n) {
            if (!neighbors[n.id] && $.inArray(n.id, nodesHiddenAsArray) < 0) {
              nodesToShow.push(n.id);  // Used for only show these nodes in the "outnodes" event.
              n.hidden = true;
            }
          });
          // Draw graph.
          sigInst.draw();
        }

        // Update node legend.
        sylva.Utils.updateNodeLegend(sylva.nodes[nodetypeId][nodePK].id, nodePK, 'element-info');
      });

      // Hide node info popup and show the rest of nodes and edges.
      sigInst.bind('outnodes', function(event) {
        // Hide node info.
        $('.node-info').remove();
        var showRelatedNodes = $('#sigma-related-nodes').prop('checked');
        if (showRelatedNodes) {
          sigInst.iterNodes(function(n) {
            n.hidden = false;
          }, nodesToShow).draw();
          nodesToShow = [];
        }
      });

      // Bind pause button.
      $('#sigma-pause').on('click', function() {
        if (isDrawing === true) {
          that.stop();
        } else {
          that.start();
        }
      });

      // Bind FishEye checkbox.
      $('#sigma-fisheye').on('change', function() {
        var fisheye = $(this).prop('checked');
        if (fisheye) {
        sigInst.activateFishEye().draw();
        } else {
        sigInst.desactivateFishEye().draw();
        }
      });

      $('#sigma-export-image').on('mouseover', function() {
        that.stop();
      });

      // Hide/show nodes by type.
      $('.show-hide-nodes').on('click', function() {
        var nodetypeId = $(this).attr('data-nodetype-id');
        var action = $(this).attr('data-action');
        if (action == "hide") {
          $(this).attr('data-action', 'show');
          $(this).removeClass('icon-eye-open');
          $(this).addClass('icon-eye-close');
          sigInst.iterNodes(function(n) {
            n.hidden = true;
          }, Object.keys(sylva.nodes[nodetypeId])).draw();
          // Adding the nodes to a dictionary to know which nodes hide in the "overnodes" event.
          $.extend(nodesHidden, sylva.nodes[nodetypeId]);
        } else {
          $(this).attr('data-action', 'hide');
          $(this).removeClass('icon-eye-close');
          $(this).addClass('icon-eye-open');
          sigInst.iterNodes(function(n) {
            n.hidden = false;
          }, Object.keys(sylva.nodes[nodetypeId])).draw();
          // Deleting the nodes from a dictionary to know which nodes hide in the "overnodes" event.
          $.each(sylva.nodes[nodetypeId], function(key, value) {
            delete nodesHidden[key];
          });
        }
      });

      // Change the color of the nodes and the legend.
      function changeNodesColor(nodetypeId, color, span) {
        var currentColor = $(span).css('background-color');
        currentColor = new RGBColor(currentColor).toHex().toUpperCase();
        if (currentColor != color) {
          sigInst.iterNodes(function(n) {
            n.color = color;
          }, Object.keys(sylva.nodes[nodetypeId])).draw();
          $(span).css({
            backgroundColor: color
          });
        }
      }

      /* Change the color of the nodes and the legend when the user is
       * selecting it in the widget.
       */
      function changeColorWidget(span, hex) {
        var nodetypeId = $(span).attr('data-nodetype-id');
        var newColor = '#' + hex
        changeNodesColor(nodetypeId, newColor, span);
      }

      /* Restore the color of the nodes and the legend when the user click out
       * of the widget.
       */
      function hideColorWidget(span, picker) {
        if ($(picker).is(':visible')) {
          var nodetypeId = $(span).attr('data-nodetype-id');
          var oldColor = $(span).attr('data-color');
          $(span).colpickSetColor(oldColor.substr(1));
          changeNodesColor(nodetypeId, oldColor, span);
        }
      }

      /* Change the color of the nodes and the legend and submit to server.
       * Also, restore the color if the request fails.
       */
      function submitColorWidget(span, hex) {
        var nodetypeId = $(span).attr('data-nodetype-id');
        var newColor = '#' + hex;
        var oldColor = $(span).attr('data-color');
        changeNodesColor(nodetypeId, newColor, span);
        $(span).attr('data-color', newColor);
        $(span).colpickHide();
        params = {
          nodetypeId: nodetypeId,
          color: newColor
        };
        var jqxhr = $.post(sylva.edit_nodetype_color_ajax_url, params, 'json');
        jqxhr.error(function() {
          changeNodesColor(nodetypeId, oldColor, span);
          $(span).attr('data-color', oldColor);
          alert(gettext("Oops! Something went wrong with the server."));
        });
      }

      // Change nodes color.
      $('.change-nodes-color').each(function(i, span) {
        var currentColor = $(span).attr('data-color');
        $(span).colpick({
          colorScheme: 'light',
          layout: 'hex',
          submitText: 'Ok',
          color: currentColor.substr(1),  // Colpick doesn't need the '#' char.
          onChange: function(hsb, hex, rgb, el, bySetColor) {
            changeColorWidget(span, hex.toUpperCase());
          },
          onHide: function(picker) {
            hideColorWidget(span, picker);
          },
          onSubmit: function(hsb, hex, rgb, el, bySetColor) {
            submitColorWidget(span, hex.toUpperCase());
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
        ctx.drawImage(document.getElementById('sigma_edges_1'), 0, 0);
        ctx.drawImage(document.getElementById('sigma_nodes_1'), 0, 0);
        ctx.drawImage(document.getElementById('sigma_labels_1'), 0, 0);
        var img_data = canvas.toDataURL('image/png');
        $(this).attr('href', img_data.replace('image/png', 'image/octet-stream'));
        $canvas.remove();
      });

      // Go fullscreen.
      $('#sigma-go-fullscreen').on('click', function() {
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
      });

      // Exit fullscreen.
      $('#sigma-exit-fullscreen').on('click', function() {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        }
      });

      // Handle the fullscreen mode changes.
      function handleFullscreen() {
        if(isFullscreenByButton) {
          isFullscreenByButton = false;
          stopFullscreen();
        } else {
          isFullscreenByButton = true;
          goFullscreen();
        }
      }

      /* Update some sizes in fullscreen mode. This function will be called
       * when changes in the size of the screen occurr, e.g., when the user
       * open the developers tools in fullscreen mode.
       */
      function updateSizes() {
          var height = $(window).height();
          var width = $(window).width();

          $('header').width(width);
          $('#main').width(width);
          $('div.inside.clearfix').width(width);
          $('#body').width(width);

          var trueHeaderHeight =  $('div.inside.clearfix').height();
          $('#body').height(height - trueHeaderHeight);

          // The new width will be: screenWidth - leftWhiteSpace - canvasInfo- rightWhiteSpace - sigmaWrapperBorder - (safeSpace between canvasInfo and canvas)
          $('#sigma-wrapper').width(width);

          // The new height will be: screenHeight - header - whiteSpace - graphControls - (border + padding from canvasInfo) - whiteSpace
          $('#sigma-wrapper').height(height - 51);

          var top = height - 97;
          var left = width - 52;
          $('#sigma-pause').css({
            top: top + "px",
            left: left + "px"
          });

          sigInst.resize();
      }

      /* Update some sizes and styles in fullscreen mode, but only needed when
       * the fullscreen mode is activated.
       */
      function updateStyles() {
        $('#body').css({
          paddingBottom: "0",
          paddingTop: "0"
        });

        $('#sigma-wrapper').css({
          border: "none",
          marginRight: "20px",
          marginTop: "-14px"
        });

        $('.graph-controls').css({
          position: "absolute",
          right: "60px",
          paddingTop: "10px",
          paddingRight: "10px",
          borderRadius: "10px",
          backgroundColor: "rgba(214, 231, 223, 0.5)"
        });

        $('#canvas-info').css({
          position: "absolute",
          zIndex: "100",
          border: "none",
          overflow: "auto",
          padding: "10px",
          height: "auto",
          borderRadius: "10px",
          backgroundColor: "rgba(214, 231, 223, 0.5)"
        });
      }

      // Restore the sizes and styles when exit fullscreen mode.
      function restoreSizesAndStyles() {
        $('#sigma-pause').removeAttr('style');
        $('#sigma-wrapper').removeAttr('style');
        $('.graph-controls').removeAttr('style');
        $('#canvas-info').removeAttr('style');
        $('#body').removeAttr('style');
        $('div.inside.clearfix').removeAttr('style');
        $('#main').removeAttr('style');
        $('header').removeAttr('style');

        sigInst.resize();
      }

      /* Perform the 'real' fullscreen action. Also perform "sytle" actions
       * that can't be undone with the "restoreSizesAndStyles()" method.
       */
      function goFullscreen() {
        $('#sigma-go-fullscreen').hide();
        $('nav.main li').hide();
        $('header.global > h2').hide();
        $('nav.menu').hide();
        $('div.graph-item').hide();
        $('div#footer').hide();
        $('#graphcanvas').hide();

        $('#link-logo').bind('click', false);
        $('#link-logo').addClass('disabled');
        linkLogo = $('#link-logo').attr('href');
        $('#link-logo').removeAttr('href');

        $('.title-graph-name').show();
        $('#sigma-exit-fullscreen').parent().show();

        updateSizes();
        updateStyles();

        $(window).on('resize', updateSizes);
      }

      /* Perform the cancelation of the fullscreen mode. Also perform the
       * "remove" of some "sytles" that can't be done with the
       * "restoreSizesAndStyles()" method.
       */
      function stopFullscreen() {
        $('#sigma-go-fullscreen').show();
        $('nav.main li').show();
        $('header.global h2').show();
        $('nav.menu').show();
        $('div.graph-item').show();
        $('div#footer').show();

        $('#link-logo').unbind('click');
        $('#link-logo').removeClass('disabled');
        $('#link-logo').attr('href', linkLogo);

        $('.title-graph-name').hide();
        $('#sigma-exit-fullscreen').parent().hide();

        $(window).unbind('resize');
        restoreSizesAndStyles();
      }

      // Listeners for handle the "fullscreen" events.
      $(document).on('fullscreenchange', handleFullscreen);
      $(document).on('mozfullscreenchange', handleFullscreen);
      $(document).on('webkitfullscreenchange', handleFullscreen);

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
    },

    // Start layout algorithm.
    start: function() {
      var sigInst = sigma.instances[1];
      if (sigInst) {
        sigInst.startForceAtlas2();
      } else {
        Sigma.init();
      }
      isDrawing = true;
      $('#sigma-pause').html('Pause');
    },

    // Stop layout algorithm.
    stop: function() {
      this.removeTimeout();
      var sigInst = sigma.instances[1];
      if (sigInst) {
        sigInst.stopForceAtlas2();
        isDrawing = false;
        $('#sigma-pause').html('Play');
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
