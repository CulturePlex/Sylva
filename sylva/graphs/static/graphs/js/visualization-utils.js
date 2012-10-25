// JSHint options

/*global window:true, document:true, setTimeout:true, console:true, jQuery:true,
sylv:true, prompt:true, alert:true, FileReader:true, Processing:true, sigma:true */


/****************************************************************************
 * Visualization utils
 ****************************************************************************/

;(function(sylv, $, window, document, undefined) {

  var Utils = {

    // Update node legend frame.
    updateNodeLegend: function(nodeId, nodeTitle, domId, html) {
      htmlContent = (typeof html === "undefined") ? '' : html;
      var nodeEditURL = sylv.nodeEditURL.replace(/nodes\/0\/edit/, 'nodes/' + nodeId + '/edit');
      var title = (nodeTitle.length < 22) ? nodeTitle : nodeTitle.substring(0,18) + "...";
      $('#' + domId).html(
          '<a href="' + sylv.graphViewURL + 'nodes/' + nodeId + '" title="' + nodeTitle + '">' +
            '<h2>' + title + '</h2>' +
          '</a>' +
          '<a href="' + nodeEditURL + '">Edit node</a>'
      ).append(htmlContent);
    }

  };

  // Reveal module.
  window.sylv.Utils = Utils;

})(sylv, jQuery, window, document);
