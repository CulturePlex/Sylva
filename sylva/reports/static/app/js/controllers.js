'use strict'


var controllers = angular.module('reports.controllers', []);


controllers.controller('ReportListCtrl', [
    '$scope',
    '$location',
    'api',
    'parser',
    'AS_MODAL',
    function ($scope, $location, api, parser, AS_MODAL) {
        $scope.graph = parser.parse();
        var periods = {h: 'Hourly', d: 'Daily', w: 'Weekly' , m: 'Monthly'}
        $scope.getPage = function (pageNum) {
            api.list.list({page: pageNum}, function (data) {
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

        // Set styles if we are in modals
        if(AS_MODAL) {
            $('#simplemodal-container').css({
                'height': '47%',
                'width': '1100px',
                'top': '25%',
                'left': '7%'
            });
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');

            $('#modal-back').css("display", "none");
            // We clone the link to put it in the right position.
            // The cloning is neccesary because Angular destroys the
            // elements when injecting in new templates.
            var cancelLinkClon = $('#modal-cancel-button').clone(true);
            cancelLinkClon.attr('id', 'modal-cancel-button-clon');
            setTimeout(function() {
              cancelLinkClon.css("display", "inline-block");
              $('.pagination-info').prepend(cancelLinkClon);
            }, 100);

            // Let's check if we have reports to add an horizontal line
            // setTimeout(function() {
            //   if($('#content_table').length != 0) {
            //     $('#new-report-button').before("<hr/>");
            //   }
            // }, 75);
        }
}]);


controllers.controller('BaseReportCtrl', [
    '$scope',
    '$location',
    '$routeParams',
    'GRAPH',
    'api',
    'breadService',
    'AS_MODAL',
    function ($scope, $location, $routeParams, GRAPH, api, breadService, AS_MODAL) {

        $scope.slugs = {
            graph: GRAPH,
            template: $routeParams.reportSlug
        };
        // Thess variables may be necessary
        $scope.template = {};
        //////////////////////////////////

        $scope.collabs = [];
        $scope.collab = ""
        $scope.removeCollab = function(ndx) {
            $scope.collabs.splice(ndx, 1)
        };


        $scope.designReport = function () {
            // Using is report form - edit and new ctrls
            $scope.editable = true;
            breadService.design()

            // Set styles if we are in modals
            if(AS_MODAL) {
                var modal = $('#simplemodal-container').css({
                    'width': '1220px'
                });
                // We set a max height for the editable table
                // The 0.80 is because we use 82% for the height
                var maxHeight = modal.height() * 0.80;
                $('.editable-table').css({
                    'max-height': maxHeight,
                    'overflow-y': 'auto'
                });
            }
        };

        $scope.editable;

        $scope.advanced;

        $scope.showAdvanced = function () {
            $scope.advanced = true;
        }

        $scope.hideAdvanced = function () {
            $scope.advanced = false;
        }

        $scope.saveReport = function (template) {
            var post = new api.builder();
            template.collabs = $scope.collabs;
            post.template = template;
            post.$save({
                graphSlug: $scope.slugs.graph,
                report: template.slug
            }, function (data) {
                if (!data.errors) {
                    var redirect = '/';
                    $location.path(redirect);
                } else {
                    if (data.errors.start_date) {
                        if (!template.time) data.errors.time = data.errors.start_date;
                        if (!template.date) data.errors.date = data.errors.start_date;
                    }
                    $scope.errors = data.errors
                }
            }, function (err) {
                if (err.status === 403) {
                    $location.path('/403')
                }

            });
        };
}]);


controllers.controller('NewReportCtrl', [
    '$scope',
    '$controller',
    'api',
    '$location',
    'AS_MODAL',
    function ($scope, $controller, api, $location, AS_MODAL) {
        // Done except post
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.precollabs = null;
        $scope.template = {
            name: 'New Report',
            periodicity: 'weekly',
            time: '',
            date: '',
            description: '',
            nameHtml: '<h2>New Report</h2>',
            is_disabled: false
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

        api.templates.blank({}, function (data) {
            data.layout = layout;
            $scope.resp = {table: {layout: layout, pagebreaks: {0: false, 1: false}}, queries: data.queries}
            $scope.prev = {table: {layout: exampleTable, pagebreaks: {0: false, 1: false}}, queries: data.queries}
            $scope.template.layout = $scope.resp.table
        }, function (err) {
            if (err.status === 403) {
                $location.path("/403")
            }
        });

        // Set styles if we are in modals
        if(AS_MODAL) {
            $('#simplemodal-container').css({
                'height': '82%',
                'width': '1220px',
                'top': '8%',
                'left': '2.5%'
            });
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');
            // We clone the link to put it in the right position.
            var backLinkClon = $('#modal-back-button').clone(true);
            backLinkClon.attr('id', 'modal-back-button-clon');
            backLinkClon.addClass('modal-back-button-clon');
            // We set the correct link
            var linkIndex = $('#App1 a').length - 2;
            var linkToBack = $('#App1 a')[linkIndex].href;
            $('a', backLinkClon).attr('href', linkToBack);
            setTimeout(function() {
              backLinkClon.css("display", "inline-block");
              $('.buttonLinkLeft').after(backLinkClon);
            }, 10);
        }
}]);


controllers.controller('EditReportCtrl', [
    '$scope',
    '$controller',
    'api',
    '$location',
    'AS_MODAL',
    function ($scope, $controller, api, $location, AS_MODAL) {
        // Done except post
        $controller('BaseReportCtrl', {$scope: $scope});
        api.templates.edit({
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
            $scope.precollabs = data.template.collabs;
            $scope.resp = {table: data.template.layout, queries: data.queries};
            $scope.prev = $scope.resp;
        }, function (err) {
            if (err.status === 403) {
                $location.path("/403")
            }
        });

        // Set styles if we are in modals
        if(AS_MODAL) {
            $('#simplemodal-container').css({
                'height': '82%',
                'width': '1220px',
                'top': '8%',
                'left': '2.5%'
            });
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');
            // We clone the link to put it in the right position.
            var backLinkClon = $('#modal-back-button').clone(true);
            backLinkClon.attr('id', 'modal-back-button-clon');
            backLinkClon.addClass('modal-back-button-clon');
            // We set the correct link
            var linkIndex = $('#App1 a').length - 2;
            var linkToBack = $('#App1 a')[linkIndex].href;
            $('a', backLinkClon).attr('href', linkToBack);
            setTimeout(function() {
              backLinkClon.css("display", "inline-block");
              $('.buttonLinkLeft').after(backLinkClon);
            }, 10);
        }
}]);


controllers.controller('ReportPreviewCtrl', [
    '$scope',
    '$controller',
    'api',
    'parser',
    'breadService',
    'AS_MODAL',
    function ($scope, $controller, api, parser, breadService, AS_MODAL) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.pdf = parser.pdf();
        api.templates.preview({
            template: $scope.slugs.template,
        }, function (data) {
            $scope.template = data.template;
            $scope.resp = {table: data.template.layout, queries: data.queries};
            breadService.updateName(data.template.name);
        });

        // Set styles if we are in modals
        if(AS_MODAL) {
            $('#simplemodal-container').css({
                'height': '82%',
                'width': '1220px',
                'top': '8%',
                'left': '2.5%'
            });
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');
            // We clone the link to put it in the right position.
            var backLinkClon = $('#modal-back-button').clone(true);
            backLinkClon.attr('id', 'modal-back-button-clon');
            backLinkClon.addClass('modal-back-button-clon');
            // We set the correct link
            var linkIndex = $('#App1 a').length - 2;
            var linkToBack = $('#App1 a')[linkIndex].href;
            $('a', backLinkClon).attr('href', linkToBack);
            setTimeout(function() {
              backLinkClon.css({
                "display": "inline-block",
                'margin-left': '10px',
                'margin-top': '-1px'
              });
              $('.button.prev-button').after(backLinkClon);
            }, 10);
        }
}]);


controllers.controller('ReportHistoryCtrl', [
    '$scope',
    '$controller',
    'api',
    'breadService',
    'AS_MODAL',
    function ($scope, $controller, api, breadService, AS_MODAL) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.getPage = function (pageNum) {
            api.history.history({
                template: $scope.slugs.template,
                page: pageNum
            }, function (data) {
                for (var i=0; i<data.reports.length; i++) {
                    var history = data.reports[i].reports
                    ,   datetime = new Date(data.reports[i].bucket);
                    if (history[0]) var mostRecent = history[0];
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
                if (data.reports.length > 0) {
                    $scope.getReport(mostRecent.id)
                }
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
                report: id
            }, function (data) {
                $scope.report = data;
                $scope.resp = {table: {layout: data.table.layout,
                               pagebreaks: data.table.pagebreaks}}
            });
        }

        // Set styles if we are in modals
        if(AS_MODAL) {
            $('#simplemodal-container').css({
                'height': '82%',
                'width': '1220px',
                'top': '8%',
                'left': '2.5%'
            });
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');
            // We clone the link to put it in the right position.
            var backLinkClon = $('#modal-back-button').clone(true);
            backLinkClon.attr('id', 'modal-back-button-clon');
            backLinkClon.addClass('modal-back-button-clon');
            // We set the correct link
            var linkIndex = $('#App1 a').length - 2;
            var linkToBack = $('#App1 a')[linkIndex].href;
            $('a', backLinkClon).attr('href', linkToBack);
            setTimeout(function() {
              backLinkClon.css("display", "inline-block");
              $('.buttonLinkLeft').after(backLinkClon);
            }, 10);
        }
}]);


controllers.controller("DeleteReportCtrl", [
    '$scope',
    '$controller',
    '$location',
    'api',
    "breadService",
    'AS_MODAL',
    function ($scope, $controller, $location, api, breadService, AS_MODAL) {
        $controller('BaseReportCtrl', {$scope: $scope});
        $scope.getTemplate = function () {
            api.del.get({
                template: $scope.slugs.template
            }, function (data) {
                breadService.updateName(data.name);
                $scope.template = data;
            }, function (err) {
                if (err.status === 403) {
                    $location.path("/403")
                }
            });
        }

        $scope.confirmed = {val: 0}
        $scope.deleteReport = function (confirmed) {
            if (parseInt(confirmed.val) ===  1) {
                var post = new api.del();
                post.template = $scope.slugs.template;
                post.$save({}, function (data) {
                    var redirect = '/';
                    $location.path(redirect);
                }, function (err) {
                    if (err.status === 403) {
                        $location.path("/403")
                    }
                });
            } else {
                var redirect = '/';
                $location.path(redirect);
            }
        }

        $scope.getTemplate();

        // Set styles if we are in modals
        if(AS_MODAL) {
            // Hide the graph from the breadcrumbs
            var graphBreadcrumb = $($('a.ng-binding')[0]);
            graphBreadcrumb.css('display', 'none');
            graphBreadcrumb.next().css('display', 'none');
        }
}]);
