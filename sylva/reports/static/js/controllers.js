var reportsControllers = angular.module('reportsControllers', []);


reportsControllers.controller('reportsListCtrl', ['$scope', '$timeout', function($scope, $timeout) {
    $scope.reports = [
        {name: 'report1', queries: ['query1', 'query3']},
        {name: 'report2', queries: ['query5', 'query2']},
        {name: 'report3', queries: ['query4', 'query5']},
    ];

    $scope.queries = [{name: 'query1'}, {name: 'query2'}, {name: 'query3'}, {name: 'query4'}, {name: 'query5'}]

    $scope.dropped = []
    $scope.namePlaceholder = 'Report Name'
    //$scope.reportForm = true;
    console.log($scope.reportForm)
    $scope.newReport = function () {
        console.log('click')
        $scope.reportForm = true;
    };  

    $scope.removeQuery = function (index) {
        console.log(index)
        if (index > -1) $scope.dropped.splice(index, 1)
    };

    $scope.handleDrop = function (drop) {
        $scope.dropped.push(drop);
        console.log($scope.dropped)
    }; 

    $scope.processForm = function (reportName) {
        var newReport = {
            name: reportName.name,
            queries: $scope.dropped
        };
        $scope.reports.push(newReport)
        $scope.dropped = []
        console.log('new', $scope.reports)
    };

    $scope.getReport = function (reportSlug) {
        // need to put an edit feature here
        var report = $scope.reports.filter(function (element) {
            return element.name === reportSlug;
        });
        console.log('applying', report[0].queries)
        $scope.dropped = report[0].queries
        $scope.namePlaceholder = report[0].name
    };
}]);