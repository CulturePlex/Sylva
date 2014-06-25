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
    'STATIC_PREFIX',
    function($routeProvider, STATIC_PREFIX) {
        console.log('DC', STATIC_PREFIX)
        $routeProvider.
            when('/', {
                templateUrl: STATIC_PREFIX + 'app/partials/reports.html',
                controller: 'ReportListCtrl'
            }).
            when('/new', {
                templateUrl: STATIC_PREFIX + 'app/partials/report_form.html',
                controller: 'NewReportCtrl'
            }).
            when('/edit/:reportSlug', {
                templateUrl: STATIC_PREFIX + 'app/partials/report_form.html',
                controller: 'EditReportCtrl'
            }).when('/history/:reportSlug', {
                templateUrl: STATIC_PREFIX + 'app/partials/report_history.html',
                controller: 'ReportHistoryCtrl'
            }).when('/preview/:reportSlug', {
                templateUrl: STATIC_PREFIX + 'app/partials/report_preview.html',
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
