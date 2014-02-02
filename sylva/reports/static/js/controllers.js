var reportsControllers = angular.module('reportsControllers', []);


reportsControllers.controller('reportsListCtrl', ['$scope', '$timeout', 'api',
    function($scope, $timeout, api) {

        $scope.dropped = [];
        $scope.namePlaceholder = 'Report Name';
        $scope.reportName = '';
        $scope.date = '19/03/2013';
        $scope.report = {};
        $scope.reportHeader = "New Report";

        $scope.init = function (graphSlug) {
            console.log('init', graphSlug);
            $scope.reports = api.reports.query({graphSlug: graphSlug});
            $scope.queries = api.queries.query({graphSlug: graphSlug}); 
            $scope.graphSlug = graphSlug;
        };
        
        $scope.newReport = function () {
            $scope.reportForm = true;
            $scope.dropped = [];
            $scope.reportName = '';
            $scope.namePlaceholder = 'Report Name';
            $scope.report = {}; 
            $scope.reportHeader = "New Report";
        };  

        $scope.removeQuery = function (index) {
            if (index > -1) $scope.dropped.splice(index, 1);
        };

        $scope.handleDrop = function (drop) {
            $scope.dropped.push(drop);
        }; 

        $scope.processForm = function (report) {
            var newReport = {
                name: report.name,
                queries: $scope.dropped,
                start_time: report.startTime,
                frequency: report.frequency
            };
            console.log('daat', report);
            var post = new api.reports();
            post.report = newReport;
            console.log('post', post)
            post.$save({graphSlug: $scope.graphSlug}, function (data) {
                $scope.reports.push(data)
                $scope.dropped = []
                $scope.namePlaceholder = 'Report Name';
                $scope.report = {};
                $scope.reportHeader = "New Report";
                
            });
        };

        $scope.showReport = function (reportSlug) {
            var report = $scope.reports.filter(function (element) {
                return element.slug === reportSlug;
            });
            var name = report[0].name
            $scope.dropped = report[0].queries;
            $scope.namePlaceholder = '';
            $scope.report.name = name;
            $scope.reportHeader = name;
            console.log('start', report[0].start_time)
            $scope.report.startTime = new Date(report[0].start_time);
            $scope.report.frequency = report[0].frequency;

        };
    }]);