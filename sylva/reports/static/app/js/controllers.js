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
                    ,   last_run = JSON.parse(template.last_run)
                    ,   periodicity = template.frequency
                    ,   datetime = new Date(date);
                    if (last_run) {
                        var last_datetime = new Date(last_run);
                        template.last_run = last_datetime.toUTCString().replace(/\s*(GMT|UTC)$/, "");
                    } else {
                        template.last_run = null;
                    }

                    template.start_date = datetime.toUTCString().replace(/\s*(GMT|UTC)$/, "");
                    template.frequency = periods[periodicity];
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
    'breadService',
    function ($scope, $location, $routeParams, GRAPH, api, breadService) {

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
            breadService.design()
        };

        $scope.editable;

        $scope.saveReport = function (template) {
            // Used in report form - both edit and new ctrls
            // Gonna have to validate here
            var date = template.date.split('/')
            ,   time = template.time.split(':')
            ,   datetime = new Date(date[2], date[1], date[0], time[0], time[1])
            ,   post = new api.builder();

            template.start_date = {year: date[2], month: date[0],
                                   day: date[1], hour: time[0], minute: time[1]}
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
            nameHtml: '<h2>New Report</h2>'
        };

        var exampleTable = [[{"col": 0, "colspan": "1", "id": "cell1", "row": 0, 
                             "rowspan": "1", "displayQuery": 1, "chartType": "pie",
                             "demo": "true", "series": [
                                ['Keanu Reeves',36],
                                ['Linus Torvalds',24],
                                ['Tyrion Lannister',20],
                                ['Morpheus',1],
                                ['Félix Lope de Vega Carpio',156],
                                ['Javier de la Rosa',24]
                            ]}, 
                            {"col": 1, "colspan": "1", "id": "cell2", "row": 0, 
                             "rowspan": "1", "displayQuery": 1, "chartType": "line",
                             "demo": "true","series": [
                                ['Keanu Reeves',36],
                                ['Linus Torvalds',24],
                                ['Tyrion Lannister',20],
                                ['Morpheus',1],
                                ['Félix Lope de Vega Carpio',156],
                                ['Javier de la Rosa',24]
                            ]}], 
                            [{"col": 0, "colspan": "1", "id": "cell3", "row": 1,
                             "rowspan": "1","displayQuery": 1, "chartType": "column",
                             "demo": "true", "series": [
                                ['Keanu Reeves',36],
                                ['Linus Torvalds',24],
                                ['Tyrion Lannister',20],
                                ['Morpheus',1],
                                ['Félix Lope de Vega Carpio',156],
                                ['Javier de la Rosa',24]
                            ]}, 
                            {"col": 1, "colspan": "1", "id": "cell4", "row": 1,
                             "rowspan": "1","displayQuery": 1, "chartType": "pie",
                             "demo": "true", "series": [
                                ['Keanu Reeves',36],
                                ['Linus Torvalds',24],
                                ['Tyrion Lannister',20],
                                ['Morpheus',1],
                                ['Félix Lope de Vega Carpio',156],
                                ['Javier de la Rosa',24]
                            ]}]];

        var layout = [[{"col": 0, "colspan": "1", "id": "cell1", "row": 0, 
                        "rowspan": "1", "displayQuery": "", "chartType": "",
                        "series": '', "xAxis":"", "yAxis": []}, 
                       {"col": 1, "colspan": "1", "id": "cell2", "row": 0,
                        "rowspan": "1", "displayQuery": "", "chartType": "",
                        "series": "", "xAxis":"", "yAxis": []}], 
                      [{"col": 0, "colspan": "1", "id": "cell3", "row": 1,
                        "rowspan": "1","displayQuery": "", "chartType": "",
                        "series": "", "xAxis":"", "yAxis": []}, 
                       {"col": 1, "colspan": "1", "id": "cell4", "row": 1,
                        "rowspan": "1", "displayQuery": "", "chartType": "",
                        "series": "", "xAxis":"", "yAxis": []}]]

        api.templates.blank({
            graphSlug: $scope.slugs.graph, 
        }, function (data) {
            data.layout = layout;
            $scope.template.layout = layout;
            $scope.resp = {table: layout, queries: data.queries}
            $scope.prev = {table: exampleTable, queries: data.queries}
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
            ,   m = datetime.getUTCMonth() + 1
            ,   month = m.toString() 
            ,   day = datetime.getUTCDate().toString()
            ,   year = datetime.getUTCFullYear().toString()
            ,   hour = datetime.getUTCHours().toString()
            ,   minute = datetime.getUTCMinutes().toString();
            if (month.length === 1) month = '0' + month;
            if (day.length === 1) day = '0' + day;
            if (hour.length === 1) hour = '0' + hour;
            if (minute.length === 1) minute = '0' + minute;
            data.template.time = hour + ':' + minute;
            data.template.date = month + '/' + day + '/' + year;
            $scope.template = data.template;
            $scope.resp = {table: data.template.layout, queries: data.queries};
            $scope.prev = $scope.resp;
        });
}]);


