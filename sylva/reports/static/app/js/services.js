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

    return new Parser();
}]);


services.factory('tableArray', function () {

    function TableArray(table, rowWidth) {
        this.table = spanToInt(table);
        this.rowWidth = rowWidth;
        this.numRows = table.length;
        this.numCols = table[0].length;
        console.log('ta', this.table)
    };

    function spanToInt(table) {
        var tableLen = table.length;
        for (var i=0; i<tableLen; i++) {
            var row = table[i];
            row.map(function (el) {
                el.colspan = parseInt(el.colspan)
                el.rowspan = parseInt(el.rowspan)
                console.log('spans', typeof el.colspan, typeof el.rowspan)
            });
        }
        return table
    }

    TableArray.prototype.getAdjCells = function(row, col) {
        var adjs = [];
        if (this.table[row][col - 1]) adjs.push('left');
        if (row !== 0 && this.table[row - 1][col]) adjs.push('up');
        if (this.table[row][col + 1]) adjs.push('right');
        if (row < this.table.length - 1 && this.table[row + 1][col]) adjs.push('down');
        return adjs;
    };

    TableArray.prototype.addRow = function() { 
        var row = []
        ,   cellId = this.getId();
        for (var i=0; i<this.numCols; i++) {
            var cell = {col: i, colspan: '1', id: 'cell' + cellId, row: this.numRows, rowspan: '1'};
            row.push(cell)
            cellId++
        }   
        this.table.push(row) 
        this.numRows++     
    };

    TableArray.prototype.addCol = function() {
        var cellId = 0;
        console.log('numrows', this.numRows)
        for (var i=0; i<this.numRows; i++) {
            var row = this.table[i]
            ,   rlen = row.length
            ,   cell = {col: rlen, colspan: '1', id: '', row: i, rowspan: '1'};
            row.push(cell);
            //console.log('row', row)
            var newRlen = rlen + 1;
            for (var j=0; j<newRlen; j++) {
                row[j].id = 'cell' + cellId;
                cellId++;
            }     
        }
        this.numCols++;
    };

    TableArray.prototype.mergeCol = function(coords) {
        console.log('coords', coords)
        var cds = coords[0]
        ,   mrgCds = coords[1]
        ,   mrgRow = this.table[cds[0]]
        ,   cell = this.table[cds[0]][cds[1]]
        ,   mrgCell = this.table[mrgCds[0]][mrgCds[1]]
        console.log('befpr', mrgRow)
        mrgRow.splice(mrgCds[1], 1);
        console.log('after', mrgRow)
        console.log('cellinfo', cell)
        cell.colspan = parseInt(cell.colspan);
        cell.colspan += parseInt(mrgCell.colspan);
        this.table[cds[0]] = mrgRow;
        //console.log("cell merge", mrgCds[1])

    };

    TableArray.prototype.getId = function() {
        var id = 0
        ,   tlen = this.table.length;
        for (var i=0; i<tlen; i++) {
            id += this.table[i].length
        }
        return id;
    };

    TableArray.prototype.htmlify = function() {
        var html = ''; 
        // this will go to j loop to check for colspan etc.
        
        for (var i=0; i<this.numRows; i++) {
            var row = this.table[i]
            ,   rlen = row.length
            ,   cells = '';
            for (var j=0; j<rlen; j++) {
                var cell = row[j]
                ,   width = (this.rowWidth / this.numCols - ((this.numCols + 1) * 2 / this.numCols)) * cell.colspan + (2 * (cell.colspan - 1)) + 'px';
                //console.log('mergeinfo', cell.colspan, width)
                if (j === rlen - 1) {
                    cells += '<div sylva-droppable sylva-merge-cells class="tcell final" id=' + cell.id + 
                        '" style="width:' + width + 
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '"></div>';
                } else {
                    cells += '<div sylva-droppable sylva-merge-cells class="tcell" id=' + cell.id + 
                        '" style="width:' + width + 
                        ';" row="' + i +
                        '" rowspan="' + cell.rowspan +
                        '" col="' + j +
                        '" colspan="' + cell.colspan + 
                        '"></div>';
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

    return function (table, rowWidth) {
        return new TableArray(table, rowWidth);
    }
});

