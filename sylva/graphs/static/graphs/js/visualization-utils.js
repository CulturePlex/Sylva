// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylva:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true,
gettext */


/****************************************************************************
 * Visualization utils
 ****************************************************************************/

;(function(sylva, $, window, document, undefined) {

  var Utils = {

    // Update node legend frame.
    updateNodeLegend: function(node, selector) {
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
        '<a href="' + nodeEditURL + '">' +
          '<i class="sylva-icon-edit-node16"></i> ' + gettext('Edit node data') +
        '</a>'
      );
    },

    cleanNodeLegend: function(selector) {
      $(selector).html('');
    }

  };

  // Reveal module.
  window.sylva.Utils = Utils;

})(sylva, jQuery, window, document);
