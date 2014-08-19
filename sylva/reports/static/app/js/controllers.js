'use strict'


var controllers = angular.module('reports.controllers', []);


controllers.controller('ReportListCtrl', [
    '$scope',
    '$location',
    'api', 
    'parser',
    function ($scope, $location, api, parser, DjangoConst) {
        // Done
        $scope.graph = parser.parse();
        $scope.templates = api.templates.list({graphSlug: $scope.graph});
}]);


controllers.controller('BaseReportCtrl', [
    '$scope',
    '$location',
    '$routeParams', 
    'GRAPH',
    'api',
    function ($scope, $location, $routeParams, GRAPH, api) {

        $scope.slugs = {
            graph: GRAPH, 
            template: $routeParams.reportSlug
        };
        // Thess variables may be necessary
        $scope.template = {};
        $scope.queries = [];
        $scope.tableArray = [];
        //////////////////////////////////

        $scope.designReport = function () {
            // Using is report form - edit and new ctrls
            $scope.editable = true;

        };

        $scope.editMeta = function () {
            $scope.editable = false;
        }

        $scope.getQuery = function(name) {
            // Preview controller - check
            return $scope.queries.filter(function (el) {
                return el['name'] === name
            });
        };

        $scope.saveReport = function (report) {
            // Used in report form - both edit and new ctrls
            //var post = new api.templates();
            //post.report = $scope.report;
            //post.table = $scope.tableArray;
            console.log('report', report)
            console.log('tableArray', $scope.tableArray)
            //post.$save({graphSlug: $scope.slugs.graph}, function (data) {
            //    console.log('data', data)
            //    var redirect = '/';
            //    $location.path(redirect);
            //});
        };
}]);


controllers.controller('NewReportCtrl', [
    '$scope', 
    '$controller',
    'api',
    function ($scope, $controller, api) {
        // Done except post
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.template = {
            name: 'New Report',
            periodicity: 'weekly',
            start_time: '',
            start_date: '',
            description: '',
            nameHtml: '<h2>New Report</h2>',
        };

        var layout = [[{"col": 0, "colspan": "1", "id": "cell1", "row": 0, 
                       "rowspan": "1", "displayQuery": "", "chartType": "",
                       "series": ""}, 
                      {"col": 1, "colspan": "1", "id": "cell2", "row": 0,
                       "rowspan": "1", "displayQuery": "", "chartType": "",
                       "series": ""}], 
                    [{"col": 0, "colspan": "1", "id": "cell3", "row": 1,
                      "rowspan": "1","displayQuery": "", "chartType": "",
                       "series": ""}, 
                     {"col": 1, "colspan": "1", "id": "cell4", "row": 1,
                      "rowspan": "1", "displayQuery": "", "chartType": "",
                       "series": ""}]]
        api.templates.blank({
            graphSlug: $scope.slugs.graph, 
        }, function (data) {
            $scope.template = data;
            $scope.resp = {table: layout, queries: data.queries}
        });
}]);


controllers.controller('EditReportCtrl', [
    '$scope', 
    '$controller',
    'api',
    function ($scope, $controller, api) {
        // Done except post
        $controller('BaseReportCtrl', {$scope: $scope});
        api.templates.edit({
            graphSlug: $scope.slugs.graph,
            template: $scope.slugs.template
        }, function (data) {
            $scope.template = data.template;
            $scope.resp = {table: data.template.layout, queries: data.queries}
        });
}]);


controllers.controller('ReportPreviewCtrl', [
    '$scope',
    '$controller',
    'api',
    'parser',
    function ($scope, $controller, api, parser) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.pdf = parser.pdf();
        api.templates.preview({
            graphSlug: $scope.slugs.graph,
            template: $scope.slugs.template  
        }, function (data) {
            console.log('data', data)
            $scope.template = data.template;
            $scope.resp = {table: data.template.layout, queries: data.queries}
        });
}]);


controllers.controller('ReportHistoryCtrl', [
    '$scope',
    '$controller',
    'api',
    function ($scope, $controller, api) {
        $controller('BaseReportCtrl', {$scope: $scope});
        api.history.history({
            graphSlug: $scope.slugs.graph,
            template: $scope.slugs.template 
        }, function (data) {
            $scope.template = data;
            $scope.getReport(data.history[0].slug)
        });

        $scope.getReport = function (slug) {
            api.history.report({
                graphSlug: $scope.slugs.graph,
                report: slug
            }, function (data) {
                console.log('report', data)
                $scope.report = data;
                $scope.resp = {table: data.table}
            });
        }
}]);
