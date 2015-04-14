"use strict";

describe("TestCtrls", function () {

    var $httpBackend, $rootScope, createController, listRequestHandler, blankRequestHandler,
    templateRequestHandler, reportPreviewHandler, reportHistoryHandler;

    beforeEach(module('reports'));

    beforeEach(inject(function($injector) {
      // Set up the mock http service responses
        $httpBackend = $injector.get('$httpBackend');
      // backend definition common for all tests
        listRequestHandler = $httpBackend.when('GET', '/reports/dh/list?page=1').respond({templates: [{
            "pk": 2,
            "model": "reports.reporttemplate",
            "layout": "",
            "name": "asdf",
            "graph": 1,
            "last_run": null,
            "slug": "asdf",
            "frequency": "w",
            "email_to": [],
            "queries": [],
            "start_date": null, //Weird behaviour here, JSON.parse throws error on string parse.
            "description": ""
        }]});

        // WILL ADD REAL RESPONSES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        blankRequestHandler = $httpBackend.when('GET', '/reports/dh/templates?queries=true').respond({
            queries: ['query1', 'query2'],
            template: null
        });

        reportPreviewHandler = $httpBackend.when('GET', '/reports/dh/templates').respond({
                template: {"layout": []},
                queries: ['query1', 'query2']
        });

        reportHistoryHandler = $httpBackend.when('GET', '/reports/dh/history?page=1').respond({
            reports: [{reports: [], bucket: []}]
        })

        // The $controller service is used to create instances of controllers
        var $controller = $injector.get('$controller');

        createController = function($scope, ctrl) {
            return $controller(ctrl, {'$scope' : $scope });
        };
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });


    it('Should fetch a single template', function() {
      $httpBackend.expectGET('/reports/dh/list?page=1');
      var $scope = {};
      var controller = createController($scope, 'ReportListCtrl');
      $httpBackend.flush();
      expect($scope.data.templates.length).toBe(1)
    });

    it('Should fetch a blank template', function () {
        $httpBackend.expectGET('/reports/dh/templates?queries=true');
        var $scope = {};
        var controller = createController($scope, 'NewReportCtrl');
        $httpBackend.flush();
        expect($scope.resp.queries.length).toBe(2)
    });

    it('Should fetch a preview', function () {
        $httpBackend.expectGET('/reports/dh/templates');
        var $scope = {};
        var controller = createController($scope, 'ReportPreviewCtrl');
        $httpBackend.flush();
        expect($scope.resp.queries.length).toBe(2)
    });

    it('Should fetch report history', function () {
        $httpBackend.expectGET('/reports/dh/history?page=1');
        var $scope = {};
        var controller = createController($scope, 'ReportHistoryCtrl');
        $httpBackend.flush();
        expect($scope.template.reports.length).toBe(1)
    });
});


// This reptition simplifies testing, maybe remove later.
describe('ReportEditCtrl', function () {

    var $httpBackend, templateRequestHandler, createController;

    beforeEach(module('reports'));

    beforeEach(inject(function($injector) {
        $httpBackend = $injector.get('$httpBackend');

        templateRequestHandler = $httpBackend.when('GET', '/reports/dh/templates?queries=true').respond(
            {template: {start_date: null}, queries: ['query1', 'query2']})

        var $controller = $injector.get('$controller');

        createController = function($scope, ctrl) {
                return $controller(ctrl, {'$scope' : $scope });
        };
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    it('Should fetch an existing template', function () {
        $httpBackend.expectGET('/reports/dh/templates?queries=true');
        var $scope = {};
        var controller = createController($scope, 'EditReportCtrl');
        $httpBackend.flush();
        expect($scope.resp.queries.length).toBe(2)
    });
})
