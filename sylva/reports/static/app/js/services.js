var reportsServices = angular.module('reportsServices', ['ngResource']);


reportsServices.factory('api', ['$resource', function ($resource) {
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
