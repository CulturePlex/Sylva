var reportsServices = angular.module('reportsServices', ['ngResource']);


reportsServices.factory('api', ['$resource', function ($resource) {
    var reports = $resource('/reports/:graphSlug/report-builder', {}, {
        query: {method:'GET', params: {reports: 'graph'}, isArray:true},
        save: {method:'POST'}
    });

    var queries = $resource('/reports/:graphSlug/queries', {}, {
        query: {method:'GET', params: {queries: 'graph'}, isArray:true}
    });

    return {
        reports: reports,
        queries: queries
    };
}]);
