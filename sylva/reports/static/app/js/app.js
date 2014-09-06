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



// Basic interceptor (will need for api interaction, 
// this is the new interceptors api)
reports.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.interceptors.push(function($q) {
        return {
            // optional method
            'request': function(config) {
                // do something on success
                //console.log('config', config)
                return config || $q.when(config);
            },
     
            // optional method
            'requestError': function(rejection) {
                // do something on error
                if (canRecover(rejection)) {
                    return responseOrNewPromise
                }
                return $q.reject(rejection);
            },
     
            // optional method
            'response': function(response) {
                // do something on success
                //console.log('response', response)
                return response || $q.when(response);
            },
     
            // optional method
            'responseError': function(rejection) {
                // do something on error
                if (canRecover(rejection)) {
                    return responseOrNewPromise
                }
                return $q.reject(rejection);
            }
        };
    });

}]);


// Django settings.
reports.run([
    '$http', 
    '$cookies', 
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
}]);
