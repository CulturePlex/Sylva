var reportsServices = angular.module('reportsServices', ['ngResource']);


reportsServices.factory('api', ['$resource', function ($resource) {
    var reports = $resource('/reports/report-builder', {}, {
        query: {method:'GET', params: {graph: 'graph'}, isArray:true},
        save: {method:'POST'}
    });

    var queries = $resource('/reports/queries', {}, {
        query: {method:'GET', isArray:true}
    });

    return {
        reports: reports,
        queries: queries
    };
}]);
