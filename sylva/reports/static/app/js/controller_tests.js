"use strict";

describe("TestCtrls", function () {

    var $httpBackend, $rootScope, createController, listEndpoint,
    templateEndpointNew, previewEndpoint, historyEndpoint, historyInstEndpoint;

    beforeEach(module('reports'));

    beforeEach(inject(function($injector) {
        // Set up the mock http service responses
        $httpBackend = $injector.get('$httpBackend');
        // backend definition common for all tests
        listEndpoint = $httpBackend.when('GET', '/reports/dh/list?page=1').respond(
            {"templates": [{"frequency": "h", "layout": {"layout": [[{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "pagebreaks": {"1": false, "0": false}}, "name": "Template2", "collabs": [{"id": "davebshow", "display": "davebshow"}], "description": "", "slug": "template2", "last_run": "\"2015-04-15T13:15:00.425264\"", "start_date": "\"2015-04-15T08:15:00\""}, {"frequency": "w", "layout": {"layout": [[{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#EDA9BC", "country_1.Name": "#FFFFFF"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}, {"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 1, "colors": {"Count(institution_1.Name)": "#C6C6FF", "country_1.Name": "#E994AB", "Count(project_1.Name)": "#38ADD1"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "column", "displayQuery": 2, "id": "cell2", "row": 0}]], "pagebreaks": {"0": false}}, "name": "Template1", "collabs": [], "description": "", "slug": "template1", "last_run": "null", "start_date": "\"2015-04-15T09:00:00\""}], "num_pages": 1, "total_count": 2, "num_objects": 2, "next_page_number": null, "page_number": 1, "previous_page_number": null}        );

        templateEndpointNew = $httpBackend.when('GET', '/reports/dh/templates?queries=true').respond(
            {"template": null, "queries": [{"series": [["color", "count1", "count2", "count3", "count4", "count5"], ["yellow", 6, 7, 8, 9, 10], ["blue", 6.5, 5.5, 8, 7, 11], ["purple", 4.5, 5.5, 6, 9, 9.5], ["red", 5, 5.5, 4.5, 3, 6], ["green", 5, 6, 7.5, 9, 10]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "datatype": "default", "distinct": "", "alias": "country_1.Name", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "datatype": "string", "distinct": false, "alias": "Count(institution_1.Name)", "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}], "name": "simple_query", "id": 1}, {"series": [["color", "count1", "count2", "count3", "count4", "count5"], ["yellow", 6, 7, 8, 9, 10], ["blue", 6.5, 5.5, 8, 7, 11], ["purple", 4.5, 5.5, 6, 9, 9.5], ["red", 5, 5.5, 4.5, 3, 6], ["green", 5, 6, 7.5, 9, 10]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "alias": "country_1.Name", "datatype": "default", "distinct": "", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "alias": "Count(institution_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "project_1", "properties": [{"display_alias": "Count(Project 1.Name)", "alias": "Count(project_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}, {"alias": "produced_by_1", "properties": []}], "name": "two_series", "id": 2}]}        );

        previewEndpoint = $httpBackend.when('GET', '/reports/dh/templates').respond(
            {"template": {"frequency": "h", "layout": {"layout": [[{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "pagebreaks": {"1": false, "0": false}}, "name": "Template2", "collabs": [{"id": "davebshow", "display": "davebshow"}], "description": "", "slug": "template2", "last_run": "\"2015-04-15T13:15:00.425264\"", "start_date": "\"2015-04-15T08:15:00\""}, "queries": [{"series": [["country_1.Name", "Count(institution_1.Name)"], ["Austria", 3], ["Canada", 7], ["Taiwan", 3], ["Australia", 2], ["Switzerland", 3], ["Hungry", 1], ["Belgium", 2], ["Norway", 2], ["Germany", 28], ["Ireland", 1], ["Italy", 6], ["France", 3], ["Poland", 1], ["Denmark", 1], ["China", 3], ["Russia", 1], ["Sweden", 2], ["Netherlands", 6], ["United States", 35], ["Turkey", 1], ["Latvia", 1], ["Spain", 3], ["New Zealand", 1], ["Serbia", 1], ["Israel", 1], ["United Kingdom", 13], ["Japan", 3], ["Finland", 3]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "datatype": "default", "distinct": "", "alias": "country_1.Name", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "datatype": "string", "distinct": false, "alias": "Count(institution_1.Name)", "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}], "name": "simple_query", "id": 1}, {"series": [["country_1.Name", "Count(institution_1.Name)", "Count(project_1.Name)"], ["Austria", 5, 5], ["Canada", 13, 13], ["Taiwan", 4, 4], ["Australia", 1, 1], ["Switzerland", 3, 3], ["Hungry", 1, 1], ["Belgium", 3, 3], ["Norway", 3, 3], ["Germany", 27, 27], ["Ireland", 1, 1], ["Italy", 6, 6], ["France", 3, 3], ["Poland", 1, 1], ["Denmark", 1, 1], ["China", 3, 3], ["Russia", 1, 1], ["Sweden", 2, 2], ["Netherlands", 8, 8], ["United States", 44, 44], ["Turkey", 1, 1], ["Latvia", 1, 1], ["Spain", 4, 4], ["New Zealand", 1, 1], ["Serbia", 1, 1], ["Israel", 1, 1], ["United Kingdom", 25, 25], ["Japan", 3, 3], ["Finland", 3, 3]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "alias": "country_1.Name", "datatype": "default", "distinct": "", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "alias": "Count(institution_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "project_1", "properties": [{"display_alias": "Count(Project 1.Name)", "alias": "Count(project_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}, {"alias": "produced_by_1", "properties": []}], "name": "two_series", "id": 2}]}        );

        historyEndpoint = $httpBackend.when('GET', '/reports/dh/history?page=1').respond(
            {"num_pages": 1, "name": "Template2", "total_count": 4, "num_objects": 2, "page_number": 1, "next_page_number": null, "reports": [{"bucket": "2015-04-15T00:00:00", "reports": [{"table": [[{"ySeries": [], "rowspan": "1", "name": "simple_query", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)"], ["Austria", 3], ["Canada", 7], ["Taiwan", 3], ["Australia", 2], ["Switzerland", 3], ["Hungry", 1], ["Belgium", 2], ["Norway", 2], ["Germany", 28], ["Ireland", 1], ["Italy", 6], ["France", 3], ["Poland", 1], ["Denmark", 1], ["China", 3], ["Russia", 1], ["Sweden", 2], ["Netherlands", 6], ["United States", 35], ["Turkey", 1], ["Latvia", 1], ["Spain", 3], ["New Zealand", 1], ["Serbia", 1], ["Israel", 1], ["United Kingdom", 13], ["Japan", 3], ["Finland", 3]], "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "name": "two_series", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)", "Count(project_1.Name)"], ["Austria", 5, 5], ["Canada", 13, 13], ["Taiwan", 4, 4], ["Australia", 1, 1], ["Switzerland", 3, 3], ["Hungry", 1, 1], ["Belgium", 3, 3], ["Norway", 3, 3], ["Germany", 27, 27], ["Ireland", 1, 1], ["Italy", 6, 6], ["France", 3, 3], ["Poland", 1, 1], ["Denmark", 1, 1], ["China", 3, 3], ["Russia", 1, 1], ["Sweden", 2, 2], ["Netherlands", 8, 8], ["United States", 44, 44], ["Turkey", 1, 1], ["Latvia", 1, 1], ["Spain", 4, 4], ["New Zealand", 1, 1], ["Serbia", 1, 1], ["Israel", 1, 1], ["United Kingdom", 25, 25], ["Japan", 3, 3], ["Finland", 3, 3]], "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "date_run": "\"2015-04-15T13:15:00.425023\"", "id": 2}, {"table": [[{"ySeries": [], "rowspan": "1", "name": "simple_query", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)"], ["Austria", 3], ["Canada", 7], ["Taiwan", 3], ["Australia", 2], ["Switzerland", 3], ["Hungry", 1], ["Belgium", 2], ["Norway", 2], ["Germany", 28], ["Ireland", 1], ["Italy", 6], ["France", 3], ["Poland", 1], ["Denmark", 1], ["China", 3], ["Russia", 1], ["Sweden", 2], ["Netherlands", 6], ["United States", 35], ["Turkey", 1], ["Latvia", 1], ["Spain", 3], ["New Zealand", 1], ["Serbia", 1], ["Israel", 1], ["United Kingdom", 13], ["Japan", 3], ["Finland", 3]], "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "name": "two_series", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)", "Count(project_1.Name)"], ["Austria", 5, 5], ["Canada", 13, 13], ["Taiwan", 4, 4], ["Australia", 1, 1], ["Switzerland", 3, 3], ["Hungry", 1, 1], ["Belgium", 3, 3], ["Norway", 3, 3], ["Germany", 27, 27], ["Ireland", 1, 1], ["Italy", 6, 6], ["France", 3, 3], ["Poland", 1, 1], ["Denmark", 1, 1], ["China", 3, 3], ["Russia", 1, 1], ["Sweden", 2, 2], ["Netherlands", 8, 8], ["United States", 44, 44], ["Turkey", 1, 1], ["Latvia", 1, 1], ["Spain", 4, 4], ["New Zealand", 1, 1], ["Serbia", 1, 1], ["Israel", 1, 1], ["United Kingdom", 25, 25], ["Japan", 3, 3], ["Finland", 3, 3]], "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "date_run": "\"2015-04-15T12:15:00.428291\"", "id": 1}]}, {"bucket": "2015-04-16T00:00:00", "reports": []}], "previous_page_number": null}        )

        historyInstEndpoint = $httpBackend.when('GET', '/reports/dh/history?report=2').respond(
            {"table": [[{"ySeries": [], "rowspan": "1", "name": "simple_query", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)"], ["Austria", 3], ["Canada", 7], ["Taiwan", 3], ["Australia", 2], ["Switzerland", 3], ["Hungry", 1], ["Belgium", 2], ["Norway", 2], ["Germany", 28], ["Ireland", 1], ["Italy", 6], ["France", 3], ["Poland", 1], ["Denmark", 1], ["China", 3], ["Russia", 1], ["Sweden", 2], ["Netherlands", 6], ["United States", 35], ["Turkey", 1], ["Latvia", 1], ["Spain", 3], ["New Zealand", 1], ["Serbia", 1], ["Israel", 1], ["United Kingdom", 13], ["Japan", 3], ["Finland", 3]], "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "name": "two_series", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": [["country_1.Name", "Count(institution_1.Name)", "Count(project_1.Name)"], ["Austria", 5, 5], ["Canada", 13, 13], ["Taiwan", 4, 4], ["Australia", 1, 1], ["Switzerland", 3, 3], ["Hungry", 1, 1], ["Belgium", 3, 3], ["Norway", 3, 3], ["Germany", 27, 27], ["Ireland", 1, 1], ["Italy", 6, 6], ["France", 3, 3], ["Poland", 1, 1], ["Denmark", 1, 1], ["China", 3, 3], ["Russia", 1, 1], ["Sweden", 2, 2], ["Netherlands", 8, 8], ["United States", 44, 44], ["Turkey", 1, 1], ["Latvia", 1, 1], ["Spain", 4, 4], ["New Zealand", 1, 1], ["Serbia", 1, 1], ["Israel", 1, 1], ["United Kingdom", 25, 25], ["Japan", 3, 3], ["Finland", 3, 3]], "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "date_run": "\"2015-04-15T13:15:00.425023\"", "id": 2}        )

        // The $controller service is used to create instances of controllers
        var $controller = $injector.get('$controller');

        createController = function($scope, ctrl, routeParams) {
            return $controller(ctrl, {'$scope' : $scope, '$routeParams': routeParams});
        };
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });


    it('Should fetch two templates', function() {
      $httpBackend.expectGET('/reports/dh/list?page=1');
      var $scope = {};
      var controller = createController($scope, 'ReportListCtrl', {});
      $httpBackend.flush();
      expect($scope.data.templates.length).toBe(2)
    });

    it('Should fetch a blank template', function () {
        $httpBackend.expectGET('/reports/dh/templates?queries=true');
        var $scope = {};
        var controller = createController($scope, 'NewReportCtrl', {});
        $httpBackend.flush();
        expect($scope.resp.queries.length).toBe(2)
    });

    it('Should fetch a preview', function () {
        $httpBackend.expectGET('/reports/dh/templates');
        var $scope = {};
        var controller = createController($scope, 'ReportPreviewCtrl', {});
        $httpBackend.flush();
        expect($scope.resp.queries.length).toBe(2)
    });

    it('Should fetch report history', function () {
        $httpBackend.expectGET('/reports/dh/history?page=1');
        $httpBackend.expectGET('/reports/dh/history?report=2');
        var $scope = {};
        var controller = createController($scope, 'ReportHistoryCtrl', {});
        $httpBackend.flush();
        expect($scope.template.reports.length).toBe(2)
    });

    it('Should fetch report a report inst', function () {
        $httpBackend.expectGET('/reports/dh/history?report=2');
        var $scope = {};
        var controller = createController($scope, 'ReportHistoryCtrl', {"reportId": 2});
        $httpBackend.flush();
        expect($scope.template.reports.length).toBe(2)
    });
});


// This reptition simplifies testing, maybe remove later.
describe('ReportEditCtrl', function () {

    var $httpBackend, templateEndpointEdit, createController;

    beforeEach(module('reports'));

    beforeEach(inject(function($injector) {
        $httpBackend = $injector.get('$httpBackend');

        templateEndpointEdit = $httpBackend.when('GET', '/reports/dh/templates?queries=true').respond(
            {"template": {"frequency": "h", "layout": {"layout": [[{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#A41CC6", "country_1.Name": "#C0E0DA"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "line", "displayQuery": 1, "id": "cell1", "row": 0}], [{"ySeries": [], "rowspan": "1", "displayMarkdown": "", "yAxis": [{"alias": "Count(institution_1.Name)", "display_alias": "Count(Institution 1.Name)"}, {"alias": "Count(project_1.Name)", "display_alias": "Count(Project 1.Name)"}], "colspan": "1", "col": 0, "colors": {"Count(institution_1.Name)": "#990099", "country_1.Name": "#CFE7E2", "Count(project_1.Name)": "#13EDC2"}, "xAxis": {"alias": "country_1.Name", "display_alias": "Country 1.Name"}, "series": "", "chartType": "column", "displayQuery": 2, "id": "cell3", "row": 1}]], "pagebreaks": {"1": false, "0": false}}, "name": "Template2", "collabs": [{"id": "davebshow", "display": "davebshow"}], "description": "", "slug": "template2", "last_run": "\"2015-04-15T13:15:00.425264\"", "start_date": "\"2015-04-15T08:15:00\""}, "queries": [{"series": [["color", "count1", "count2", "count3", "count4", "count5"], ["yellow", 6, 7, 8, 9, 10], ["blue", 6.5, 5.5, 8, 7, 11], ["purple", 4.5, 5.5, 6, 9, 9.5], ["red", 5, 5.5, 4.5, 3, 6], ["green", 5, 6, 7.5, 9, 10]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "datatype": "default", "distinct": "", "alias": "country_1.Name", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "datatype": "string", "distinct": false, "alias": "Count(institution_1.Name)", "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}], "name": "simple_query", "id": 1}, {"series": [["color", "count1", "count2", "count3", "count4", "count5"], ["yellow", 6, 7, 8, 9, 10], ["blue", 6.5, 5.5, 8, 7, 11], ["purple", 4.5, 5.5, 6, 9, 9.5], ["red", 5, 5.5, 4.5, 3, 6], ["green", 5, 6, 7.5, 9, 10]], "results": [{"alias": "country_1", "properties": [{"display_alias": "Country 1.Name", "alias": "country_1.Name", "datatype": "default", "distinct": "", "aggregate": false, "property": "Name"}]}, {"alias": "institution_1", "properties": [{"display_alias": "Count(Institution 1.Name)", "alias": "Count(institution_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "project_1", "properties": [{"display_alias": "Count(Project 1.Name)", "alias": "Count(project_1.Name)", "datatype": "string", "distinct": false, "aggregate": "Count", "property": "Name"}]}, {"alias": "located_in_1", "properties": []}, {"alias": "produced_by_1", "properties": []}], "name": "two_series", "id": 2}]}
        )

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

    });
})
