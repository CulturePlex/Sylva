var reportsControllers = angular.module('reportsControllers', []);


reportsControllers.controller('reportsListCtrl', ['$scope', '$timeout', 'api',
    function($scope, $timeout, api) {

        $scope.dropped = [];
        $scope.namePlaceholder = 'Report Name';
        $scope.reportName = '';

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
        };  

        $scope.removeQuery = function (index) {
            if (index > -1) $scope.dropped.splice(index, 1);
        };

        $scope.handleDrop = function (drop) {
            $scope.dropped.push(drop);
        }; 

        $scope.processForm = function (reportName) {
            var newReport = {
                name: reportName,
                queries: $scope.dropped
            };
        
            var post = new api.reports();
            post.report = newReport;
            console.log('post', post)
            post.$save({graphSlug: $scope.graphSlug}, function (data) {
                $scope.reports.push(data)
                $scope.dropped = []
            });
        };

        $scope.showReport = function (reportSlug) {
            var report = $scope.reports.filter(function (element) {
                return element.slug === reportSlug;
            });
            $scope.dropped = report[0].queries
            $scope.namePlaceholder = ''
            $scope.reportName = report[0].name
        };
    }]);