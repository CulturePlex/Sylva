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

    function TableArray(tableArray) {
        this.tableArray = tableArray  
    };

    TableArray.prototype.findAdjCells = function(row, col) {
        var adjs = [];
        if (this.tableArray[row][col - 1]) adjs.push('left');
        if (row !== 0 && this.tableArray[row - 1][col]) adjs.push('up');
        if (this.tableArray[row][col + 1]) adjs.push('right');
        if (row < this.tableArray.length - 1 && this.tableArray[row + 1][col]) adjs.push('down');
        return adjs;
    };

    TableArray.prototype.addRow = function(tr) {
        // will improve efficiency, maybe worth it to implement
        var row = mapper(tr);
        this.tableArray.push(row);                
    };

    TableArray.prototype.jsonify = function() {
        console.log('jsonify')
    }

      
    return function (table, ang) {
        return new TableArray(table, ang);
    }
});