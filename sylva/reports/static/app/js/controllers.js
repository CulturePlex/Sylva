'use strict'


var controllers = angular.module('reports.controllers', []);


controllers.controller('ReportListCtrl', [
    '$scope',
    '$location',
    'api', 
    'parser',
    function ($scope, $location, api, parser) {
        $scope.graph = parser.parse();
        $scope.reports = api.reports.query({graphSlug: $scope.graph});
    
}]);


controllers.controller('BaseReportFormCtrl', [
    '$scope',
    '$location', 
    'api',
    'parser',
    'tableArray', 
    function ($scope, $location, api, parser, tableArray) {
        $scope.graph = parser.parse();
        $scope.queries = [];
        $scope.report = {
            table: null
        };
        $scope.tCells = [];

        $scope.designReport = function () {
            api.queries.query({graphSlug: $scope.graph}, function (data) {
                $scope.queries = data;
            });
            $scope.editable = true;  
        };

        $scope.editMeta = function () {
            $scope.queries = [];
            $scope.editable = false;
        }

        $scope.handleDrop = function (binId, drop) {
            console.log('drop')
            if ($scope.report.queries[binId] === undefined) {
                $scope.report.queries[binId] = drop;
            }
        }; 

        $scope.format = function () {
            $scope.report.table = false;
        }

        $scope.removeQuery = function (key) {
            $scope.report.queries[key] = undefined;
        };

        $scope.saveReport = function (report) {
            var post = new api.reports();
            post.report = $scope.report;
            post.$save({graphSlug: $scope.graph}, function (data) {
                console.log(data)
                var redirect = '/';
                $location.path(redirect);
            });
        };

        $scope.mergeCells = function(coords) {
            console.log('merge', coords)
        }

        $scope.addRow = function() {
            //$scope.tableArray.addRow()
        }

        $scope.addCol = function() {
            //$scope.tableArray.addCol()
        }
}]);


controllers.controller('NewReportCtrl', [
    '$scope', 
    '$controller',
    function ($scope, $controller) {
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
            queries: {}
        };
}]);


controllers.controller('EditReportCtrl', [
    '$scope', 
    '$routeParams',
    '$controller',
    'api',
    function ($scope, $routeParams, $controller, api) {
        $controller('BaseReportFormCtrl', {$scope: $scope});
        $scope.report.slug = $routeParams.reportSlug;
        api.reports.query({
            graphSlug: $scope.graph,
            slug: $scope.report.slug  
        }, function (data) {
            $scope.report = data[0];
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
            console.log(data)
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