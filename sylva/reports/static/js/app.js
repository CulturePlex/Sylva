var reports = angular.module('reports', ['reportsControllers', 'reportsServices', 'reportsDirectives', 'ngDragDrop']);

reports.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});