controllers.controller('ReportPreviewCtrl', [
    '$scope',
    '$controller',
    'api',
    'parser',
    'breadService',
    function ($scope, $controller, api, parser, breadService) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.pdf = parser.pdf();
        api.templates.preview({
            graphSlug: $scope.slugs.graph,
            template: $scope.slugs.template,  
        }, function (data) {
            $scope.template = data.template;
            $scope.resp = {table: data.template.layout, queries: data.queries};
            breadService.updateName(data.template.name);
        });
}]);


controllers.controller('ReportHistoryCtrl', [
    '$scope',
    '$controller',
    'api',
    'breadService',
    function ($scope, $controller, api, breadService) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.getPage = function (pageNum) {
            api.history.history({
                graphSlug: $scope.slugs.graph,
                template: $scope.slugs.template,
                page: pageNum
            }, function (data) {
                for (var i=0; i<data.reports.length; i++) {
                    var history = data.reports[i].reports
                    ,   mostRecent = history[0]
                    ,   datetime = new Date(data.reports[i].bucket);
                    data.reports[i]["display"] = datetime.toUTCString().replace(/\s*(GMT|UTC)$/, "").replace("00:00:00", "")
                    for (var j=0; j<history.length; j++) {
                        var report = history[j]
                        ,   date = JSON.parse(report.date_run)
                        ,   datetime = new Date(date);
                        report.date_run = datetime.toUTCString().replace(/\s*(GMT|UTC)$/, "")

                        if (datetime > mostRecent.date_run) mostRecent = report;
                    }
                }
                breadService.updateName(data.name)
                $scope.template = data;
                if (data.reports.length > 0) $scope.getReport(mostRecent.id)
            });
        }

        $scope.getPage(1)

        $scope.expanded = {}

        $scope.expand = function (bucket) {
            if (bucket.expanded) {
                bucket.expanded = false;
            } else {
               bucket.expanded = true; 
            }
        }
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


controllers.controller('Chart', [
    '$scope',
    function ($scope) {
        $scope.charts = {
                bar: {options: {chart: {type: 'column'}},
                      series: [{data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]]}],
                      size: {width: 200, height: 200},
                      title: {text: 'column'}},
                scatter: {options: {chart: {type: 'scatter'}},
                          series: [{data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]]}],
                          size: {width: 200, height: 200},
                          title: {text: 'scatter'}},
                line: {options: {chart: {type: 'line'} },
                       series: [{data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]]}],
                       size: {width: 200, height: 200},
                       title: {text: 'line'}},
                pie: {options: {chart: {type: 'pie'}},
                      series: [{data: [['a', 6], ['b', 6.5], ['c', 7], ['d', 7.5]]}],
                      size: {width: 200, height: 200},
                      title: {text: 'pie'}}
            }
}])