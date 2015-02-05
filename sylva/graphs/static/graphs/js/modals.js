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
    prepareModal: function(url, showOverlay, modalActions, extraParams) {
      that.customTextModal(loadingTextFunction, showOverlay);

      var params = {
        'asModal': true
      };

      if (extraParams !== undefined) {
        $.extend(params, extraParams);
      }

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
      jqxhr.error(function(e) {
        alert(e);
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
        if(response.action == 'edit') {
          modalAction = that.editNode;
        } else if (response.action == 'delete') {
          modalAction = that.deleteNode;
        } else if (response.action == 'create') {
           modalAction = that.createNode;
        } else if (response.action == 'collaborators') {
          modalAction = that.collaborators;
        } else if (response.action == 'import_schema') {
          modalAction = that.importSchema;
        } else if (response.action == 'queries_list') {
          modalAction = that.queriesList;
        } else if (response.action == 'queries_new') {
          modalAction = that.queriesNew;
        } else if (response.action == 'queries_results') {
          modalAction = that.queriesResults;
        } else if (response.action == 'queries_delete') {
          modalAction = that.queriesDelete;
        } else if (response.action == 'schema_main') {
          modalAction = that.schemaMainView;
        } else if (response.action == 'schema_nodetype_editcreate') {
          modalAction = that.schemaNodetypeEditCreate;
        } else if (response.action == 'schema_relationship_editcreate') {
          modalAction = that.schemaRelationshipEditCreate;
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
          case 'create':
            sylva.Sigma.addNode(false, response.node, response.relationships);
            break;

          case 'delete':
            sylva.Sigma.deleteNode(false, response.nodeId,
              response.oldRelationshipIds);
            break;
          case 'import_schema':
            /* TODO: When the full window mode could be activated withot schema
             * data, the next line should be changed.
             */
            location.reload();
          case 'import_graph':
            /* TODO: When the full window mode could be activated withot schema
             * data, the next line should be changed.
             */
            // location.reload(); But this is called in the tool.js file.
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

      preProcessHTML: editAndCreateNodePreProcessHTML,

      onShow: editAndCreateNodeOnShow

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

    createNode: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: editAndCreateNodePreProcessHTML,

      onShow: editAndCreateNodeOnShow
    },

    listNodes: {

      start: function(url, showOverlay, params) {
        that.prepareModal(url, showOverlay, this, params);
      },

      preProcessHTML: function() {
        var existList = true;
        if ($('.visual-search').length == 0) {
          existList = false;
        }

        if (existList) {
          var viewNodeLinks = $("a[title='View node']");
          viewNodeLinks.css({
            cursor: 'default'
          });
          viewNodeLinks.on('click', function() {
            return false;
          });

          // A function for handling the pagination and sorting events.
          var handlePagination = function(event) {
            var listURL = $('#list-url').attr('data-url');

            if ($(event.target).attr('href') != undefined) {
              var rawParams = $(event.target).attr('href');
            } else {
              var rawParams = $(event.target).parent().attr('href');
            }

            var regex = /[?&]([^=#]+)=([^&#]*)/g;
            var match = {};
            var params = {};

            while (match = regex.exec(rawParams)) {
              params[match[1]] = match[2];
            }

            $.modal.close();
            setTimeout(function() {
              that.listNodes.start(listURL, false, params);
            }, fast);

            return false;
          };

          // The events for the previous function.
          $('span.step-links > a').on('click', handlePagination);
          $('a.remove-sorting').on('click', handlePagination);
          $('a[data-modal="list-sort"]').on('click', handlePagination);

          $('a[class="edit"][alt="Edit node"]').on('click', function(event) {
            var editNodeURL = $(event.target).attr('href');

            $.modal.close();
            setTimeout(function() {
              that.editNode.start(editNodeURL, false);
            }, fast);

            return false;
          });

          $('#content2').css({
            minHeight: 215,
            width: 810
          });

        } else {
          $('#submit-cancel').parent().width('92%');

          $('#content2').width(235);

          $('#content2').css({
            minHeight: 55
          });
        }

        $('#submit-create').on('click', function() {
            var createNodeURL = $(event.target).attr('href');

            $.modal.close();
            setTimeout(function() {
              that.createNode.start(createNodeURL, false);
            }, fast);

            return false;
          });

        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });

        // Getting HTML elemetns as variables.
        var scrollWrapper = $('#modal-content-scrollable-wrapper');
        var scrollContent = $('#modal-content-scrollable');
        var contentControls = $('.content2-full-bottom');
        scrollWrapper.addClass('modal-content-scrollable-wrapper');
        // Calculating the width of the table.
        var contentTable = $('#content_table');

        return {
          contentControls: contentControls,
          scrollWrapper: scrollWrapper,
          scrollContent: scrollContent,
          contentTable: contentTable
        };
      },

      onShow: function(dialog, options) {
        // It's the content who controls the scrollbars.
        dialog.wrap.css({
          overflow: 'hidden'
        });

        /* Calculating the height of the wrapper of the form for make it
         * scrollable.
         */
        var scrollHeigth = dialog.wrap.height() - options.contentControls.height();
        options.scrollWrapper.css({
          height: scrollHeigth,
          overflow: 'auto'
        });

        $('#search-query').width('auto');
      }
    },

    collaborators: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        $('#content2').css({
          minHeight: 170
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
          top: 100,
          left: 10
        });
      }
    },

    importSchema: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        var formSelector = '#import-schema-form';
        var saveURL = $(formSelector).attr('action');
        var extraParams = '&asModal=true';

        $('#id_file').on('change', function(event) {
          var reader = new FileReader();

          reader.onload = function(e) {
            var contents = e.target.result;
            var inputName = 'file-modal';

            $('#' + inputName).remove();

            $('<input>').attr({
              type: 'hidden',
              id: inputName,
              name: inputName,
              value: contents
            }).appendTo(formSelector);
          };

          reader.readAsText(event.target.files[0]);
        });

        // Binding save/continue action.
        $('#submit-save').attr('onclick',
          "return sylva.modals.saveModalForm({url: '" + saveURL + "'" +
            ", formSelector: '" + formSelector + "'" +
            ", extraParams: '" + extraParams + "'" +
            "})");

        // Binding cancel action.
        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#id_file').width(240);
      }
    },

    importData: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Binding cancel action.
        $('#submit-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {}
    },

    // Modals for queries

    queriesList: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Event to create a new query
        $('#create-query').on('click', function() {
          var queriesNewUrl = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.queriesNew.start(queriesNewUrl, false);
          }, fast);

          return false;
        });

        // Event to edit an existing query
        $('a.edit').on('click', function() {
          var queriesNewUrl = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.queriesNew.start(queriesNewUrl, false);
          }, fast);

          return false;
        });

        // Event to execute an existing query
        $('a.run').on('click', function() {
          var queriesResultsUrl = $(event.target).parent().attr('href');
          var params = "&asModal=true";
          $.modal.close();
          setTimeout(function() {
            that.queriesResults.execute(queriesResultsUrl, params);
          }, fast);

          return false;
        });

        // Event to delete an existing query
        $('a.delete').on('click', function() {
          var queriesDeleteUrl = $(event.target).parent().attr('href');

          $.modal.close();
          setTimeout(function() {
            that.queriesDelete.start(queriesDeleteUrl, false);
          }, fast);

          return false;
        });

        // A function for handling the pagination and sorting events.
        var handlePagination = function(event) {
          var queriesListUrl = $('#queries-url').attr('data-url');

          if ($(event.target).attr('href') != undefined) {
            var pagAndOrderParams = $(event.target).attr('href');
          } else {
            var pagAndOrderParams = $(event.target).parent().attr('href');
          }

          pagAndOrderUrl = queriesListUrl + pagAndOrderParams;

          $.modal.close();
          setTimeout(function() {
            that.queriesList.start(pagAndOrderUrl, false);
          }, fast);

          return false;
        };

        // The events for the previous function.
        $('span.step-links > a').on('click', handlePagination);
        $('a.remove-sorting').on('click', handlePagination);
        $('a.sorting-asc').on('click', handlePagination);
        $('a.sorting-desc').on('click', handlePagination);
        $('.shorten-text').on('click', handlePagination);

        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1000,
          left: 100
        });

        $('#modal-cancel').css({
          'margin-left': '10px'
        });
      }
    },

    queriesNew: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        $('#run-query').on('click', function() {

          var queryElements = diagram.saveQuery();
          var query = queryElements['query'];
          var query_aliases = queryElements['aliases'];
          var query_fields = queryElements['fields'];

          var queryJson = JSON.stringify(query);
          var queryAliases = JSON.stringify(query_aliases);
          var queryFields = JSON.stringify(query_fields);

          $('input[id=query]').val(queryJson);
          $('input[id=query_aliases]').val(queryAliases);
          $('input[id=query_fields]').val(queryFields);

          var executeUrl = $('#execute-url').data('url');
          var formSelector = '#form-run-query';
          var extraParams = '&asModal=true';

          var serializedForm = $(formSelector).serialize();
          serializedForm += extraParams;

          $.modal.close();
          setTimeout(function() {
            that.queriesResults.execute(executeUrl, serializedForm);
          }, fast);

          return false;
        });

        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1170,
        });
        try {
          diagram.loadQuery(JSON.stringify(query));
        } catch (e) {}
      }
    },

    queriesResults: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      execute: function(requestUrl, params) {
        $.modal.close();
        setTimeout(function() {
          that.customTextModal(loadingTextFunction);
        }, fast);

        // Performing the request with the created variables.
        var jqxhr = $.ajax({
          url: requestUrl,
          type: 'POST',
          data: params,
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
        jqxhr.error(function(e) {
          alert(gettext("Oops! Something went wrong with the server."));
          that.closeModalLib();
        });
      },

      preProcessHTML: function() {
        // A function for handling the pagination and sorting events.
        var handlePagination = function(event) {
          var queriesListUrl = $('#queries-results-url').attr('data-url');

          if ($(event.target).attr('href') != undefined) {
            var pagAndOrderParams = $(event.target).attr('href');
          } else {
            var pagAndOrderParams = $(event.target).parent().attr('href');
          }

          params = "&asModal=true";

          pagAndOrderUrl = queriesListUrl + pagAndOrderParams;

          $.modal.close();
          setTimeout(function() {
            that.queriesResults.execute(pagAndOrderUrl, params);
          }, fast);

          return false;
        };

        // The events for the previous function.
        $('span.step-links > a').on('click', handlePagination);
        $('a.remove-sorting').on('click', handlePagination);
        $('a.sorting-asc').on('click', handlePagination);
        $('a.sorting-desc').on('click', handlePagination);
        $('.shorten-text').on('click', handlePagination);

        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1000
        });
      }
    },

    queriesDelete: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {}
    },

    // Schema modals

    schemaMainView: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // This is for create a new nodetype
        $('#schemaNewType').on('click', function() {
          var url = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.schemaNodetypeEditCreate.start(url, false);
          }, fast);

          return false;
        });

        // This is for edit nodetypes
        $('fieldset.module h2 a').on('click', function() {
          var url = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.schemaNodetypeEditCreate.start(url, false);
          }, fast);

          return false;
        });

        // This if for create a new relationship
        $('#allowedRelations').on('click', function() {
          var url = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.schemaRelationshipEditCreate.start(url, false);
          }, fast);

          return false;
        });

        // This is for create and edit relationships
        $('div.form-row a').on('click', function() {
          var url = $(event.target).attr('href');

          $.modal.close();
          setTimeout(function() {
            that.schemaRelationshipEditCreate.start(url, false);
          }, fast);

          return false;
        });

        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1170,
          left: 100
        });

        $('#diagramContainer').ready(function(){
          try {
            // diagram.loadModels();
          } catch(e) {}
        });
      }
    },

    schemaNodetypeEditCreate: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1170,
          left: 100
        });
      }
    },

    schemaRelationshipEditCreate: {

      start: function(url, showOverlay) {
        that.prepareModal(url, showOverlay, this);
      },

      preProcessHTML: function() {
        // Binding cancel action.
        $('#modal-cancel').on('click', function() {
          that.closeModalLib();
          return false;
        });
      },

      onShow: function() {
        $('#simplemodal-container').css({
          width: 1170,
          left: 100
        });
      }
    }

  };

  // Reveal module.
  window.sylva.modals = modals;

  // Two functions for not repeating them twice in edit and create node modals.
  function editAndCreateNodePreProcessHTML() {
    // Hidding "Add node" links.
    $('.add-node').hide();

    // Variables for save the node by saving the form.
    var saveURL = $('#save-url').attr('data-url');
    var formSelector = '#edit-node-form';
    var extraParams = '&asModal=true';

    // Binding the 'events' for the four actions.
    $('#submit-save').attr('onclick',
      "return sylva.modals.saveModalForm({url: '" + saveURL + "'" +
        ", formSelector: '" + formSelector + "'" +
        ", extraParams: '" + extraParams + "'" +
        "})");

    if ($('#submit-save-as-new').length) {
      var extraParamsAsNew = extraParams + '&as-new=true';
      var deleteFormURL = $('#delete-url').attr('data-url');

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
    }

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
  }

  function editAndCreateNodeOnShow(dialog, options) {
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

})(sylva, sigma, jQuery, window, document);
