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

// Varieble to store the ids to render the charts
var analyticsId = {
  "connected_components": "connected_components-results",
  "triangle_counting": "triangle_counting-results",
  "graph_coloring": "graph_coloring-results",
  "betweenness_centrality": "betweenness_centrality-results",
  "pagerank": "pagerank-results",
  "kcore": "kcore-results"
};

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
  sylva.listClickNodes = [];

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
            allowPointSelect: true,
            marker: {
              radius: 5,
              states: {
                hover: {
                  enabled: true,
                  lineColor: 'rgb(100,100,100)'
                },
                select: {
                  fillColor: 'rgb(255,0,0)',
                  lineWidth: 1
                }
              }
            },
            tooltip: {
              headerFormat: '',
              pointFormat: '{point.y} with {point.x} ' + analyticsAxis[algorithm] + ''
            },
            point: {
              events: {
                mouseOver: function() {
                  var id = this.x, sylvaList;
                  if(id in sylva.analyticAffectedNodes) {
                    sylvaList = sylva.analyticAffectedNodes[id].map(String);
                    sylva.Sigma.changeSigmaTypes("aura", sylvaList);
                  } else {
                    // We have an error and do nothing
                    console.log("There's an error highlighting the nodes");
                  }
                },
                mouseOut: function() {
                  var point = this;
                  if(!point.selected) {
                    sylva.Sigma.cleanSigmaTypes();
                    // If we had selected nodes, we keep the aura
                    if(sylva.listClickNodes.length > 0) {
                      sylva.Sigma.changeSigmaTypes("aura", sylva.listClickNodes);
                    }
                  }
                },
                click: function() {
                  var point = this;
                  sylva.Sigma.cleanSigmaTypes();
                  if(!point.selected) {
                    var id = this.x, sylvaList;
                    if(id in sylva.analyticAffectedNodes) {
                      sylvaList = sylva.analyticAffectedNodes[id].map(String);
                      sylva.Sigma.changeSigmaTypes("aura", sylvaList);
                    } else {
                      sylva.listClickNodes = [];
                      console.log("There's an error highlighting nodes on click");
                    }
                    // We store the list of nodes
                    sylva.listClickNodes = sylvaList;
                  } else {
                    // We reset the list of nodes
                    sylva.listClickNodes = [];
                  }
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
                mouseOver: function() {
                  var id = this.x, sylvaList;
                  if(id in sylva.analyticAffectedNodes) {
                    sylvaList = sylva.analyticAffectedNodes[id].map(String);
                    sylva.Sigma.changeSigmaTypes("aura", sylvaList);
                  } else {
                    // We have an error and do nothing
                    console.log("There's an error highlighting the nodes on point over");
                  }
                },
                mouseOut: function() {
                  var point = this;
                  if(!point.selected) {
                    sylva.Sigma.cleanSigmaTypes();
                    // If we had selected nodes, we keep the aura
                    if(sylva.listClickNodes.length > 0) {
                      sylva.Sigma.changeSigmaTypes("aura", sylva.listClickNodes);
                    }
                  }
                },
                click: function() {
                  var point = this;
                  if(!point.selected) {
                    var id = this.x, sylvaList;
                    if(id in sylva.analyticAffectedNodes) {
                      sylvaList = sylva.analyticAffectedNodes[id].map(String);
                      sylva.Sigma.changeSigmaTypes("aura", sylvaList);
                    } else {
                      sylvaList = [];
                      console.log("There's an error highlighting the nodes on point click");
                    }
                    // We store the list of nodes
                    sylva.listClickNodes = sylvaList;
                  } else {
                    sylva.Sigma.cleanSigmaTypes();
                    // We reset the list of nodes
                    sylva.listClickNodes = [];
                  }
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
  var getResults = function(resultsUrl, algorithm, analyticId, analyticTaskStart, valuesUrl) {
    $.ajax({
      type: "GET",
      dataType: 'json',
      url: resultsUrl,
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

        optionsScatter = getHighchartsOptions(chartType, algorithm, parentArray);

        // Here, we need to catch the exception if the analytic is running
        // right now or it was running before. In that case, we save the
        // attributes in localStorage to load them when we enter in
        // fullscreen mode
        // Create the chart
        try {
          // This is the regular case
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
            // We remove the running option or the choose one
            $('option[value="running"]', selectAnalyticsId).remove();
            $('option[value="default"]', selectAnalyticsId).remove();
            // We add the new analytic
            $(selectAnalyticsId).prepend("<option value=" + analyticId + " selected>" + gettext(moment.duration(-1, "seconds").humanize(true)) + "</option>");
            // We add the default option
            $(selectAnalyticsId).prepend("<option value='default' disabled>" + gettext('Choose one') + "</option>");
            // We remove the disabled attribute of the select
            $(selectAnalyticsId).prop('disabled', false);
            $(selectAnalyticsId).css({
              'display': 'inline-block'
            });
          }

          // We get the values data
          $.ajax({
            type: "GET",
            dataType: 'json',
            url: valuesUrl,
            success: function(data) {
              var sylvaKey;
              sylva.analyticAffectedNodes = {}
              for(var key in data) {
                if(data.hasOwnProperty(key)) {
                  sylvaKey = parseFloat(key);
                  sylva.analyticAffectedNodes[sylvaKey] = data[key];
                }
              }
            },
            error: function(e) {
              alert("Error: " + e);
            }
          });

          // We remove the values in localStorage
          localStorage.clear()
        } catch(e) {

        }
      },
      error: function (e) {
        alert("Error: " + e);
      }
    });
  };

  // pole state of the current task
  var getTaskState = function(analyticsExecuting, progressBarId) {
    // We store the analyticsExecuting in case that
    // we navigate to another view or refresh the page
    localStorage.setItem("analyticsExecuting", analyticsExecuting);
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
          // We get the status: OK or REVOKED
          analyticStatus = analyticsResults[key][0]
          if(analyticStatus == 'OK') {
            resultsUrl = analyticsResults[key][1];
            analyticId = analyticsResults[key][2];
            analyticTaskStart = analyticsResults[key][3];
            algorithm = analyticsResults[key][4];
            valuesUrl = analyticsResults[key][5];

            // We show the play button
            $('#' + algorithm + ' .play-algorithm').css('visibility', 'visible');

            // We hide the stop button
            $('#stop-analytic-' + algorithm).css('visibility', 'hidden');

            getResults(resultsUrl, algorithm, analyticId, analyticTaskStart, valuesUrl);
          }

          $(progressBarId).attr('value', 100);
          // We remove the element of the list of analytics executing
          var index = analyticsExecuting.indexOf(key);
          if(index > -1)
            analyticsExecuting.splice(index, 1);
          // If we dont have more analytics executing, we reset the time for the progress bars
          if(analyticsExecuting.length == 0)
            taskTime = 0;

          // We remove the analytic of the localStorage array
          analyticsExecutingStored = localStorage.getItem('analyticsExecuting');
          analyticsExecutingSplitted = analyticsExecutingStored.split(',');
          var index = analyticsExecutingSplitted.indexOf(key);
          if(index > -1) {
            analyticsExecutingSplitted.splice(index, 1);
            localStorage.removeItem(key);
            // We update the local storage analytics array
            localStorage.setItem('analyticsExecuting', JSON.stringify(analyticsExecutingSplitted));
          }
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
    });
  }

  $('.play-algorithm').on('click', function() {
    var $this = $(this);
    var measure = $this.data('measure');
    var plotId = $this.data('plot');
    var etaId = $this.data('eta');
    var progressBarId = "#progress-bar-" + measure;
    var stopAnalyticId = "#stop-analytic-" + measure;

    // We check if we have to apply the algorithm over a subgraph
    var inputSelected = $this.next().children()[0];
    var checked = $(inputSelected).attr('checked');
    var isVisible = $(inputSelected).is(':visible');

    if((checked == 'checked') && isVisible) {
      var subgraph = JSON.stringify(sylva.selectedNodes);
    }

    //analyticsId[measure] = plotId;
    $('#' + etaId).html(gettext("Estimating time"));

    jQuery.ajax({
      type: "POST",
      url: sylva.urls.analyticsEstimate,
      data: {"algorithm": measure}
    }).done(function(data){
      var algorithm = data[0];
      var etaTime = data[1];

      // We remove the value attribute of the progress bar to simulate
      // the infinite bar
      $(progressBarId).removeAttr("value");
      $(progressBarId).removeClass("progress");
      $(progressBarId).css({
        'display': 'inline-block',
        'height': '18px',
        'width': '198px'
      });
      $(progressBarId).attr('max', 300);

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
        var graph = data[2];

        $(stopAnalyticId).attr('data-taskid', taskId);

        // We hide the play button
        $('#' + measure + ' .play-algorithm').css('visibility', 'hidden');
        // We show the stop analytic button
        $(stopAnalyticId).css('visibility', 'visible');

        // We add the info of the analytic running to the select
        selectAnalyticsId = '#last-analytics-' + algorithm;
        // We get the choose one option
        var defaultOption = $('option[value="default"]', selectAnalyticsId);
        // We remove the default option
        $('option[value="default"]', selectAnalyticsId).remove();
        // We add the new analytic
        $(selectAnalyticsId).prepend("<option value='running' selected>(" + gettext("running") + ")</option>");
        // We set the select to disable
        $(selectAnalyticsId).prop('disabled', 'disabled');

        analyticsExecuting.push(taskId);

        // We store the algorithm of the taskId in case that we need to
        // navigate to another view or refresh the page
         // We also store the graph, because we need to take care if we
        // navaigate to another graph
        var algorithmAndGraph = Array(algorithm, graph);
        localStorage.setItem(taskId, JSON.stringify(algorithmAndGraph));
        $(progressBarId).addClass("progress");
        getTaskState(analyticsExecuting, progressBarId);
      });
    });
  });

  $('.stop-analytic').on('click', function() {
    $this = $(this);
    var analyticTaskId = $this.attr('data-taskid');

    if(analyticTaskId != '') {
      $.ajax({
        type: "POST",
        url: sylva.urls.analyticsStop,
        data: {"task_id": analyticTaskId}
      }).done(function(data){
        // Data contains the analytic id and the algorithm
        analyticId = data[0];
        algorithm = data[1];

        // We need to add the analytic to the select, info for the user
        selectAnalyticsId = '#last-analytics-' + algorithm;
        // We enable the select field
        $(selectAnalyticsId).prop('disabled', false);
        // We remove the running option
        $('option[value="running"]', selectAnalyticsId).remove();
        // We add the new analytic
        $(selectAnalyticsId).prepend("<option value='" + analyticId +"' selected disabled>" + gettext("Stopped analytic") + "</option>");
        // We add again the default option
        $(selectAnalyticsId).prepend("<option value='default' disabled>" + gettext("Choose one") + "</option>");

        // We show the play button
        $('#' + algorithm + ' .play-algorithm').css('visibility', 'visible');
        // We hide the stop button
        stopAnalyticId = '#stop-analytic-' + algorithm;
        $(stopAnalyticId).css('visibility', 'hidden');

        // We hide the progress bar
        progressBarId = '#progress-bar-' + algorithm;
        $(progressBarId).css('display', 'none');

        // We remove the analytic of the localStorage array
        analyticsExecutingStored = localStorage.getItem('analyticsExecuting');
        analyticsExecutingSplitted = analyticsExecutingStored.split(',');
        var index = analyticsExecutingSplitted.indexOf(analyticTaskId);
        if(index > -1) {
          analyticsExecutingSplitted.splice(index, 1);
          localStorage.removeItem(analyticTaskId);
          // We update the local storage analytics array
          localStorage.setItem('analyticsExecuting', JSON.stringify(analyticsExecutingSplitted));
        }
      });
    }
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
      var valuesUrl = result[2];

      // We check if we have defined the id for render highcharts
      if(!analyticsId[algorithm]) {
        analyticsId[algorithm] = algorithm + "-results";
      }

      getResults(resultsUrl, algorithm, "", "", valuesUrl);

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

  sylva.reactor.addEventListener('entireGraphSelected', function() {
    // We restore the checkbox checked before hide it
    $('.div-selected-nodes input').attr('checked', 'checked')
    $('.div-selected-nodes').css(
      {'display':'none'}
    );
  });

  // When the document is loaded, we check if we have some analytic running
  $(document).ready(function() {
    // Let's get the graph to check if the analytics belong to it
    var graphName = sylva.urls.viewGraphAjax;
    graphName = graphName.split('/')[2];

    analyticsExecutingStored = localStorage.getItem('analyticsExecuting');

    if(analyticsExecutingStored != null &&
       analyticsExecutingStored != '') {
      // We need to split the string stored
      analyticsExecutingSplitted = analyticsExecutingStored.split(',');

      // We iterate over the analytics that are running to format the selects
      // and all the analytics side
      index = 0;
      var analyticsLength = analyticsExecutingSplitted.length;
      while(index < analyticsLength) {
        // We get the task id
        var taskId = analyticsExecutingSplitted[index];
        // We get the algorithm and the graph
        var algorithmAndGraph = localStorage.getItem(taskId);
        var algorithm = JSON.parse(algorithmAndGraph)[0];
        var graph = JSON.parse(algorithmAndGraph)[1];

        if(graph == graphName) {
          var stopAnalyticId = "#stop-analytic-" + algorithm;
          $(stopAnalyticId).attr('data-taskid', taskId);

          // We show the stop analytic button
          $(stopAnalyticId).css('visibility', 'visible');
          // We add the info of the analytic running to the select
          selectAnalyticsId = '#last-analytics-' + algorithm;
          // We get the choose one option
          var defaultOption = $('option[value="default"]', selectAnalyticsId);
          // We remove the default option
          $('option[value="default"]', selectAnalyticsId).remove();
          // We add the new analytic
          $(selectAnalyticsId).prepend("<option value='running' selected>(" + gettext("running") + ")</option>");
          // We set the select to disable
          $(selectAnalyticsId).prop('disabled', 'disabled');


          var progressBarId = '#progress-bar-' + algorithm;
          $(progressBarId).attr('max', 300);

          // We remove the value attribute of the progress bar to simulate
          // the infinite bar
          $(progressBarId).removeAttr("value");
          $(progressBarId).css({
            'display': 'inline-block'
          });

          getTaskState(analyticsExecutingSplitted, progressBarId);
        }

        index = index + 1;
      }
    }
  });
};
