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

    return new Parser()
}]);

services.factory('tableArray', function () {

    function TableArray() {
        this;
    };

    TableArray.prototype.addTable = function(table) {
        this.table = table;
        console.log('serviceTable', table.children()[0].children())
    };

    TableArray.prototype.addRow = function() {
        console.log('adding row')
    };

    TableArray.prototype.addCol = function() {
        console.log('adding col')
    };

    TableArray.prototype.jsonify = function() {
        console.log('jsonify')
    }

    return function () {
        return new TableArray()
    }
    
});


services.service('breadcrumbs', function () {
    this.breadcrumb = '';
    var setBreadcrumb = function (breadcrumb) {
        this.breadcrumb = breadcrumb
    };

});
