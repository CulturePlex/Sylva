// Base code for Sylva data import tools (Gephi, CSV).

/* jshint strict: true, undef: true, unused: true, eqeqeq: true, maxlen: 80 */
/* global window, document, console, FileReader, DOMParser, jQuery */

;(function($, window, document, undefined) {

  'use strict';


  // Sylva global namespace.
  var sylv = window.sylv || {};

  if (!sylv.sylvaSchema) {
    console.log("Error: graph schema not found.");
    return;
  }

  // Django i18n.
  // var gettext = window.gettext || String;

  // Data import library namespace.
  sylv.DataImporter = {};

  // Nodes schema.
  sylv.DataImporter.schemaNodes = sylv.sylvaSchema.nodeTypes;

  // Relationships schema.
  sylv.DataImporter.schemaEdges = sylv.sylvaSchema.allowedEdges;

  // Nodes to import.
  sylv.DataImporter.nodes = {};

  // Edges to import.
  sylv.DataImporter.edges = [];

  // Number of nodes to import.
  sylv.DataImporter.nodesLength = 0;

  // A dictionary mapping imported nodes and recently created nodes on the
  // server.
  sylv.DataImporter.serverNodes = {};


  // Save a node in browser memory.
  sylv.DataImporter.addNode = function(id, type, properties) {
    if (type) {
      this.nodes[id] = {
        type: type,
        properties: properties
      };
      sylv.DataImporter.nodesLength++;
    }
  };


  // Save an edge in browser memory.
  sylv.DataImporter.addEdge = function(sourceId, targetId, label, properties) {
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
  sylv.DataImporter.matchNodeSchema = function(node, schemaNodes) {
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
  sylv.DataImporter.matchEdgeSchema = function(edge, schemaEdges, nodes) {
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
  sylv.DataImporter.validateNodes = function(nodes, schemaNodes) {
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
  sylv.DataImporter.validateEdges = function(edges, schemaEdges, nodes) {
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
  sylv.DataImporter.validateGraph = function(nodes, edges, schemaNodes,
      schemaEdges) {
    return this.validateNodes(nodes, schemaNodes) &&
      this.validateEdges(edges, schemaEdges, nodes);
  };


  // Send data to the server.
  sylv.DataImporter.sendData = function(url, data) {
    // $.ajax() implements the Promise interface.
    return $.ajax({
      url: url,
      data: data,
      type: 'POST',
      dataType: 'json'
    });
  };


  // Send a node to the server.
  sylv.DataImporter.sendNode = function(url, node) {
    var data;

    data = {
      type: node.type,
      properties: JSON.stringify(node.properties)
    };

    return this.sendData(url, data);
  };


  // Send an edge to the server.
  sylv.DataImporter.sendEdge = function(url, edge) {
    var data;

    data = {
      sourceId: this.serverNodes[edge.sourceId],
      targetId: this.serverNodes[edge.targetId],
      type: edge.label,
      properties: JSON.stringify(edge.properties)
    };

    return this.sendData(url, data);
  };


  // Send nodes to the server.
  sylv.DataImporter.sendNodes = function(url, nodes) {
    var queue = [],
        deferred = $.Deferred();

    for (var nodeId in nodes) {
      queue.push({
        id: nodeId,
        node: nodes[nodeId]
      });
    }

    processQueue(this, url, queue, deferred);

    function processQueue(self, url, queue, deferred) {
      var obj,
          jqxhr;

      if (queue.length > 0) {
        obj = queue.pop();
        jqxhr = self.sendNode(url, obj.node);

        jqxhr.done(function(response) {
          if (response) {
            self.serverNodes[obj.id] = response.id;
            processQueue(self, url, queue, deferred);
          }
        });
      } else {
        deferred.resolve();
      }
    }

    return deferred.promise();
  };


  // Send edges to the server.
  sylv.DataImporter.sendEdges = function(url, edges) {
    var queue = edges.slice(0),
        deferred = $.Deferred();

    processQueue(this, url, queue, deferred);

    function processQueue(self, url, queue, deferred) {
      var edge,
          jqxhr;

      if (queue.length > 0) {
        edge = queue.pop();
        jqxhr = self.sendEdge(url, edge);

        jqxhr.done(function() {
          processQueue(self, url, queue, deferred);
        });
      } else {
        deferred.resolve();
      }
    }

    return deferred.promise();
  };


  // Send nodes and edges to the server.
  sylv.DataImporter.sendGraph = function(nodes, edges, nodesUrl, edgesUrl) {
    var promiseNodes,
        promiseEdges,
        self = this;

    promiseNodes = this.sendNodes(nodesUrl, nodes);

    promiseEdges = promiseNodes.then(function() {
      return self.sendEdges(edgesUrl, edges);
    });

    return promiseEdges;
  };


  // CSV import.
  sylv.DataImporter.loadCSV = function(nodesFiles, edgesFiles) {
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
              i, li, j, lj;

          console.log('Processing nodes...');

          rows = getRows(event.target.result);

          if (rows.length > 0) {
            csvHeader = getColumns(rows[0]);

            for (i = 1, li = rows.length; i < li; i++) {
              columns = getColumns(rows[i]);

              properties = {};
              for (j = 2, lj = columns.length; j < lj; j++) {
                properties[csvHeader[j]] = columns[j];
              }

              self.addNode(columns[0], columns[1], properties);
            }
          }

          if (sylv.DataImporter.nodesLength > 0) {
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
                i, li, j, lj;

            console.log('Processing edges...');

            rows = getRows(event.target.result);
            csvHeader = getColumns(rows[0]);

            for (i = 1, li = rows.length; i < li; i++) {
              columns = getColumns(rows[i]);

              properties = {};
              for (j = 3, lj = columns.length; j < lj; j++) {
                properties[csvHeader[j]] = columns[j];
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
  sylv.DataImporter.loadGEXF = function(file) {
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
        var attribute, attributeId, attributeTitle;
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
                  attributeTitle = attribute.title;
                  nodeAttributes[attributeTitle] =
                      attvalueNode.getAttribute('value');
                }
              }
            }

            sylv.DataImporter.addNode(nodeId, nodeType, nodeAttributes);
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
                  attributeTitle = attribute.title;
                  edgeAttributes[attributeTitle] =
                      attvalueEdge.getAttribute('value');
                }
              }
            }

            sylv.DataImporter.addEdge(edgeSource, edgeTarget, edgeLabel,
                                      edgeAttributes);
          }
        }

        if (sylv.DataImporter.nodesLength > 0) {
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

}(jQuery, window, document));