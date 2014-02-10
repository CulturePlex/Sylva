var reports = angular.module('reports', [
    'ngCookies',
    'ngRoute',
    'ngSanitize',
    'reports.controllers',
    'reports.services',
    'reports.directives', 
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
            when('/', {
                templateUrl: '/static/app/partials/reports.html',
                controller: 'ReportListCtrl'
            }).
            when('/new', {
                templateUrl: '/static/app/partials/report_form.html',
                controller: 'NewReportCtrl'
            }).
            when('/edit/:reportSlug', {
                templateUrl: '/static/app/partials/report_form.html',
                controller: 'EditReportCtrl'
            }).when('/history/:reportSlug', {
                templateUrl: '/static/app/partials/report_history.html',
                controller: 'ReportHistoryCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
}]).

run([
    '$http', 
    '$cookies', 
    function($http, $cookies, $timeout) {
            $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}]);
