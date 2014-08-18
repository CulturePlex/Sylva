(function($) {

  "use strict";

  $(function() {
    var facets = sylva.jsValues.facets;
    var facet_values = sylva.jsValues.facetValues;

    var $table_rows = $('#content_table tbody tr');
    var $table_rows_filtered = $table_rows;
    var query_facets = {};
    var pagination_content = '';

    var searching = false;

    var visualSearch = VS.init({
      container: $('#search-query'),
      query: '',
      autosearch: true,
      showFacets: true,
      remainder: 'search',
      callbacks: {
        facetMatches: function(callback) {
          callback(facets);
        },
        valueMatches: function(facet, searchTerm, callback) {
          callback(facet_values[facet]);
        },
        search: function(query, searchCollection) {
          var collection_facets = searchCollection.facets();
          for (var i = 0, l = collection_facets.length; i < l; i++) {
            var collection_facet = collection_facets[i];
            for (var facet in collection_facet) {
              if (collection_facet.hasOwnProperty(facet)) {
                $table_rows_filtered = $table_rows_filtered.filter(':contains("' + collection_facet[facet] + '")');
                query_facets[facet] = collection_facet[facet];
              }
            }
          }
          // Show only faceted results.
          $table_rows.not($table_rows_filtered).hide();

          // Update pagination info.
          var $pag_info = $('.pagination-info');
          pagination_content = $pag_info.parent().html();
          var info_list = $pag_info.text().trim().split(' ');
          var results_count = $table_rows.filter(':visible').length;
          info_list[1] = results_count;
          $pag_info.text(info_list.join(' '));

          // In other case, run a full search.
          if (!$table_rows.is(':visible')) {
            searching = true;
            var node_type_id = sylva.jsValues.nodetypeId;
            var data_query = {};
            data_query[node_type_id] = JSON.stringify(query_facets);
            $.ajax({
              url: sylva.urls.nodesLookupFull,
              data: data_query,
              success: add_search_results
            });
          }
        },
        clearSearch: function(actualClearSearch) {
          if (!searching) {
            update_pagination_info(pagination_content);
          }
          actualClearSearch();
          $table_rows.show();
          $table_rows_filtered = $table_rows;
        },
        removedFacet: function (facet, query, options) {
          if (!searching) {
            update_pagination_info(pagination_content);
          }
          delete query_facets[facet.attributes.category];
          $table_rows_filtered = $table_rows;
          var is_empty = true;
          for (var prop in query_facets) {
            if (query_facets.hasOwnProperty(prop)) {
              is_empty = false;
              $table_rows_filtered = $table_rows_filtered.filter(':contains("' + query_facets[prop] + '")');
            }
          }
          if (is_empty) {
            $table_rows.show();
            $table_rows_filtered = $table_rows;
          } else {
            $table_rows.show()
                       .not($table_rows_filtered)
                       .hide();
          }
        }
      }
    });

    var update_pagination_info = function(content) {
      document.querySelector('.pagination').innerHTML = content;
    };

    // Show search results as table rows.
    var add_search_results = function(nodes) {
      var i, j, l1, l2;

      var tbody = document.querySelector('#content_table tbody');
      tbody.innerHTML = '';
      var pagination = document.querySelector('.pagination');
      pagination.classList.add('hidden');

      if (nodes.length === 0) {
        tbody.innerHTML =
          '<tr>' +
            '<td colspan="4" style="padding-top: 10px; text-align: center;">' +
              gettext("Your search did not return any results") +
            '</td>' +
          '</tr>';
        return;
      }

      var properties = facets;

      var tr_elements = document.createDocumentFragment();

      for (i = 0, l1 = nodes.length; i < l1; i++) {
        var tr_node = document.createElement('tr');
        var tr_rel = document.createElement('tr');

        if (i % 2 === 0) {
          tr_node.className = 'row-even';
          tr_rel.className = 'row-even';
        } else {
          tr_node.className = 'row-odd';
          tr_rel.className = 'row-odd';
        }

        var td_dataList = document.createElement('td');
        td_dataList.className = 'dataList';

        var link_toggle = document.createElement('a');
        link_toggle.href = 'javascript:void(0)';
        link_toggle.dataset.node = nodes[i].id;
        link_toggle.className = 'rels';
        link_toggle.title = gettext("Toggle relationships");
        link_toggle.innerHTML = '&nbsp';

        td_dataList.appendChild(link_toggle);

        var link_edit = document.createElement('a');
        var link_edit_url = sylva.urls.nodesEdit;
        link_edit.href = link_edit_url.replace('/0/', '/' + nodes[i].id + '/');
        link_edit.className = 'edit';
        link_edit.title = gettext("Edit node");
        link_edit.innerHTML = '&nbsp';

        td_dataList.appendChild(link_edit);
        tr_node.appendChild(td_dataList);
        tr_elements.appendChild(tr_node);

        var node_properties = nodes[i].properties;
        for (j = 0, l2 = properties.length; j < l2; j++) {
          var prop = properties[j];
          var td_prop = document.createElement('td');

          if (node_properties.hasOwnProperty(prop)) {
            if (node_properties[prop] === '') {
              var span_empty = document.createElement('span');
              span_empty.className = 'helptext';
              span_empty.innerText = '(Empty)';

              td_prop.appendChild(span_empty);
            } else if (node_properties[prop] === 'True' || node_properties[prop] === 'False') {
              td_prop.appendChild(document.createTextNode(node_properties[prop]));
            } else {
              var link_prop = document.createElement('a');
              var link_prop_url = sylva.urls.nodesView;
              link_prop.href = link_prop_url.replace('/0/', '/' + nodes[i].id + '/');
              link_prop.title = gettext("View node");
              link_prop.innerText = node_properties[prop];

              td_prop.appendChild(link_prop);
            }
          } else {
            var span_empty = document.createElement('span');
            span_empty.className = 'helptext';
            span_empty.innerText = '(Empty)';

            td_prop.appendChild(span_empty);
          }

          tr_node.appendChild(td_prop);
        }

        var td_rel = document.createElement('td');
        td_rel.colSpan = properties.length + 1;
        td_rel.id = 'td' + nodes[i].id;
        td_rel.className = 'hidden retrieve-relationships';
        td_rel.dataset.node = nodes[i].id;
        td_rel.dataset.display = nodes[i].display;
        var rel_url = sylva.urls.nodeRelationships;
        td_rel.dataset.nodeRels= rel_url.replace('/0/', '/' + nodes[i].id + '/');

        var span_loading = document.createElement('span');
        span_loading.className = 'helptext';
        span_loading.innerText = gettext("Loading");

        td_rel.appendChild(span_loading);
        tr_rel.appendChild(td_rel);
        tr_elements.appendChild(tr_rel);
      }

      tbody.appendChild(tr_elements);

      pagination.innerHTML = '<span class="pagination-info">' +
                             gettext("Showing") + ' ' + nodes.length + ' ' + gettext("results") +
                             '</span>';
      pagination.classList.remove('hidden');
    };

    // Bind events to data toggle controls to start the fetching of relationships.
    $('#content_table').on('click', '.rels', function() {
      var $this = $(this);
      var nodeId = $this.data("node");
      $("#td" + nodeId).toggle(0, function () {
        var element = $(this);
        element.parent().show();
        var url = element.data("node-rels");
        var display = element.data("display");
        // Fetch elements that are not already loaded and are visible
        if (!element.hasClass('is-loaded')) {
          element.addClass('is-loaded');
          retrieveRelationships(element, url, nodeId, display);
        }
      });
    });

    var retrieveRelationships = function(element, url, elementId, elemendDisplay) {
      $.ajax({
        url: url,
        success: function(data){
          var label, html;
          var relationships = JSON.parse(data);
          var divs = [];
          $.each(relationships, function(direction, rels) {
            html = $('<div>');
            html.addClass('indent');
            html.addClass('relationships-box');
            if (rels != false){
              html.append($('<span>').text(''));
            }
            $.each(rels, function(index, item){
              if (direction == "outgoing") {
                label = '<span class="symbol-medium">→</span> '+ elemendDisplay  +' <span class="bold">'+ item.label +'</span> '+ item.node_display;
              } else {
                label = ' <span class="symbol-medium">←</span> '+ item.node_display +' <span class="bold">'+ item.label +'</span> '+ elemendDisplay;
              }
              html.append($('<span>')
                .append(label))
                .append(' <br/> ');
            });
            divs.push(html);
          });
          element.html(divs);
        },
        error: function(error){
          console.log("ERROR: ", error);
        }
      });
    };

    $('.show-hide-button').hover(function() {
      //$('.show-hide').css('display', 'block');
      $('.dropdown').css('display', 'block');
    }, function() {
      //$('.show-hide').css('display', 'none');
      $('.dropdown').css('display', 'none');
    });

    $('.show-hide').on('click', function() {
      var $this = $(this);
      var key = $this.data("key");
      var classId = "." + key;
      var imgId = "#show-hide-" + key;
      $(classId).toggle();
      if ($(imgId).attr('class') == 'fa fa-eye'){
        $(imgId).attr('class','fa fa-eye-slash');
      } else {
        $(imgId).attr('class','fa fa-eye');
      }
    });
  });
}(jQuery));
