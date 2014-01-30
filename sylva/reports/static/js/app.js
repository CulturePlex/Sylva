var reports = angular.module('reports', [
    'reportsControllers',
    'reportsServices',
    'reportsDirectives', 
    'ngCookies'
]);


reports.config([
    '$httpProvider', 
    '$interpolateProvider', 
    function($httpProvider, $interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
        $httpProvider.defaults.headers.post['Content-Type'] = 
                                    'application/x-www-form-urlencoded';
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    }]).
    run([
    '$http', 
    '$cookies', 
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    }]);
