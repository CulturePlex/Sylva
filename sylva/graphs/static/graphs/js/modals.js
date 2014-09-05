// JSHint options

/* global window:true, document:true, setTimeout:true, console:true,
 * jQuery:true, sylva:true, prompt:true, alert:true, sigma:true, clearTimeout
 */

/****************************************************************************
 * modal.js - All the function need for control the modal windows.
 ****************************************************************************/

;(function(sylva, sigma, $, window, document, undefined) {

  var that = null;
  // The loading string for the modals, a very used resource.
  var loadingTextFunction = gettext('Loading...');
  // For some animations we need the same time that the 'fast' jQuery, 200ms.
  var fast = 200;

  var modals = {

    /* ****
     * Functions of the 'mini-framework'.
     *
     * It has 4 main parts in 2 blocks, you need to use complete blocks and
     * being the first one obligatory:
     *
     *  BLOCK I
     *  =======
     *
     *  - preapreModal: Gets the HTML to show. Its parameters are:
     *      - url: Where to get the HTML
     *      - showOverlay: Does it must to darken the background?
     *                     (Only for the first modal)
     *      - modalActions: A dictionary with three functions, two of them for
     *                      use them in the next step
     *
     *  - showModal: Changes what its necesary in the recevied HTML with the
     *               the help of two of the three fucntions commented before.
     *               Its parameter are:
     *      - html: The HTML to show
     *      - modalActions: A dictionary with three functions, here it only use
     *                      two of them:
     *          - preProcessHTML: Here you can change wathever you need from
     *                            your HTML and return a dictionary with the
     *                            objects you'll ned in the 'onShow' function
     *                            need from your HTML
     *          - onShow: Function for call it in the 'onShow' event of the
     *                    dropit library. Here you can change again whatever
     *                    you need. Also you receive a dictonary with the
     *                    returned object in the 'preProcessHTML' function plus
     *                    the next ones:
     *              - html: The HTML inside the modal
     *              - modalHTML: The parent HTML element that contains the
     *                           modal
     *              - windowHeight: The height of the browser window
     *              - windowWidth: The width of the browser window
     *              - modalPadding: The padding added to the modal HTML element
     *
     *  BLOCK II
     *  ========
     *
     *  - saveModalForm: Send a form to the backend for save it. Its parameter
     *                   is a dictonary called 'requestInfo' with these keys:
     *      - url: The URL for perform the request
     *      - formSelector: The selector of the form to serialize
     *      - extraParams: A string to append at the end of the serialized form
     *
     *  - handleFormServerResponse: The only 'changing' function of the
     *                              framework, because it needs to be changed
     *                              with new behaviours. It handles the
     *                              response of the previous function,
     *                              'saveModalForm', by reloading a from with
     *                              erros or whatever you need.
     ***** */

    init: function() {
      that = this;
    },

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
    prepareModal: function(url, showOverlay, modalActions) {
      that.customTextModal(loadingTextFunction, showOverlay);

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
          that.showModal(data.html, modalActions);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });

    },

    // It displays the HTML given by 'prepareModal'.
    showModal: function(html, modalActions) {
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

      onShowOptions = {
        html: html,
        modalHTML: modalHTML,
        windowHeight: windowHeight,
        windowWidth: windowWidth,
        modalPadding: modalPadding
      };
      $.extend(onShowOptions, modalActions.preProcessHTML());

      if (modalActions.onShow == null) {
        modalActions.onShow = function() {};
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
        onShow: function(dialog) {
          modalActions.onShow(dialog, onShowOptions);
        }
      });
    },

    /* This function handles the 'Save' and 'Save as new' options from the
     * 'edit node modal'.
     */
    saveModalForm: function(requestInfo) {
      // Closing the 'edit node' modal and showing the loading one.
      $.modal.close();
      setTimeout(function() {
        that.customTextModal(loadingTextFunction);
      }, fast);

      var serializedForm = $(requestInfo.formSelector).serialize();
      serializedForm += requestInfo.extraParams;

      // Performing the request with the created variables.
      var jqxhr = $.ajax({
        url: requestInfo.url,
        type: 'POST',
        data: serializedForm,
        dataType: 'json'
      });
      jqxhr.success(function(data) {
        /* Here we need a double 'setTimeout()' because the previous one, also
         * inside this function maybe isn't finished when the AJAX request
         * starts.
         */
        setTimeout(function() {
          $.modal.close(); // Closing the loading modal.
          setTimeout(function() {
            that.handleFormServerResponse(data);
          }, fast);
        }, fast);
      });
      jqxhr.error(function() {
        alert(gettext("Oops! Something went wrong with the server."));
        that.closeModalLib();
      });

      // False is needed, that way the form isn't sended.
      return false;
    },

    // It acts depending of what the server returns from the modal forms.
    handleFormServerResponse: function(response) {
      if (response.type == 'html') { // If it's 'html' it's a form with errors.

        /* This is the only part of the mini-framework that must be changed if
         * something new is added.
         */
        var modalAction = null
        if(response.action == 'collaborators') {
          modalAction = that.collaborators;
        } else if(response.action == 'edit') {
          modalAction = that.editNode;
        } else if(response.action == 'delete') {
          modalAction = that.deleteNode;
        }
        that.showModal(response.html, modalAction);

      } else { // If it is not, is a final reponse.

        that.destroyOverlay(); // Exiting, so destroying the overlay layer.

        switch (response.action) {
          case 'edit':
            sylva.Sigma.deleteNode(true, response.node,
              response.oldRelationshipIds);
            sylva.Sigma.addNode(true, response.node, response.relationships);
            break;

          case 'new':
            sylva.Sigma.addNode(false, response.node, response.relationships);
            break;

          case 'delete':
            sylva.Sigma.deleteNode(false, response.nodeId,
              response.oldRelationshipIds);
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

    /* ****
     * Upper level 'actions' for use them in the 'mini-framework'.
     *
     * These are the dictionary that the framework takes, mainly for the
     * 'preProcessHTML' and 'onShow' functions. No one of them are obligatory,
     * only the first one, 'start' that tell how you must start the modal.
     *
     ***** */

    editNode: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        var deleteNodeActions = that.deleteNode;

        // Getting the URL for delete the node.
        var deleteFormURL = $('#delete-url').attr('data-url');

        // Hidding "Add node" links.
        $('.add-node').hide();

        // Variables for save the node by saving the form.
        var saveURL = $('#save-url').attr('data-url');
        var formSelector = '#edit-node-form';
        var extraParamsEdit = '&asModal=true';
        var extraParamsAsNew = extraParamsEdit + '&as-new=true';

        // Binding the 'events' for the four actions.
        $('#submit-save').attr('onclick',
          "return sylva.modals.saveModalForm({url: '" + saveURL + "'" +
            ", formSelector: '" + formSelector + "'" +
            ", extraParams: '" + extraParamsEdit + "'" +
            "})");
        $('#submit-save-as-new').attr('onclick',
          "return sylva.modals.saveModalForm({url: '" + saveURL + "'" +
            ", formSelector: '" + formSelector + "'" +
            ", extraParams: '" + extraParamsAsNew + "'" +
            "})");
        $('#submit-delete').on('click', function() {
          $.modal.close();
          setTimeout(function() {
            that.deleteNode.start(deleteFormURL, false);
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
      },

      onShow: function(dialog, options) {
        // It's the content who controls the scrollbars.
        dialog.wrap.css({
          overflow: 'hidden'
        });

        /* Calculatin the height of the wrapper of the form for made it
         * scrollable.
         */
        var scrollHeigth = dialog.wrap.height() - options.contentControls.height();
        options.scrollWrapper.css({
          height: scrollHeigth
        });

        options.scrollContent.css({
          width: options.formWidth
        });

        // Attaching the events for make scrollbars appear and disappear.
        options.scrollWrapper.on('mouseover', function() {
          options.scrollWrapper.css({
            overflow: 'auto'
          });
          /* The next lines are for show de horizontal scrollbar only when
           * it's needed.
           */
          if (options.windowWidth >= (options.formWidth + options.modalPadding)) {
            options.scrollWrapper.css({
              overflowX: 'hidden'
            });
          }
        });

        options.scrollWrapper.on('mouseout', function() {
          options.scrollWrapper.css({
            overflow: 'hidden'
          });
        });
      }

    },

    deleteNode: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Removing style.
        $('#content2').css({
          minHeight: '100px',
          overflow: 'hidden'
        });

        // Variables for save the node by saving the form.
        var deleteURL = $('#delete-url').attr('data-url');
        var formSelector = '#delete-node-form';
        var extraParams = '&asModal=true';

        // Binding the 'events' for the four actions.
        $('#submit-delete').attr('onclick',
          "return sylva.modals.saveModalForm({url: '" + deleteURL + "'" +
            ", formSelector: '" + formSelector + "'" +
            ", extraParams: '" + extraParams + "'" +
            "})");
        $('#submit-cancel').removeAttr('href');
        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
        });
      },

      onShow: function() {}
    },

    collaborators: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        $('#content2').css({
          minHeight: 120
        });

        // Variables for save the collaborator by saving the form.
        var addURL = $('#add-url').attr('data-url');
        var formSelector = '#add-collaborator-form';
        var extraParams = '&asModal=true';

        // Binding the 'events' for the two actions.
        $('#submit-add').attr('onclick',
          "return sylva.modals.saveModalForm({url: '" + addURL + "'" +
            ", formSelector: '" + formSelector + "'" +
            ", extraParams: '" + extraParams + "'" +
            "})");

        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#id_new_collaborator_chzn').css({
          position: 'absolute',
          top: 63,
          left: 10
        });
      }
    }

  };

  // Reveal module.
  window.sylva.modals = modals;

})(sylva, sigma, jQuery, window, document);
