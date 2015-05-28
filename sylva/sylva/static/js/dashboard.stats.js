(function ($) {

  var sizeFormat = function(bytecount) {
    var str = bytecount+' B';
    if (Number(bytecount) > 1000) { str = (bytecount/1000).toFixed(2)+' kB'; }
    if (Number(bytecount) > 1000000) { str = (bytecount/1000000).toFixed(2)+' MB'; }
    if (Number(bytecount) > 1000000000) { str = (bytecount/1000000000).toFixed(2)+' GB'; }
    if (Number(bytecount) > 1000000000000) { str = (bytecount/1000000000000).toFixed(2)+' TB'; }
    return str;
  };

  var init = function() {
    var labels = [];
    var nodes = [];
    var relationships = [];
    var storages = [];
    var storagesValues = [];

    // We declare the array types
    var seriesOwned = {};
    seriesOwned.data = new Array();
    var seriesCollaboration = {};
    seriesCollaboration.data = new Array();

    $("input[type=\"hidden\"].stats-series").each(function (e) {
      var serie = JSON.parse($(this).val());
      if (serie.nodes + serie.relationships > 0) {
          var values = {};
          values.x = serie.nodes;
          values.y = serie.relationships;
          values.z = serie.storage;
          values.name =  serie.title;
          type = serie.type;
          if(type == "owned") {
            // Values
            seriesOwned.data.push(values);
          } else {
            // Values
            seriesCollaboration.data.push(values);
          }
          labels.push(serie.title +" ("+ sizeFormat(serie.storage) +")");
          nodes.push(serie.nodes);
          relationships.push(serie.relationships);
          storages.push(serie.storage);
      }
    });

    $('#dashboardStats').highcharts({
      chart: {
        type: 'bubble',
        zoomType: 'xy'
      },
      title: {
        text: ''
      },
      xAxis: {
        title: {
          text: gettext('Nodes')
        }
      },
      yAxis: {
        title: {
          text: gettext('Relationships')
        }
      },
      tooltip: {
        formatter: function() {
          return gettext('Nodes') + ': ' + this.point.x + ', ' + gettext('Relationships') + ': ' + this.point.y + ', ' + gettext('Size') + ': ' + this.point.z;
        }
      },
      plotOptions: {
        series: {
          dataLabels: {
            useHTML: true,
            enabled: true,
            y: 30,
            formatter:function() {
                return '<span class="datalabel" style="text-shadow: none;">' + this.point.name + '</div>';
            },
            style: {
              color:"#348E82"
            }
          }
        }
      },
      series: [{
        name: gettext('Owned'),
        data: seriesOwned.data
      }, {
        name: gettext('Collaboration'),
        data: seriesCollaboration.data
      }]
    });
  };
  $(document).ready(init);
})(jQuery.noConflict());
