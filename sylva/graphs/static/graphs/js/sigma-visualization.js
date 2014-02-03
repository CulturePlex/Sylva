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

  colors = ['#F70000', '#B9264F', '#990099', '#74138C', '#0000CE',
        '#1F88A7', '#4A9586', '#FF2626', '#D73E68', '#B300B3', '#8D18AB',
        '#5B5BFF', '#25A0C5', '#5EAE9E', '#FF5353', '#DD597D', '#CA00CA',
        '#A41CC6', '#7373FF', '#29AFD6', '#74BAAC', '#FF7373', '#E37795',
        '#D900D9', '#BA21E0', '#8282FF', '#4FBDDD', '#8DC7BB', '#FF8E8E',
        '#E994AB', '#FF2DFF', '#CB59E8', '#9191FF', '#67C7E2', '#A5D3CA',
        '#FFA4A4', '#EDA9BC', '#F206FF', '#CB59E8', '#A8A8FF', '#8ED6EA',
        '#C0E0DA', '#FFB5B5', '#F0B9C8', '#FF7DFF', '#D881ED', '#B7B7FF',
        '#A6DEEE', '#CFE7E2', '#FFC8C8', '#F4CAD6', '#FFA8FF', '#EFCDF8',
        '#C6C6FF', '#C0E7F3', '#DCEDEA', '#FFEAEA', '#F8DAE2', '#FFC4FF',
        '#EFCDF8', '#DBDBFF', '#D8F0F8', '#E7F3F1', '#FFEAEA', '#FAE7EC',
        '#FFE3FF', '#F8E9FC', '#EEEEFF', '#EFF9FC', '#F2F9F8', '#FFFDFD',
        '#FEFAFB', '#FFFDFF', '#FFFFFF', '#FDFDFF', '#FAFDFE', '#F7FBFA'];

  var Sigma = {

    init: function() {
      var that = this;
      // Nodes and edges.
      var sylv_nodes = sylva.nodes;
      var sylv_edges = sylva.edges;
      // Node info.
      var $tooltip;
      // Graph size.
      var size = sylva.size;
      // Objects for play with them for show and hide nodes.
      var nodesInTypes = {};  // Group the nodes by type.
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

      // Add nodes and create colors.
      for (var n in sylv_nodes) {
        type = sylv_nodes[n].type;
        if (!(type in nodesInTypes)) {
          nodesInTypes[type] = {};
        }
        nodesInTypes[type][n] = "";
        if (!(type in sylva.colors)) {
          sylva.colors[type] = colors[Object.keys(sylva.colors).length];
        }
        sigInst.addNode(n, {
          x: Math.random(),
          y: Math.random(),
          color: sylva.colors[type]
        });
      }

      // Add edges.
      for (var e in sylv_edges) {
        sigInst.addEdge(sylv_edges[e].id, sylv_edges[e].source, sylv_edges[e].target);
      }

      // Create the legend.
      sylva.colors["notype"] = colors[Object.keys(sylva.colors).length];
      $('#node-type-legend').empty();
      var list = $('#node-type-legend').append($('<ul>'));
      list.css({
        listStyleType: 'none',
        marginTop: "5px"
      });
      $.each(sylva.colors, function(type, color) {
        if (type !== "notype") {
          list.append($('<li>')
            .css({
              minHeight: "20px",
              paddingLeft: "3px"
            })
            .append($('<i>')
              .addClass("icon-eye-open")
              .addClass("show-hide-nodes")
              .attr("data-action", "hide")
              .attr("data-nodetype", type)
              .css({
                paddingRight: "3px",
                width: "1em",
                height: "1em",
                cursor: "pointer",
                verticalAlign: "-2px"
              }))
            .append($('<span>')
              .css({
                backgroundColor: color,
                display: "inline-block",
                width: "16px",
                height: "16px",
                verticalAlign: "middle"
              }))
            .append($('<span>')
              .css({
                paddingLeft: "0.3em",
                verticalAlign: "middle"
              })
              .text(type)
            )
          );
        }
      });

      // Show node info and hide the rest of nodes and edges.
      sigInst.bind('overnodes', function(event) {
        var nodes = event.content;
        var nodePK = nodes[0];  // node primary key
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
          sigInst.iterNodes(function(node) {
            $tooltip =
              $('<div class="node-info"></div>')
                .append('<ul>' + attributesToString(sylv_nodes[nodePK]) + '</ul>')
                .css({
                  'left': node.displayX+212,
                  'top': node.displayY+61
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
        sylva.Utils.updateNodeLegend(sylv_nodes[nodePK].id, nodePK, 'element-info');

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
        var type = $(this).attr('data-nodetype');
        var action = $(this).attr('data-action');
        if (action == "hide") {
          $(this).attr('data-action', 'show');
          $(this).removeClass('icon-eye-open');
          $(this).addClass('icon-eye-close');
          sigInst.iterNodes(function(n) {
            n.hidden = true;
          }, Object.keys(nodesInTypes[type])).draw();
          // Adding the nodes to a dictionary to know which nodes hide in the "overnodes" event.
          $.extend(nodesHidden, nodesInTypes[type]);
        } else {
          $(this).attr('data-action', 'hide');
          $(this).removeClass('icon-eye-close');
          $(this).addClass('icon-eye-open');
          sigInst.iterNodes(function(n) {
            n.hidden = false;
          }, Object.keys(nodesInTypes[type])).draw();
          // Deleting the nodes from a dictionary to know which nodes hide in the "overnodes" event.
          $.each(nodesInTypes[type], function(key, value) {
            delete nodesHidden[key];
          });
        }
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
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
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
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
      });

      // Handle the fullscreen changes.
      function handleFullscreen() {
        if(isFullscreenByButton) {
          isFullscreenByButton = false;
          stopFullscreen();
        } else {
          isFullscreenByButton = true;
          goFullscreen();
        }
      }

      // Update some sizes in fullscreen mode.
      function updateSizes() {
          var height = $(window).height();
          var width = $(window).width();

          $('header').width(width);
          $('#main').width(width);
          $('div.inside.clearfix').width(width);
          $('#body').width(width);

          var trueHeaderHeight =  $('div.inside.clearfix').height();
          $('#body').height(height - trueHeaderHeight);

          // The new height will be: screenHeight - header - whiteSpace - (border + padding from canvasInfo) - whiteSpace
          $('#canvas-info').height(height - 103);

          $('.graph-controls').css({marginRight: "40px"});
          $('#sigma-wrapper').css({marginRight: "40px"});

          // The new width will be: screenWidth - leftWhiteSpace - canvasInfo- rightWhiteSpace - sigmaWrapperBorder - (safeSpace between canvasInfo and canvas)
          $('#sigma-wrapper').width(width - 248);

          // The new height will be: screenHeight - header - whiteSpace - graphControls - (border + padding from canvasInfo) - whiteSpace
          $('#sigma-wrapper').height(height - 133);

          var top = height - 101;
          var left = width - 52;
          $('#sigma-pause').css({top: top + "px", left: left + "px"});

          sigInst.resize();
      }

      // Restore some size when exit fullscreen mode.
      function restoreSizes() {
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

      // Perform the 'real' fullscreen action.
      function goFullscreen() {
        $('#sigma-go-fullscreen').hide();
        $('nav.main li').hide();
        $('header.global h2').hide();
        $('nav.menu').hide();
        $('div.graph-item').hide();
        $('div#footer').hide();
        $('#link-logo').bind('click', false);
        $('#link-logo').addClass('disabled');
        linkLogo = $('#link-logo').attr('href');
        $('#link-logo').removeAttr('href');

        $('.title-graph-name').show();
        $('#sigma-exit-fullscreen').parent().show();

        updateSizes();

        $(window).on('resize', updateSizes);
      }

      // Perform the cancelation of the fullscreen mode.
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
        restoreSizes();
      }

      // Listeners for handle the "fullscreen" events.
      $(document).on('fullscreenchange', handleFullscreen);
      $(document).on('mozfullscreenchange', handleFullscreen);
      $(document).on('webkitfullscreenchange', handleFullscreen);
      $(document).on('MSFullscreenChange', handleFullscreen);

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
