var reportsControllers = angular.module('reportsControllers', ['ngSanitize']);


reportsControllers.controller('reportsListCtrl', ['$scope', function($scope) {
	$scope.reports = [
		{name: 'report1'},
		{name: 'report2'},
		{name: 'report3'},
		{name:'report4'},
		{name: 'report5'},
		{name: 'report6'},
		{name: 'report7'},
		{name: 'report8'},
		{name:'report9'},
		{name: 'report10'},
		{name: 'report11'},
		{name: 'report12'},
		{name: 'report13'},
		{name:'report14'},
		{name: 'report15'},
	];

	$scope.queries = [{name: 'query1'}, {name: 'query2'}, {name: 'query3'}, {name: 'query4'}, {name: 'query5'}]

	//$scope.reportForm = true;
	console.log($scope.reportForm)
	$scope.newReport = function () {
		console.log('click')
		$scope.reportForm = true;
	}

	$scope.dropped = []

	$scope.removeQuery = function (index) {
		console.log(index)
		if (index > -1) $scope.dropped.splice(index, 1)
	}

	$scope.handleDrop = function (drop) {
		$scope.dropped.push(drop);
		console.log($scope.dropped)
	} 
}]);