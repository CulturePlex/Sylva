'use strict'


var controllers = angular.module('reports.controllers', []);


controllers.controller('ReportListCtrl', [
    '$scope',
    '$location',
    'api', 
    'parser',
    function ($scope, $location, api, parser) {
        $scope.graph = parser.parse();
        var periods = {h: 'Hourly', d: 'Daily', w: 'Weekly' , m: 'Monthly'}
        $scope.getPage = function (pageNum) {
            api.templates.list({page: pageNum}, function (data) {
                $scope.data = data;
                var len = data.templates.length;
                for (var i=0;i<len;i++) {
                    var template = data.templates[i]
                    ,   date = JSON.parse(template.start_date)
                    ,   datetime = new Date(date)
                    ,   last_run = JSON.parse(template.last_run)
                    ,   periodicity = template.frequency;
                    template.start_date = datetime.toString();
                    template.frequency = periods[periodicity];
                    if (last_run) {
                        var last_datetime = new Date(last_date)
                        ,   last_run = last_datetime.toString();
                    }
                    template.last_run = last_run;
                }
            });
        }

        $scope.getPage(1)
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
        //////////////////////////////////

        $scope.designReport = function () {
            // Using is report form - edit and new ctrls
            $scope.editable = true;
        };

        $scope.editMeta = function () {
            $scope.editable = false;
        }

        $scope.saveReport = function (template) {
            // Used in report form - both edit and new ctrls
            // Gonna have to validate here
            var date = template.date.split('/')
            ,   time = template.time.split(':')
            ,   datetime = new Date(date[2], date[1] - 1, date[0], time[0], time[1])
            ,   post = new api.builder();
            template.start_date = datetime.toISOString()
            post.template = template
            post.$save({
                graphSlug: $scope.slugs.graph,
                report: template.slug
            }, function (data) {
                var redirect = '/';
                $location.path(redirect);
            }); // What if post fails
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
            data.layout = layout;
            $scope.template.layout = layout;
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
            var date = JSON.parse(data.template.start_date)
            ,   datetime = new Date(date)
            ,   m = datetime.getMonth() + 1
            ,   month = m.toString()
            ,   day = datetime.getDate().toString()
            ,   year = datetime.getFullYear().toString()
            ,   hour = datetime.getHours().toString()
            ,   minute = datetime.getMinutes().toString();

            if (month.length === 1) month = '0' + month;
            if (day.length === 1) day = '0' + day;
            if (hour.length === 1) hour = '0' + hour;
            if (minute.length === 1) minute = '0' + minute;

            data.template.time = hour + ':' + minute;
            data.template.date = day + '/' + month + '/' + year;

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
            template: $scope.slugs.template,  
        }, function (data) {
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
            for (var i=0; i<data.history.length; i++) {
                var report = data.history[i]
                ,   date = JSON.parse(report.date_run)
                ,   datetime = new Date(date)
                report.date_run = datetime.toString()
            }
            $scope.template = data;
            if (data.history.length > 0) $scope.getReport(data.history[0].id)
        });

        $scope.getReport = function (id) {
            api.history.report({
                graphSlug: $scope.slugs.graph,
                report: id
            }, function (data) {
                $scope.report = data;
                $scope.resp = {table: data.table}
            });
        }
}]);
