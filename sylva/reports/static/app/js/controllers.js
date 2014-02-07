var reportsControllers = angular.module('reportsControllers', []);

reportsControllers.controller('ReportListCtrl', ['$scope', '$routeParams', '$timeout', 'api',  function ($scope, $routeParams, $timeout, api) {
    console.log('yes')
    $scope.graph = $routeParams.graphid;
    $scope.reports = api.reports.query({graphSlug: $scope.graph});
    
}]);

reportsControllers.controller('EditReportCtrl', ['$scope', '$routeParams', 'api', function ($scope, $routeParams, api) {
    $scope.report = 'report'
}]);

reportsControllers.controller('reportsEditCtrl', ['$scope', '$timeout', 'api',
    function($scope, $timeout, api) {

        $scope.dropped = [];
        $scope.reportName = '';
        $scope.report = {};
        
        $scope.init = function (graphSlug, reportHeader, namePlaceholder) {
            console.log('init', graphSlug);
            $timeout(function () {
                $scope.reports = api.reports.query({graphSlug: graphSlug});
                $scope.queries = api.queries.query({graphSlug: graphSlug}); 
                $scope.graphSlug = graphSlug;
                $scope.defaultReportHeader = reportHeader;
                $scope.defaultNamePlaceholder = namePlaceholder;
                $scope.reportHeader = $scope.defaultReportHeader;
                $scope.namePlaceholder = $scope.defaultNamePlaceholder

            });
        };
        
        $scope.newReport = function () {
            $scope.reportForm = true;
            $scope.dropped = [];
            $scope.reportName = '';
            $scope.namePlaceholder = $scope.defaultNamePlaceholder;
            $scope.report = {}; 
            $scope.reportHeader = $scope.defaultReportHeader;
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
                frequency: report.frequency,
                description: report.description
            };
            console.log('daat', report);
            var post = new api.reports();
            post.report = newReport;
            console.log('post', post)
            post.$save({graphSlug: $scope.graphSlug}, function (data) {
                $scope.reports.push(data)
                $scope.dropped = []
                $scope.namePlaceholder = $scope.defaultNamePlaceholder;
                $scope.report = {};
                $scope.reportHeader = $scope.defaultReportHeader;
                
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
            $scope.report.description = report[0].description;

        };
    }]);
