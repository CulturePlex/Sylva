// JSHint options

/* global window:true, document:true, setTimeout:true, console:true,
 * jQuery:true, sylva:true, prompt:true, alert:true, sigma:true, clearTimeout
 */

/****************************************************************************
 * modal.js - All the function need for control the modal windows.
 ****************************************************************************/

;(function(sylva, sigma, $, window, document, undefined) {

  // The loading string for the modals, a very used resource.
  var loadingText = gettext('Loading...');
  // For some animations we need the same time that the 'fast' jQuery, 200ms.
  var fast = 200;

  var modals = {

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
    openModal: function(dialog) {
      dialog.container.fadeIn('fast');
      dialog.data.fadeIn('fast');
    },

    // The common behaviour for closing the modals.
    closeModal: function(dialog) {
      dialog.container.fadeOut('fast');
      dialog.data.fadeOut('fast');

      /* The next lines will destroy the modal instance completely and the
       * orginal data that SimpeModal saved.
       */
      setTimeout(function() {
        $.modal.close();
        $('#current-modal').remove();
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
    customTextModal: function(message, crateOverlay) {
      // Creating the HTML to show.
      var textModal = $('<div id="current-modal" style="display:none">');
      $('body').append(textModal);
      textModal.text(message);

      var modalPadding = 10;

      // The creation of the loading modal.
      if (crateOverlay) {
        that.createOverlay();
      }
      $('#' + textModal.attr('id')).modal({
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
          that.openModal(dialog);
        },
        onClose: function(dialog) {
          that.closeModal(dialog);
        },
      });
    },

    // It handles the obtainig of the HTML that the modal will show.
    prepareModal: function(url, showOverlay, preProcessHTML, preProcessHTMLOptions, onShow) {
      that.customTextModal(loadingText, showOverlay);

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
          that.showModal(data.html, preProcessHTML, preProcessHTMLOptions, onShow);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });
    },

    // It displays the HTML given by 'prepareModal'.
    showModal: function(html, preProcessHTML, preProcessHTMLOptions, onShow) {
      // Setting the form into the HTML.
      var modalHTML = $('<div id="current-modal" style="display: none;">');
      $('body').append(modalHTML);  // This line need to be executed here, so the internal JS will be executed.
      modalHTML.append(html);

      // Size variables for the modal library.
      var windowHeight = Math.max(document.documentElement.clientHeight,
          window.innerHeight || 0);
      var windowWidth = Math.max(document.documentElement.clientWidth,
          window.innerWidth || 0);
      var modalPadding = 10;

      options = {
        html: html,
        modalHTML: modalHTML,
        windowHeight: windowHeight,
        windowWidth: windowWidth,
        modalPadding: modalPadding
      };
      optionsAux = preProcessHTML(preProcessHTMLOptions);

      if (onShow == null) {
        onShow = function() {};
      }

      // Creating the modal.
      $('#' + modalHTML.attr('id')).modal({
        // Options.
        modal: true,
        escClose: false,
        focus: false,

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
          that.openModal(dialog);
        },
        onClose: function(dialog) {
          that.closeModal(dialog);
        },
        onshow: function(dialog) {
          onShow(dialog, options, optionsAux);
        }
      });
    },

    /* This function handles the 'Save' and 'Save as new' options from the
     * 'edit node modal'.
     */
    saveEditNodeModal: function(button) {
      // Obtaining the parameters.
      var url = $('#save-url').attr('data-url');
      var serializedForm = $('#edit-node-form').serialize() + '&asModal=true';

      if (button.id == 'submit-save-as-new') {
        serializedForm += '&as-new=true';
      }
    },

    /* This function handles the 'Continue' button action from the
     * 'delete node modal'.
     */
    saveDeleteNodeModal: function() {
      // Obtaining the parameters.
      var url = $('#delete-url').attr('data-url');
      var serializedForm = $('#delete-node-form').serialize() + '&asModal=true';
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
            sylva.Sigma.deleteNodeFromRequest(response.action, response.nodeId,
              response.node, response.oldRelationshipIds);
            sylva.Sigma.addNodeFromRequest(response.action, response.nodeId,
              response.node, response.relationships);
            break;

          case 'new':
            sylva.Sigma.addNodeFromRequest(response.action, response.nodeId,
              response.node, response.relationships);
            break;

          case 'delete':
            sylva.Sigma.deleteNodeFromRequest(response.action, response.nodeId,
              response.node, response.oldRelationshipIds);
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
          sylva.Sigma.redrawLayout(type, degreeOrder, order, drawHidden);
        }
      }
    },

    editNode: function(url) {

      var preProcessHTMLDelete = function(options) {
        // Removing style.
        $('#content2').css({
          minHeight: '100px',
          overflow: 'hidden'
        });
        // Binding the 'events' for the two actions.
        $('#submit-delete').attr('onclick',
          'return sylva.modals.saveDeleteNodeModal()');
        $('#submit-cancel').removeAttr('href');
        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
        });
      };

      var onShowDelete = function() {};

      options = {
        preProcessHTMLDelete: preProcessHTMLDelete,
        onShowDelete: onShowDelete
      };

      var preProcessHTMLEdit = function(options) {
        // Getting the URL for delete the node.
        var deleteUrl = $('#delete-url').attr('data-url');

        // Hidding "Add node" links.
        $('.add-node').hide();

        // Binding the 'events' for the four actions.
        $('#submit-save').attr('onclick',
          'return sylva.modals.saveEditNodeModal(this)');
        $('#submit-save-as-new').attr('onclick',
          'return sylva.modals.saveEditNodeModal(this)');
        $('#submit-delete').on('click', function() {
          $.modal.close();
          setTimeout(function() {
            that.prepareModal(deleteUrl, false, options.preProcessHTMLDelete, {}, options.onShowDelete);
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
        // Calculating the width of the form.
        var widths = scrollContent.children().map(function(){
          return $(this).outerWidth(true);
        });
        var formWidth = 0;
        $.each(widths, function() {
          formWidth += this;
        });

        return {
          contentControls: contentControls,
          scrollWrapper: scrollWrapper,
          scrollContent: scrollContent,
          formWidth: formWidth
        };
      };

      var onShowEdit = function(dialog, opitons, optionsAux) {
        // It's the content who controls the scrollbars.
        dialog.wrap.css({
          overflow: 'hidden'
        });

        /* Calculatin the height of the wrapper of the form for made it
         * scrollable.
         */
        var scrollHeigth = dialog.wrap.height() - optionsAux.contentControls.height();
        optionsAux.scrollWrapper.css({
          height: scrollHeigth
        });

        optionsAux.scrollContent.css({
          width: optionsAux.formWidth
        });

        // Attaching the events for make scrollbars appear and disappear.
        optionsAux.scrollWrapper.on('mouseover', function() {
          optionsAux.scrollWrapper.css({
            overflow: 'auto'
          });
          /* The next lines are for show de horizontal scrollbar only when
           * it's needed.
           */
          if (options.windowWidth >= (optionsAux.formWidth + options.modalPadding)) {
            optionsAux.scrollWrapper.css({
              overflowX: 'hidden'
            });
          }
        });

        optionsAux.scrollWrapper.on('mouseout', function() {
          optionsAux.scrollWrapper.css({
            overflow: 'hidden'
          });
        });
      };

      that.prepareModal(url, true, preProcessHTMLEdit, options, onShowEdit);
    }

  };

  // Reveal module.
  window.sylva.modals = modals;
  var that = modals;

})(sylva, sigma, jQuery, window, document);
