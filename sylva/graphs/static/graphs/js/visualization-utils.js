// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true,
gettext */


/****************************************************************************
 * Visualization utils
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var Utils = {

    // Update node legend frame.
    updateNodeLegend: function(nodeId, nodeTitle, domId, html) {
      var htmlContent = (typeof html === "undefined") ? '' : html;
      var nodeEditURL = sylv.nodeEditURL.replace(/nodes\/0\/edit/, 'nodes/' + nodeId + '/edit');
      var title = (nodeTitle.length < 22) ? nodeTitle : nodeTitle.substring(0,18) + "...";
      $('#' + domId).html(
        '<h2 title="' + nodeTitle + '">' + title + '</h2>' +
        '<a href="' + sylv.graphViewURL + 'nodes/' + nodeId + '">' +
          '<i class="icon-connections16"></i> ' + gettext('View related nodes') +
        '</a>' +
        '<br>' +
        '<a href="' + nodeEditURL + '">' +
          '<i class="icon-nodes16"></i> ' + gettext('View node data') +
        '</a>' +
        '<br>' +
        '<a href="' + nodeEditURL + '">' +
          '<i class="icon-edit-node16"></i> ' + gettext('Edit node data') +
        '</a>'
      ).append(htmlContent);
    }

  };

  // Reveal module.
  window.sylv.Utils = Utils;

})(sylv, jQuery, window, document);
