var reports = angular.module('reports', [
    'ngCookies',
    'ngRoute',
    'reportsControllers',
    'reportsServices',
    'reportsDirectives', 
    'datePicker'
]);


reports.config([
    '$httpProvider', 
    '$interpolateProvider', 
    '$routeProvider',
    function($httpProvider, $interpolateProvider, $routeProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $routeProvider.
            when('/:graphid', {
                templateUrl: '/static/app/partials/reports.html',
                controller: 'ReportListCtrl'
            }).
            when('/:graphid/edit/:reportid', {
                templateUrl: '/static/app/partials/edit_report.html',
                controller: 'EditReportCtrl'
            });

    }]).

    run([
    '$http', 
    '$cookies', 
    function($http, $cookies, $timeout) {
            $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    }]);
