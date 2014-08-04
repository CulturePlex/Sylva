'use strict'


var controllers = angular.module('reports.controllers', []);


controllers.controller('ReportListCtrl', [
    '$scope',
    '$location',
    'api', 
    'parser',
    function ($scope, $location, api, parser, DjangoConst) {
        $scope.graph = parser.parse();
        $scope.reports = api.reports.query({graphSlug: $scope.graph});
}]);


controllers.controller('BaseReportFormCtrl', [
    '$scope',
    '$location',
    '$routeParams', 
    'api',
    'parser',
    'tableArray',
    function ($scope, $location, $routeParams, api, parser, tableArray) {

        $scope.graph = parser.parse();
        $scope.report = {};
        $scope.queries = [];


        $scope.report.slug = $routeParams.reportSlug;

        $scope.designReport = function () {
            $scope.editable = true;

        };

        $scope.editMeta = function () {
            $scope.editable = false;
        }

        $scope.getQuery = function(name) {
            return $scope.queries.filter(function (el) {
                return el['name'] === name
            });
        };

        $scope.removeQuery = function (key) {
            $scope.report.queries[key] = undefined;
        };

        $scope.saveReport = function (report) {
            var post = new api.reports();
            post.report = $scope.report;
            post.table = $scope.tableArray;

            post.$save({graphSlug: $scope.graph}, function (data) {
                console.log('data', data)
                var redirect = '/';
                $location.path(redirect);
            });
        };
}]);


controllers.controller('NewReportCtrl', [
    '$scope', 
    '$controller',
    'api',
    'tableArray',
    '$sce',
    function ($scope, $controller, api, tableArray, $sce) {
        $controller('BaseReportFormCtrl', {$scope: $scope});
        $scope.report = {
            name: 'New Report',
            slug: $scope.report.name,
            periodicity: 'weekly',
            start_time: '',
            start_date: '',
            description: '',
            // move this to directive
            nameHtml: '<h2>New Report</h2>',
        };
}]);


controllers.controller('EditReportCtrl', [
    '$scope', 
    '$routeParams',
    '$controller',
    'api',
    'tableArray',
    function ($scope, $routeParams, $controller, api, tableArray) {
        $controller('BaseReportFormCtrl', {$scope: $scope});
        $scope.report.slug = $routeParams.reportSlug;
        $scope.tableArray = [];
        api.reports.query({
            graphSlug: $scope.graph,
            slug: $scope.report.slug  
        }, function (data) {
            $scope.report = data[0];
            $scope.resp = {table: $scope.report.table, queries: $scope.report.queries}
        });
}]);


controllers.controller('ReportHistoryCtrl', [
    '$scope',
    '$routeParams',
    'api',
    'parser',
    function ($scope, $routeParams, api, parser) {
        $scope.report = {};
        $scope.graph = parser.parse();
        $scope.report.slug = $routeParams.reportSlug;
        api.reports.query({
            graphSlug: $scope.graph,
            slug: $scope.report.slug  
        }, function (data) {
            $scope.report = data[0];
            if ($scope.report.history != undefined) {
                $scope.currentContext = $scope.report.history.sort(function (a, b) {
                    if (a.date < b.date) return 1;
                    if (a.date > b.date) return -1;
                    return 0;
                })[0];
            }
        });

        $scope.updateContext = function (contextID) {
            $scope.currentContext = $scope.report.history.filter(function (element) {
                return element.id === contextID;
            })[0];
        }
}]);

controllers.controller('ReportPreviewCtrl', [
    '$scope',
    '$routeParams',
    'api',
    'parser',
    'tableArray',
    function ($scope, $routeParams, api, parser, tableArray) {
        $scope.report = {};
        $scope.graph = parser.parse();
        $scope.pdf = parser.pdf();
        $scope.report.slug = $routeParams.reportSlug;
        console.log('params', $scope.report.slug)
            api.reports.query({
                graphSlug: $scope.graph,
                slug: $scope.report.slug  
            }, function (data) {
                $scope.report = data[0];
                $scope.resp = {table: $scope.report.table, queries: $scope.report.queries}
            });

        $scope.editable = true; // this for now to deal with table width
        $scope.getQuery = function(name) {
            return $scope.queries.filter(function (el) {
                return el['name'] === name
            });
        };
    }]);