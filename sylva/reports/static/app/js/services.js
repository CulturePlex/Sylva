'use strict'


var services = angular.module('reports.services', ['ngResource']);

services.factory('api', ['$resource',  'DJANGO_URLS', function ($resource, DJANGO_URLS) {


    var list = $resource(DJANGO_URLS.list, {}, {
        list: {method:'GET'}
    });

    var templates = $resource(DJANGO_URLS.templates, {}, {
        blank: {method:'GET', params: {queries: true}},
        edit: {method:'GET', params: {queries: true}},
        preview: {method:'GET'}
    });

    var history = $resource(DJANGO_URLS.history, {}, {
        history: {method: 'GET'},
        report: {method: 'GET'}
    });

    var del = $resource(DJANGO_URLS.del, {}, {
        get: {method: 'GET'}
    });

    var builder = $resource(DJANGO_URLS.builder, {}, {});

    return {
        templates: templates,
        history: history,
        builder: builder,
        list: list,
        del: del
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

    TableArray.prototype.addAxis = function(coords, axis, alias) {
        if (axis === 'x') {
            this.table[coords[0]][coords[1]].xAxis = alias;
        } else {
            this.table[coords[0]][coords[1]].yAxis.push(alias);
        }
    }

    TableArray.prototype.removeAxis = function(coords, axis, alias) {
        if (axis === 'y') {
            if (!('yAxis' in this.table[coords[0]][coords[1]])) {
                this.table[coords[0]][coords[1]]['yAxis'] = []
            }
            var i = this.table[coords[0]][coords[1]].yAxis.indexOf(alias)
            this.table[coords[0]][coords[1]].yAxis.splice(i, 1);
            this.table[coords[0]][coords[1]].yAxis = this.table[coords[0]][coords[1]].yAxis.filter(function (el) {
                return el.alias !== alias;
            });

        } else {
            this.table[coords[0]][coords[1]].xAxis = null;
        }
    }

    TableArray.prototype.addMarkdown = function(coords, markdown) {
        this.table[coords[0]][coords[1]].displayMarkdown = markdown;
    }

    TableArray.prototype.addChart = function(coords, chart) {
        this.table[coords[0]][coords[1]].chartType = chart;
    }

    TableArray.prototype.delQuery = function(coords) {
        this.table[coords[0]][coords[1]].query = '';
    }

    TableArray.prototype.collapseCol = function (coords, dir) {
        var colspan = this.table[coords[0]][coords[1]].colspan
        this.table[coords[0]][coords[1]].colspan = parseInt(colspan) - 1;
        var cell = {
                colspan: '1',
                id: '',
                row: i,
                rowspan: '1',
                query: ''
        };
        if (dir === 1) {
            cell.col = coords[1] + 1
            this.table[coords[0]].splice(coords[1] + 1, 0, cell)
        } else {
            cell.col = coords[1]
            this.table[coords[0]].splice(coords[1], 0, cell)
        }
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

    TableArray.prototype.getId = function() {
        var id = 0
        ,   tlen = this.table.length;
        for (var i=0; i<tlen; i++) {
            id += this.table[i].length
        }
        return id;
    };

    return function (table) {
        return new TableArray(table);
    }
});


services.factory('breadService', ['$rootScope', function ($rootScope) {
    var breadcrumbs = {
        design: function() {
            $rootScope.$broadcast('design')
        },
        meta: function() {
            $rootScope.$broadcast('meta')
        },
        updateName: function(newVal) {
            $rootScope.$broadcast('name', newVal);
        },
        editing: function (newVal) {
            $rootScope.$broadcast('editing', newVal);
        }
    }
    return breadcrumbs
}]);
