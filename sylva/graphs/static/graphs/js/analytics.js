// Variable to store the ids to plot the results of the analytics
var analyticsName = {
  "connected_components": gettext("Connected components"),
  "triangle_counting": gettext("Triangle counting"),
  "graph_coloring": gettext("Graph coloring"),
  "betweenness_centrality": gettext("Betweenness centrality"),
  "pagerank": gettext("Pagerank"),
  "kcore": gettext("Degeneracy (k-core)")
};

// Variable to store the text to plot the x axis
var analyticsAxis = {
  "connected_components": gettext("Connected components"),
  "triangle_counting": gettext("Triangles"),
  "graph_coloring": gettext("Colors"),
  "betweenness_centrality": gettext("Betweenness centrality"),
  "pagerank": gettext("Pagerank"),
  "kcore": gettext("Degeneracy (k-core)")
};

// Variable to store the text to plot in the pie charts
var analyticsPieSubtitle = {
  "connected_components": gettext("connected components"),
  "graph_coloring": gettext("colors"),
}

// Variable to store the analytics that actually are executing
var analyticsExecuting = new Array();

var analyticsId = {};
var taskTime = 0;

var initAnalytics = function($) {
  /**
   * AJAX Setup for CSRF Django token
   */

  /* Variable for get the nodes implied on an analytic. It's here for control
   * the data flux when the user request another dump before the last one
   * gets fully showed. The next one control when to stop the drawing of a
   * previous dump.
   */
  var nodeStreaming = null;
  var drawingTasks = [];

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

  var getHighchartsOptions = function(option, algorithm, parentArray) {
    var highchartsOptions = "";
    if(option == "scatter") {
      highchartsOptions = {
        chart: {
          renderTo: analyticsId[algorithm],
          type: 'scatter'
        },
        title: {
          text: analyticsName[algorithm]
        },
        xAxis: {
          title: {
            text: analyticsAxis[algorithm]
          }
        },
        yAxis: {
          title: {
            text: 'Nodes'
          }
        },
        plotOptions: {
          scatter: {
            marker: {
              radius: 5,
              states: {
                hover: {
                  enabled: true,
                  lineColor: 'rgb(100,100,100)'
                }
              }
            },
            states: {
              hover: {
                marker: {
                  enabled: false
                }
              }
            },
            tooltip: {
              headerFormat: '',
              pointFormat: '{point.y} with {point.x} ' + analyticsAxis[algorithm] + ''
            },
            point: {
              events: {
                mouseOver: function () {
                    alert(this.x);
                }
              }
            }
          }
        },
        series: [{
          showInLegend: false,
          color: 'rgba(223, 83, 83, .5)',
          data: parentArray
        }]
      };
    } else if (option == "pie") {
      highchartsOptions = {
        chart: {
          renderTo: analyticsId[algorithm],
          plotBackgroundColor: null,
          plotBorderWidth: 1,
          plotShadow: false
        },
        title: {
          text: analyticsName[algorithm]
        },
        subtitle: {
          text: "Set of " + analyticsPieSubtitle[algorithm] + " of the graph"
        },
        tooltip: {
          headerFormat: '',
          showInLegend: false,
          pointFormat: '{series.name}: <b>{point.y}</b>'
        },
        plotOptions: {
          pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
              enabled: true,
              format: '{point.percentage:.1f}% ' + gettext("of nodes"),
                style: {
                  color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                }
            },
            point: {
              events: {
                mouseOver: function () {
                    alert(this.x);
                }
              }
            }
        }
        },
        series: [{
          type: 'pie',
          showInLegend: false,
          name: 'Number of nodes',
          data: parentArray
        }]
      };
    }

    return highchartsOptions;
  };

  // get results of the analytic
  var getResults = function(results_url, algorithm, analyticId, analyticTaskStart) {
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: results_url,
      success: function (data) {
        var chartType = "";
        var parentArray = new Array();
        var highchartPieOption = algorithm == "connected_components" ||
                                 algorithm == "graph_coloring";
        if(highchartPieOption) {
          chartType = "pie";
          for(var i in data) {
            var childArray = new Array();
            childArray.push(parseFloat(i));
            childArray.push(data[i]);
            parentArray.push(childArray);
          }
        } else {
          chartType = "scatter";
          for(var i in data) {
            var childArray = new Array();
            childArray.push(parseFloat(i));
            childArray.push(data[i]);
            parentArray.push(childArray);
          }
        }

        // Create the chart
        optionsScatter = getHighchartsOptions(chartType, algorithm, parentArray);
        var chart = new Highcharts.Chart(optionsScatter);

        // We hide the estimated time and the progress bar
        etaId = '#' + algorithm +"-eta";
        progressBarId = '#progress-bar-' + algorithm;
        $(etaId).html("");
        $(progressBarId).css({
          "display": "none"
        });
        $(progressBarId).attr('value', 0);

        if(analyticId != "") {
          selectAnalyticsId = '#last-analytics-' + algorithm;
          $(selectAnalyticsId).prepend("<option value=" + analyticId + " selected>" + gettext(moment.duration(-1, "seconds").humanize(true)) + "</option>");
          $(selectAnalyticsId).css({
            'display': 'inline-block'
          });
        }
      },
      error: function (e) {
          alert("Error: " + e);
      }
    });
  };

  // pole state of the current task
  var getTaskState = function(analyticsExecuting, progressBarId) {
    progressBarMax = $(progressBarId).attr('max');
    analyticsRequest = JSON.stringify(analyticsExecuting);
    $.ajax({
      type: "GET",
      url: sylva.urls.analyticsStatus,
      data: {"analytics_request": analyticsRequest}
    }).done(function(analyticsResults){
      // If we have finished analytics, we show them
      for(key in analyticsResults) {
        if(analyticsResults.hasOwnProperty(key)) {
          resultsUrl = analyticsResults[key][0];
          analyticId = analyticsResults[key][1];
          analyticTaskStart = analyticsResults[key][2];
          algorithm = analyticsResults[key][3];
          getResults(resultsUrl, algorithm, analyticId, analyticTaskStart);
          $(progressBarId).attr('value', 100);
          // We remove the element of the list of analytics executing
          var index = analyticsExecuting.indexOf(key);
          if(index > -1)
            analyticsExecuting.splice(index, 1);
          // If we dont have more analytics executing, we reset the time for the progress bars
          if(analyticsExecuting.length == 0)
            taskTime = 0;
        }
      }
      if(analyticsExecuting.length > 0) {
        // We ask for the analytics until all of them are finished
        window.setTimeout(function() {
          getTaskState(analyticsExecuting, progressBarId);
        }, 1000);
        if(taskTime < progressBarMax) {
          taskTime = taskTime + 7;
          $(progressBarId).attr('value', taskTime);
        }
      }
      // create the infinite loop of Ajax calls to check the state
      // of the current task
    });
  }

  $('.play-algorithm').on('click', function() {
    var $this = $(this);
    var measure = $this.data('measure');
    var plotId = $this.data('plot');
    var etaId = $this.data('eta');
    var progressBarId = "#progress-bar-" + measure;

    // We check if we have to apply the algorithm over a subgraph
    var inputSelected = $this.next().children()[0];
    var checked = $(inputSelected).attr('checked');
    var isVisible = $(inputSelected).is(':visible');

    if((checked == 'checked') && isVisible) {
      var subgraph = JSON.stringify(sylva.selectedNodes);
    }

    analyticsId[measure] = plotId;
    $('#' + etaId).html(gettext("Estimating time"));

    jQuery.ajax({
      type: "POST",
      url: sylva.urls.analyticsEstimate,
      data: {"algorithm": measure}
    }).done(function(data){
      var algorithm = data[0];
      var etaTime = data[1];
      if(etaTime < 10) {
        $(progressBarId).attr('max', 100);
      } else {
        $(progressBarId).attr('max', 300);
      }
      $('#' + etaId).html(gettext("Estimated time ") + etaTime.toFixed(2) + gettext(" seconds"));
      jQuery.ajax({
        type: "POST",
        url: sylva.urls.analyticsRun,
        data: {
          "algorithm": measure,
          "subgraph": subgraph
        }
      }).done(function(data) {
        var taskId = data[0];
        var algorithm = data[1];
        analyticsExecuting.push(taskId);
        getTaskState(analyticsExecuting, progressBarId);
        $(progressBarId).css({
          'display': 'inline-block'
        });
      });
    });
  });

  $('.analytics-measure').accordion({
    collapsible: true,
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
    active: false,
    heightStyle: 'content'
  });

  $(document).on('change', '.last-analytics', function() {
    /* This lines will stop the drawing tasks (of a previous streaming) that
     * still are waiting being executed.
     */
    for (var i = 0; i < drawingTasks.length; i++) {
      clearTimeout(drawingTasks[i]);
    }
    drawingTasks = [];

    // Stopping the streaming if the previous one is still running.
    if (nodeStreaming != null) {
      nodeStreaming.close();
      nodeStreaming.onmessage = function() {};
      nodeStreaming = null;
    }

    var $this = $(this);
    var analyticId = $('option:selected', $this).val();

    $.ajax({
      type: "GET",
      url: sylva.urls.analyticsAnalytic,
      data: {"id": analyticId}
    }).success(function(result){
      var resultsUrl = result[0];
      var algorithm = result[1];

      // We check if we have defined the id for render highcharts
      if(!analyticsId[algorithm]) {
        analyticsId[algorithm] = algorithm + "-results";
      }

      console.log(resultsUrl);
      console.log(algorithm);
      getResults(resultsUrl, algorithm, "", "");

      /* A function for update the selected nodes in the graph using the
       * analytic implied nodes.
       */
      var updateGraph = function(data) {
        if (data == null) {
          sylva.selectedNodes = [];
        } else {
          sylva.selectedNodes.push.apply(sylva.selectedNodes, data);
        }
        sylva.Sigma.grayfyNonListedNodes(sylva.selectedNodes);
      };

      // Draw no nodes.
      updateGraph(null);
      var returnedNodes = [];
      var sliceSize = 20;

      // Getting the implied nodes.
      nodeStreaming = new EventSource(
        sylva.urls.analtyicsDump + '?id=' + analyticId);

      nodeStreaming.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var drawNodes = false;

        // Draw nodes only when it has 10 in the "buffer".
        if (data != 'close') {
          returnedNodes.push(data);
          if (returnedNodes.length >= sliceSize) {
            drawNodes = true;
          }

        // Stop the streaming and drow the nodes in the "buffer".
        } else {
          nodeStreaming.close();
          nodeStreaming.onmessage = function() {};
          nodeStreaming = null;
          if (returnedNodes.length > 0) {
            drawNodes = true;
          }
        }

        if (drawNodes) {
          // This wrap is used for take "copy" of the returnedNodes object.
          (function(returnedNodes) {
            var task = setTimeout(function () {
              updateGraph(returnedNodes);
            }, 0);

            drawingTasks.push(task); // Saving the task for stop if is needed.
          })(returnedNodes);

          returnedNodes = [];
        }
      };

    });
  });

  $('#analytics-algorithms').sortable();

  sylva.reactor.addEventListener('subgraphSelected', function() {
    $('.div-selected-nodes').css(
      {'display':'inline'}
    );
  });
};
