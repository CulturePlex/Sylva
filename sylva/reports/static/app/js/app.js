'use strict'


var reports = angular.module('reports', [
    'ngCookies',
    'ngRoute',
    'ngSanitize',
    'highcharts-ng',
    'reports.controllers',
    'reports.services',
    'reports.directives', 
]);


// Django settings.
reports.config([
    '$httpProvider',

    function($httpProvider) {
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
}]);



// Routing.
reports.config([ 
    '$routeProvider',
    'DJANGO_URLS',
    function($routeProvider, DJANGO_URLS) {
        console.log('DC', DJANGO_URLS)
        $routeProvider.
            when('/', {
                templateUrl: DJANGO_URLS.partials + '?name=reports',
                controller: 'ReportListCtrl'
            }).
            when('/new', {
                templateUrl: DJANGO_URLS.partials + '?name=report_form',
                controller: 'NewReportCtrl'
            }).
            when('/edit/:reportSlug', {
                templateUrl: DJANGO_URLS.partials + '?name=report_form', 
                controller: 'EditReportCtrl'
            }).
            when('/history/:reportSlug', {
                templateUrl: DJANGO_URLS.partials + '?name=report_history',
                controller: 'ReportHistoryCtrl'
            }).
            when('/preview/:reportSlug', {
                templateUrl: DJANGO_URLS.partials + '?name=report_preview',
                controller: 'ReportPreviewCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
}]);


// Django settings.
reports.run([
    '$http', 
    '$cookies', 
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}]);
