// Base code for Sylva data import tools (Gephi, CSV).

/* jshint strict: true, undef: true, unused: true, eqeqeq: true, maxlen: 80 */
/* global window, document, console, FileReader, DOMParser, jQuery */

;(function($, window, document, undefined) {

  'use strict';


  // Sylva global namespace.
  var sylva = window.sylva || {};

  if (!sylva.sylvaSchema) {
    console.log("Error: graph schema not found.");
    return;
  }

  // Django i18n.
  // var gettext = window.gettext || String;

  // Data import library namespace.
  sylva.DataImporter = {};

  // Nodes schema.
  sylva.DataImporter.schemaNodes = sylva.sylvaSchema.nodeTypes;

  // Relationships schema.
  sylva.DataImporter.schemaEdges = sylva.sylvaSchema.allowedEdges;

  // Nodes to import.
  sylva.DataImporter.nodes = {};

  // Edges to import.
  sylva.DataImporter.edges = [];

  // Number of nodes to import.
  sylva.DataImporter.nodesLength = 0;

  // A dictionary mapping imported nodes and recently created nodes on the
  // server.
  sylva.DataImporter.serverNodes = {};


  // Save a node in browser memory.
  sylva.DataImporter.addNode = function(id, type, properties) {
    if (type) {
      this.nodes[id] = {
        type: type,
        properties: properties
      };
      sylva.DataImporter.nodesLength++;
    }
  };


  // Save an edge in browser memory.
  sylva.DataImporter.addEdge = function(sourceId, targetId, label, properties) {
    if (label) {
      this.edges.push({
        sourceId: sourceId,
        targetId: targetId,
        label: label,
        properties: properties
      });
    }
  };


  // Check if a node matches the schema.
  sylva.DataImporter.matchNodeSchema = function(node, schemaNodes) {
    var isValid = true;

    if (schemaNodes.hasOwnProperty(node.type)) {
      for (var prop in node.properties) {
        if (!schemaNodes[node.type].hasOwnProperty(prop)) {
          isValid = false;
          break;
        }
      }
    } else {
      isValid = false;
    }

    return isValid;
  };


  // Check if an edge matches the schema.
  sylva.DataImporter.matchEdgeSchema = function(edge, schemaEdges, nodes) {
    var isValid = false;

    for (var i = 0, l = schemaEdges.length; i < l; i++) {
      var schemaEdge = schemaEdges[i];
      var source = nodes[edge.sourceId];
      var target = nodes[edge.targetId];

      if (source.type !== schemaEdge.source ||
          target.type !== schemaEdge.target ||
          edge.label !== schemaEdge.label) {
        continue;
      }

      isValid = true;
      for (var prop in edge.properties) {
        if (!schemaEdge.properties.hasOwnProperty(prop)) {
          isValid = false;
          break;
        }
      }

      if (isValid) {
        break;
      }
    }

    return isValid;
  };


  // Check if all nodes match the schema.
  sylva.DataImporter.validateNodes = function(nodes, schemaNodes) {
    var isValid = true;

    for (var nodeId in nodes) {
      isValid = this.matchNodeSchema(nodes[nodeId], schemaNodes);

      if (!isValid) {
        break;
      }
    }

    return isValid;
  };


  // Check if all edges match the schema.
  sylva.DataImporter.validateEdges = function(edges, schemaEdges, nodes) {
    var isValid = true;

    for (var i = 0, l = edges.length; i < l; i++) {
      isValid = this.matchEdgeSchema(edges[i], schemaEdges, nodes);

      if (!isValid) {
        break;
      }
    }

    return isValid;
  };


  // Check if the graph matches the schema.
  sylva.DataImporter.validateGraph = function(nodes, edges, schemaNodes,
      schemaEdges) {
    return this.validateNodes(nodes, schemaNodes) &&
      this.validateEdges(edges, schemaEdges, nodes);
  };


  // Send data to the server.
  sylva.DataImporter.sendData = function(url, data) {
    // $.ajax() implements the Promise interface.
    return $.ajax({
      url: url,
      data: data,
      type: 'POST',
      dataType: 'json'
    });
  };


  // Send a list of nodes to the server.
  sylva.DataImporter.sendNodesList = function(url, nodes) {
    return this.sendData(url, {data: JSON.stringify(nodes)});
  };


  // Send a list of edges to the server.
  sylva.DataImporter.sendEdgesList = function(url, edges) {
    var data = [],
        edge,
        i, li;

    for (i = 0, li = edges.length; i < li; i++) {
      edge = edges[i];
      data.push({
        sourceId: this.serverNodes[edge.sourceId],
        targetId: this.serverNodes[edge.targetId],
        type: edge.label,
        properties: edge.properties
      });
    }

    return this.sendData(url, {data: JSON.stringify(data)});
  };


  // Send nodes to the server.
  sylva.DataImporter.sendNodes = function(url, nodes) {
    var queue = [],
        deferred = $.Deferred();

    for (var nodeId in nodes) {
      queue.push({
        id: nodeId,
        data: nodes[nodeId]
      });
    }

    processQueue(this, url, queue, deferred);

    function processQueue(self, url, queue, deferred) {
      var elements,
          jqxhr,
          MAX_SIZE = sylva.IMPORT_MAX_SIZE,
          errorCounter = 0,
          MAX_ERRORS = 10;

      if (queue.length > 0) {
        elements = queue.splice(0, MAX_SIZE);
        jqxhr = self.sendNodesList(url, elements);
        jqxhr.done(doneFilter);
        jqxhr.fail(failFilter);
      } else {
        deferred.resolve();
      }

      function doneFilter(ids) {
        var id;

        for (id in ids) {
          self.serverNodes[id] = ids[id];
        }

        deferred.notify(elements.length);  // update progress bar
        processQueue(self, url, queue, deferred);
      }

      function failFilter() {
        if (errorCounter < MAX_ERRORS) {
          errorCounter++;
          window.setTimeout(function() {
            jqxhr = self.sendNodesList(url, elements);
            jqxhr.done(doneFilter);
            jqxhr.fail(failFilter);
          }, 1000 * errorCounter);
        } else {
          deferred.reject();
        }
      }
    }

    return deferred.promise();
  };


  // Send edges to the server.
  sylva.DataImporter.sendEdges = function(url, edges) {
    var queue = edges.slice(0),
        deferred = $.Deferred();

    processQueue(this, url, queue, deferred);

    function processQueue(self, url, queue, deferred) {
      var elements,
          jqxhr,
          MAX_SIZE = sylva.IMPORT_MAX_SIZE,
          errorCounter = 0,
          MAX_ERRORS = 10;

      if (queue.length > 0) {
        elements = queue.splice(0, MAX_SIZE);
        jqxhr = self.sendEdgesList(url, elements);
        jqxhr.done(doneFilter);
        jqxhr.fail(failFilter);
      } else {
        deferred.resolve();
      }

      function doneFilter() {
        deferred.notify(elements.length);  // update progress bar
        processQueue(self, url, queue, deferred);
      }

      function failFilter() {
        if (errorCounter < MAX_ERRORS) {
          errorCounter++;
          window.setTimeout(function() {
            jqxhr = self.sendEdgesList(url, elements);
            jqxhr.done(doneFilter);
            jqxhr.fail(failFilter);
          }, 1000 * errorCounter);
        } else {
          deferred.reject();
        }
      }
    }

    return deferred.promise();
  };


  // Send nodes and edges to the server.
  sylva.DataImporter.sendGraph = function(nodes, edges, nodesUrl, edgesUrl) {
    var promiseGraph,
        promiseNodes,
        self = this;

    promiseNodes = this.sendNodes(nodesUrl, nodes);
    promiseGraph = promiseNodes.then(function() {
      return self.sendEdges(edgesUrl, edges);
    });

    return promiseGraph;
  };


  // CSV import.
  sylva.DataImporter.loadCSV = function(nodesFiles, edgesFiles) {
    var deferredNodes = $.Deferred(),
        deferredCSV = $.Deferred(),
        self = this;

    function getRows(csv) {
      var rows = csv.split(/^[ \t]*"(?!")/gm);

      rows.shift();

      for (var i = 0, li = rows.length; i < li; i++) {
        rows[i] = ('"' + rows[i]).trim();
      }

      return rows;
    }

    function getColumns(row) {
      var columns,
          columnsLength,
          column,
          last,
          cleanedRow,
          cleanedColumns = [];

      // Replace blank fields: "field1",,"field3" → "field1","","field3"
      cleanedRow = row.replace(/",,(\s*$|(?="[^"]))/g, '","",');
      if (cleanedRow.charAt(cleanedRow.length - 1) === ',') {
        cleanedRow += '""';
      }

      // Every field must be enclosed in double quotes.
      columns = cleanedRow.split(/"\s*,\s*((?=""\s*$)|(?=""\s*,)|(?="[^"]))/g);
      columnsLength = columns.length;
      last = columns[columnsLength - 1];

      for (var i = 0; i < columnsLength - 1; i++) {
        column = columns[i];

        if (column !== "") {
          cleanedColumns.push(column.trim().substring(1).trim());
        }
      }

      cleanedColumns.push(last.trim().slice(1, -1).trim());

      return cleanedColumns;
    }

    function loadNodes(files) {
      var deferredsQueue = [];

      for (var i = 0, li = files.length; i < li; i++) {
        deferredsQueue.push(loadNodesFile(files[i]));
      }

      $.when.apply(window, deferredsQueue)
        .done(function() {
          deferredNodes.resolve();
        })
        .fail(function() {
          deferredNodes.reject();
          deferredCSV.reject();
          console.log("Error: nodes not found.");
        });

      function loadNodesFile(file) {
        var deferredFile = $.Deferred(),
            reader = new FileReader();

        reader.onload = processNodes;
        reader.readAsText(file);

        function processNodes(event) {
          var rows,
              columns,
              csvHeader,
              properties,
              propKey,
              i, li, j, lj;

          console.log('Processing nodes...');

          rows = getRows(event.target.result);

          if (rows.length > 0) {
            csvHeader = getColumns(rows[0]);

            for (i = 1, li = rows.length; i < li; i++) {
              columns = getColumns(rows[i]);

              properties = {};
              for (j = 2, lj = columns.length; j < lj; j++) {
                propKey = csvHeader[j];
                if (propKey.charAt(0) !== '_') {
                  properties[propKey] = cleanValue(columns[j]);
                }
              }

              self.addNode(columns[0], columns[1], properties);
            }
          }

          if (sylva.DataImporter.nodesLength > 0) {
            deferredFile.resolve();
          } else {
            deferredFile.reject();
          }
        }

        return deferredFile.promise();
      }
    }

    function loadEdges(files) {
      var deferredsQueue = [];

      for (var i = 0, li = files.length; i < li; i++) {
        deferredsQueue.push(loadEdgesFile(files[i]));
      }

      $.when.apply(window, deferredsQueue).done(function() {
        deferredCSV.resolve();
      });

      function loadEdgesFile(file) {
        var deferredFile = $.Deferred(),
            reader = new FileReader();

        reader.onload = processEdges;
        reader.readAsText(file);

        function processEdges(event) {
          deferredNodes.done(function() {
            var rows,
                columns,
                csvHeader,
                properties,
                propKey,
                i, li, j, lj;

            console.log('Processing edges...');

            rows = getRows(event.target.result);
            csvHeader = getColumns(rows[0]);

            for (i = 1, li = rows.length; i < li; i++) {
              columns = getColumns(rows[i]);

              properties = {};
              for (j = 3, lj = columns.length; j < lj; j++) {
                propKey = csvHeader[j];
                if (propKey.charAt(0) !== '_') {
                  properties[propKey] = cleanValue(columns[j]);
                }
              }

              self.addEdge(columns[0], columns[1], columns[2], properties);
            }

            deferredFile.resolve();
          });
        }

        return deferredFile.promise();
      }
    }

    loadNodes(nodesFiles);
    loadEdges(edgesFiles);

    return deferredCSV.promise();
  };


  // Gephi import.
  sylva.DataImporter.loadGEXF = function(file) {
    var deferred = $.Deferred();

    function loadFile(file) {
      var reader = new FileReader();

      reader.onload = processGEXF;
      reader.readAsText(file);

      function processGEXF(event) {
        var parser = new DOMParser();
        var gexf = parser.parseFromString(event.target.result, "text/xml");

        var nodesAttributes = {};
        var edgesAttributes = {};
        var attributesNodes = gexf.getElementsByTagName('attributes');

        var id, title, type;
        var attribute, attributeId, attributeTitle, attributeValue;
        var i, j, k, li, lj, lk;

        // Loop through attributes elements and store attributes for
        // nodes and edges.
        for (i = 0, li = attributesNodes.length; i< li; i++) {
          var attributesNode = attributesNodes[i];

          if (attributesNode.getAttribute('class') === 'node') {
            var attributeNodes =
                attributesNode.getElementsByTagName('attribute');

            for (j = 0, lj = attributeNodes.length; j < lj; j++) {
              var attributeNode = attributeNodes[j];

              id = attributeNode.getAttribute('id').trim();
              title = attributeNode.getAttribute('title');
              title = title.slice(title.indexOf(')') + 1).trim();
              type = attributeNode.getAttribute('type').trim();

              // Store node attributes.
              nodesAttributes[id] = {title: title, type: type};
            }
          } else if (attributesNode.getAttribute('class') === 'edge') {
            var attributeEdges =
                attributesNode.getElementsByTagName('attribute');

            for (j = 0, lj = attributeEdges.length; j < lj; j++) {
              var attributeEdge = attributeEdges[j];

              id = attributeEdge.getAttribute('id').trim();
              title = attributeEdge.getAttribute('title');
              title = title.slice(title.indexOf(')') + 1).trim();
              type = attributeEdge.getAttribute('type').trim();

              // Store edge attributes.
              edgesAttributes[id] = {title: title, type: type};
            }
          }
        }

        var nodesNodes = gexf.getElementsByTagName('nodes');

        // loop through <nodes> elements
        for (i = 0, li = nodesNodes.length; i < li; i++) {
          var nodesNode = nodesNodes[i];
          var nodeNodes = nodesNode.getElementsByTagName('node');

          // loop through <node> elements
          for (j = 0, lj = nodeNodes.length; j < lj; j++) {
            var nodeNode = nodeNodes[j];

            var nodeId = nodeNode.getAttribute('id').trim(),
                nodeType = nodeNode.getAttribute('type').trim();

            // TODO: store node position (x,y)
            var nodeAttributes = {};

            var attvalueNodes = nodeNode.getElementsByTagName('attvalue');

            // loop through <attvalue> elements
            for (k = 0, lk = attvalueNodes.length; k < lk; k++) {
              var attvalueNode = attvalueNodes[k];

              attributeId = attvalueNode.getAttribute('for');

              if (attributeId !== 'NodeType' && attributeId !== 'NodeTypeId') {
                attribute = nodesAttributes[attributeId];

                if (attribute !== undefined) {
                  attributeTitle = attribute.title.trim();
                  if (attributeTitle.charAt(0) !== '_') {
                    attributeValue = attvalueNode.getAttribute('value').trim();
                    nodeAttributes[attributeTitle] = cleanValue(attributeValue);
                  }
                }
              }
            }

            sylva.DataImporter.addNode(nodeId, nodeType, nodeAttributes);
          }
        }

        var edgesNodes = gexf.getElementsByTagName('edges');

        // loop through <edges> elements
        for (i = 0, li = edgesNodes.length; i < li; i++) {
          var edgesNode = edgesNodes[i];
          var edgeNodes = edgesNode.getElementsByTagName('edge');

          // loop through <edge> elements
          for (j = 0, lj = edgeNodes.length; j < lj; j++) {
            var edgeNode = edgeNodes[j];

            var edgeSource = edgeNode.getAttribute('source').trim(),
                edgeTarget = edgeNode.getAttribute('target').trim(),
                edgeLabel = edgeNode.getAttribute('label').trim();

            var edgeAttributes = {};

            var attvalueEdges = edgeNode.getElementsByTagName('attvalue');

            // loop through <attvalue> elements
            for (k = 0, lk = attvalueEdges.length; k < lk; k++) {
              var attvalueEdge = attvalueEdges[k];

              attributeId = attvalueEdge.getAttribute('for');

              if (attributeId !== '_id' && attributeId !== 'RelationshipType' &&
                  attributeId !== 'RelationshipTypeId') {
                attribute = edgesAttributes[attributeId];

                if (attribute !== undefined) {
                  attributeTitle = attribute.title.trim();
                  if (attributeTitle.charAt(0) !== '_') {
                    attributeValue = attvalueEdge.getAttribute('value').trim();
                    edgeAttributes[attributeTitle] = cleanValue(attributeValue);
                  }
                }
              }
            }

            sylva.DataImporter.addEdge(edgeSource, edgeTarget, edgeLabel,
                                      edgeAttributes);
          }
        }

        if (sylva.DataImporter.nodesLength > 0) {
          deferred.resolve();
        } else {
          deferred.reject();
          console.log("Error: nodes not found.");
        }
      }
    }

    loadFile(file);

    return deferred.promise();
  };


  // Utils.


  // Try to convert `value` into a valid type for Sylva.
  function cleanValue(value) {
     return cleanBoolean(cleanDate(cleanQuotes(value)));
  }


  // Remove escaped double quotes (see CSV standard).
  function cleanQuotes(str) {
    return str.replace(/\"\"/g, '"');
  }


  // Change `date` to match the pattern: yyyy-mm-dd.
  function cleanDate(date) {
    var cleanedDate,
        matches,
        day,
        month,
        year,
        aux,
        isCleaned = false;

    // match dd/mm/yyyy or mm/dd/yyyy?
    matches = date.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
    if (matches !== null) {
      day = parseInt(matches[1], 10);
      month = parseInt(matches[2], 10);
      year = matches[3];

      if (month > 12) {
        aux = day;
        day = month;
        month = aux;
      }

      isCleaned = true;
    }

    if (!isCleaned) {
      // match yyyy/mm/dd or yyyy/dd/mm?
      matches = date.match(/(\d{4})\/(\d{1,2})\/(\d{1,2})/);
      if (matches !== null) {
        day = parseInt(matches[3], 10);
        month = parseInt(matches[2], 10);
        year = matches[1];

        if (month > 12) {
          aux = day;
          day = month;
          month = aux;
        }

        isCleaned = true;
      }
    }

    if (!isCleaned) {
      // match dd-mm-yyyy or mm-dd-yyyy?
      matches = date.match(/(\d{1,2})-(\d{1,2})-(\d{4})/);
      if (matches !== null) {
        day = parseInt(matches[1], 10);
        month = parseInt(matches[2], 10);
        year = matches[3];

        if (month > 12) {
          aux = day;
          day = month;
          month = aux;
        }

        isCleaned = true;
      }
    }

    if (!isCleaned) {
      // match yyyy-dd-mm?
      matches = date.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
      if (matches !== null) {
        day = parseInt(matches[3], 10);
        month = parseInt(matches[2], 10);
        year = matches[1];

        if (month > 12) {
          aux = day;
          day = month;
          month = aux;
        }

        isCleaned = true;
      }
    }

    if (isCleaned) {
      cleanedDate = year + '-' + month + '-' + day;
    } else {
      cleanedDate = date;
    }

    return cleanedDate;
  }


  // Change `bool` to match Python booleans: True/False.
  function cleanBoolean(bool) {
    var cleanedBoolean,
        isCleaned = false;

    cleanedBoolean = bool.toLowerCase();

    if (cleanedBoolean === 'true') {
      cleanedBoolean = 'True';
      isCleaned = true;
    } else if (cleanedBoolean === 'false') {
      cleanedBoolean = 'False';
      isCleaned = true;
    }

    if (!isCleaned) {
      cleanedBoolean = bool;
    }

    return cleanedBoolean;
  }

}(jQuery, window, document));