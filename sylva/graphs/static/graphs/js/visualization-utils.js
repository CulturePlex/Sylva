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
    updateNodeLegend: function(nodeId, nodeTitle, domId, html) {
      var htmlContent = (typeof html === "undefined") ? '' : html;
      var nodeEditURL = sylva.nodeEditURL.replace(/nodes\/0\/edit/, 'nodes/' + nodeId + '/edit');
      var nodeViewURL = sylva.nodeViewURL.replace(/nodes\/0\/view/, 'nodes/' + nodeId + '/view');
      var title = (nodeTitle.length < 22) ? nodeTitle : nodeTitle.substring(0,16) + "...";
      if ($("#content3").length > 0) { // Checkg that we are in a node vie page
        graphViewLink = ''
      } else {
        graphViewLink = '<a href="' + sylva.graphViewURL + 'nodes/' + nodeId + '">' +
          '<i class="sylva-icon-connections16"></i> ' + gettext('View related nodes') +
        '</a>' +
        '<br>'
      }
      $('#' + domId).html(
        '<h2 title="' + nodeTitle + '" style="font-size: 18px;">' + title + '</h2>' +
        graphViewLink +
        '<a href="' + nodeViewURL + '">' +
          '<i class="sylva-icon-nodes16"></i> ' + gettext('View node data') +
        '</a>' +
        '<br>' +
        '<a href="' + nodeEditURL + '">' +
          '<i class="sylva-icon-edit-node16"></i> ' + gettext('Edit node data') +
        '</a>'
      ).append(htmlContent);
    }

  };

  // Reveal module.
  window.sylva.Utils = Utils;

})(sylva, jQuery, window, document);
