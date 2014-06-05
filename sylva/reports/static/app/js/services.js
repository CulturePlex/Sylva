'use strict'


var services = angular.module('reports.services', ['ngResource']);

services.factory('api', ['$resource', function ($resource) {

    var reports = $resource('/reports/:graphSlug/reports', {}, {
        query: {method:'GET', isArray:true},
        save: {method:'POST'}
    });

    var queries = $resource('/reports/:graphSlug/queries', {}, {
        query: {method:'GET', isArray:true}
    });

    //var queryContext = queries.query()
    return {
        reports: reports,
        queries: queries
    };
}]);


services.factory('parser', ['$location', function ($location) {

    function Parser() {
        this.parser = document.createElement('a')
        this.parser.href = $location.absUrl();
    }

    Parser.prototype.parse = function () {
        return this.parser.pathname.split('/')[2]
    }

    Parser.prototype.pdf = function () {
        var pdf;
        try {
            var match = this.parser.href.match(/pdf=(\w*)/)[1]
            if (match === 'true') pdf = true;
        } catch (e) {
            pdf = false;
        }
    return pdf
    }

    return new Parser();
}]);


services.factory('tableArray', function () {

    function TableArray(table) {
        this.table = table;
        this.numRows = table.length;
        this.numCols = getNumCols(table[0]);
    };

    function getNumCols(row) {
        var count = 0;
        angular.forEach(row, function (el) {
            count += parseInt(el.colspan)
        });
        return count;
    }

    TableArray.prototype.getAdjCells = function(row, col) {
        //var upMerge = this.rowMerge(row, col, 'up');
        //var downMerge = this.rowMerge(row, col, 'down');
        var adjs = [];
        if (this.table[row][col - 1]) adjs.push('left');
        //if (upMerge) adjs.push('up');
        if (this.table[row][col + 1]) adjs.push('right');
        //if (downMerge) adjs.push('down');
        return adjs;
    };

    //TableArray.prototype.rowMerge = function(row, col, dir) {
    //    var merge = false
    //    ,   thisRow = this.table[row]
    //    ,   cellPos = 0
    //    ,   mergePos = 0
    //    ,   direction = {up: row - 1, down: row + 1}
    //    for (var i=0; i<col; i++) {
    //        cellPos += parseInt(thisRow[i].colspan)
    //    }
    //    if (this.table[direction[dir]]) {
    //        var mergeRow = this.table[direction[dir]]
    //        ,   j = 0;
    //        while (mergePos<cellPos) {
    //            mergePos += parseInt(mergeRow[j].colspan)
    //            j++;
    //        }
    //        console.log('pos', mergePos, cellPos, j)
    //        if (mergePos === cellPos && thisRow[col].colspan === mergeRow[j].colspan) merge = true;
    //    }
        
    //    return merge
    //}

    TableArray.prototype.addRow = function() { 
        var row = []
        ,   cellId = this.getId();
        for (var i=0; i<this.numCols; i++) {
            var cell = {
                col: i,
                colspan: '1',
                id: 'cell' + cellId,
                row: this.numRows,
                rowspan: '1',
                query: ''
            };
            row.push(cell);
            cellId++;
        }   
        this.table.push(row); 
        this.numRows++;     
    };

    TableArray.prototype.addCol = function() {
        var cellId = 0;
        for (var i=0; i<this.numRows; i++) {
            var row = this.table[i]
            ,   rlen = row.length
            ,   cell = {
                col: rlen,
                colspan: '1',
                id: '',
                row: i,
                rowspan: '1',
                query: ''
            };
            row.push(cell);
            var newRlen = rlen + 1;
            for (var j=0; j<newRlen; j++) {
                row[j].id = 'cell' + cellId;
                cellId++;
            }     
        }
        this.numCols++;
    };

    TableArray.prototype.delRow = function() {
        // will have to update for verticle merge
        var ndx = this.table.length - 1;
        this.table.splice(ndx, 1);
        this.numRows -= 1;
    }

    TableArray.prototype.delCol = function() {
        var self = this;
        this.table.map(function (el) {
            var lastCell = el[el.length - 1]
            if (lastCell.colspan > 1) {
                lastCell.colspan = lastCell.colspan - 1;
            } else {
                el.splice(el.length - 1, 1);
            }
        });
        this.numCols -= 1;     
    }

    TableArray.prototype.addQuery = function(coords, query) {
        this.table[coords[0]][coords[1]].displayQuery = query;
    }

    TableArray.prototype.addChart = function(coords, chart) {
        this.table[coords[0]][coords[1]].chartType = chart;
    }

    TableArray.prototype.delQuery = function(coords) {
        this.table[coords[0]][coords[1]].query = '';
    }

    TableArray.prototype.mergeCol = function(coords) {
        var cds = coords[0]
        ,   mrgCds = coords[1]
        ,   mrgRow = this.table[cds[0]]
        ,   cell = this.table[cds[0]][cds[1]]
        ,   mrgCell = this.table[mrgCds[0]][mrgCds[1]];
        mrgRow.splice(mrgCds[1], 1);
        cell.colspan = parseInt(cell.colspan);
        cell.colspan += parseInt(mrgCell.colspan);
        this.table[cds[0]] = mrgRow;
    };

    // MABE JUST MERGE THIS WITH PREVIOUS METHOD
    //TableArray.prototype.mergeRow = function(coords) {
    //    var cds = coords[0]
    //    ,   mrgCds = coords[1]
    //    ,   mrgRow = this.table[mrgCds[0]]
    //    ,   cell = this.table[cds[0]][cds[1]]
    //    ,   mrgCell = this.table[mrgCds[0]][mrgCds[1]];
    //    console.log('MERGER',  mrgRow,  mrgCds)
        //mrgRow.splice(mrgCds[1], 1);
    //    cell.rowspan = parseInt(cell.rowspan);
    //    cell.rowspan += parseInt(mrgCell.rowspan);
    //    mrgCell.rowspan = 0;
    //};

    TableArray.prototype.getId = function() {
        var id = 0
        ,   tlen = this.table.length;
        for (var i=0; i<tlen; i++) {
            id += this.table[i].length
        }
        return id;
    };

    TableArray.prototype.displayHtml = function(rowWidth) {
        // maybe fix width here later
        var html = ''; 
        for (var i=0; i<this.numRows; i++) {
            var row = this.table[i]
            ,   rlen = row.length
            ,   cells = '';
            for (var j=0; j<rlen; j++) {
                var cell = row[j]
                ,   width = (rowWidth / this.numCols - ((this.numCols + 1) * 2 / this.numCols)) * cell.colspan + (2 * (cell.colspan - 1)) + 'px' 
                // will implement later
                if (cell.rowspan === 0) {
                    var height = '0px'
                } else {
                   var height = 175 * cell.rowspan - 2 * this.numRows + (cell.rowspan -1) * 2 + 'px';
                }
                if (j === rlen - 1) {
                    cells += '<div sylva-display-cell class="tcell final" id=' + cell.id + 
                        '" style="width:' + width + 
                        '; height:' + height +
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '" query="' + cell['query'] +
                        '">';
                    //if (cell.query  !== '') {
                    //    cells += '<div>' + '<h2>' + cell.query + '</h2>' + '</div>';
                    //}
                    cells += '</div>'
                } else {
                    cells += '<div sylva-display-cell class="tcell" id=' + cell.id + 
                        '" style="width:' + width + 
                        '; height:' + height +
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '" query="' + cell['query'] +
                        '">';
                    //if (cell.query !== '') {
                    //    cells += '<div>' + '<h2>' + cell.query + '</h2>' + '</div>';
                    //}
                    cells += '</div>'
                }
            }
            if (i === this.numRows - 1) {
                html += '<div class="trow bottom">' + cells + '</div>';
            } else {
                html += '<div class="trow">' + cells + '</div>';
            }
        }
        return html;
    };

    TableArray.prototype.htmlify = function(rowWidth) {
        var html = ''; 
        for (var i=0; i<this.numRows; i++) {
            var row = this.table[i]
            ,   rlen = row.length
            ,   cells = '';
            for (var j=0; j<rlen; j++) {
                var cell = row[j]
                ,   width = (rowWidth / this.numCols - ((this.numCols + 1) * 2 / this.numCols)) * cell.colspan + (25 * (cell.colspan - 1)) + 'px'
                // will implement later
                if (cell.rowspan === 0) {
                    var height = '0px'
                } else {
                   var height = 175 * cell.rowspan - 2 * this.numRows + (cell.rowspan -1) * 2 + 'px';
                }
                if (j === rlen - 1) {
                    cells += '<div sylva-droppable sylva-merge-cells class="tcell final" id=' + cell.id + 
                        '" style="width:' + width + 
                        '; height:' + height +
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '" query="' + cell['query'] +
                        '">';
                    cells += '</div>'
                } else {
                    cells += '<div sylva-droppable sylva-merge-cells class="tcell" id=' + cell.id + 
                        '" style="width:' + width +
                        '; height:' + height + 
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '" query="' + cell['query'] +
                        '">';
                    cells += '</div>'
                }
            }
            if (i === this.numRows - 1) {
                html += '<div class="trow bottom">' + cells + '</div>';
            } else {
                html += '<div class="trow">' + cells + '</div>';
            }
        }
        return html;
    };

    TableArray.prototype.jsonify = function() {
        console.log('jsonify')
    };

    return function (table) {
        return new TableArray(table);
    }
});

