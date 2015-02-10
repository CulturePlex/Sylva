'use strict'


var directives = angular.module('reports.directives', []);


var gettext = window.gettext || String;


directives.directive('sylvaUpdateText', ['breadService', function (breadService) {
    return {
        link: function(scope) {
            scope.$watch('template.name', function (newVal, oldVal) {
                breadService.updateName(newVal);
                scope.template.name = newVal
            });
        }
    };
}]);



directives.directive('sylvaColpick', function () {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, ngModelCtrl) {
            if (attrs.color) element.css('background-color', attrs.color)
            $(function(){
                element.colpick({
                    layout:'hex',
                    submit:0,
                    colorScheme:'dark',
                    onChange:function(hsb, hex, rgb, el, bySetColor) {
                        $(el).css('background-color','#' + hex);
                        // Fill the text box just if the color was set using the picker, and not the colpickSetColor function.
                        if(!bySetColor) $(el).val(hex);
                        scope.$apply(function () {
                            ngModelCtrl.$setViewValue('#' + hex);
                        });
                    }
                })
            });
        }
    };
});



directives.directive('sylvaDatepicker', function () {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, ngModelCtrl) {
            $(function(){
                element.datepicker({
                    dateFormat:'mm/dd/yy',
                    onSelect:function (date) {
                        scope.$apply(function () {
                            ngModelCtrl.$setViewValue(date);
                        });
                    }
                });
            });
        }
    };
});


directives.directive('sylvaTimepicker', function () {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function(scope, element, attrs, ngModelCtrl) {
            $(function(){
                element.timepicker({
                    minutes: {
                        interval: 15
                    }, onSelect:function (time) {
                        scope.$apply(function () {
                            ngModelCtrl.$setViewValue(time);
                        });
                    }
                });
            });
        }
    };
});


directives.directive('sylvaPvRowRepeat', ['tableArray', function (tableArray) {
    return {
        transclude: 'element',
        scope: {
            resp: '='
        },
        controller: function ($scope) {

            this.getQueries = function() {
                return $scope.queries;
            };

            this.getTableWidth = function() {
                return $scope.tableWidth;
            };

            this.getTableArray = function() {
                return $scope.tableArray;
            }
        },
        link: function (scope, elem, attrs, ctrl, transclude) {

            var childScopes = []
            ,   parent = elem.parent();

            scope.tableWidth = parseInt(attrs.width)
            //scope.tableWidth = parseInt(angular.element(elem.parents()[0]).css('width'));

            scope.$watch('resp', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.queries = scope.resp.queries;
                scope.tableArray = tableArray(scope.resp.table);

                var numScopes = childScopes.length;
                if (numScopes > 0) {
                    for (var i=0; i<numScopes; i++) {
                        childScopes[i].element.remove();

                        childScopes[i].scope.$destroy();
                    }
                    childScopes = [];
                }

                var previous = elem
                ,   childScope
                ,   block
                ,   len = scope.tableArray.table.length;
                for (var i=0; i<len; i++) {
                    childScope = scope.$new();
                    childScope.$index = i;
                    if (i === 0) {
                        childScope.rowStyle = {'margin-top': '100px'};
                    } else {
                        childScope.rowStyle = {'margin-top': '50px'};
                    }

                    transclude(childScope, function (clone) {
                        childScope.row = scope.tableArray.table[i];
                        previous.after(clone);
                        block = {};
                        block.element = clone;
                        block.scope = childScope;
                        childScopes.push(block);
                        previous = clone;
                    });
                }
            }, true);
        }
    };
}]);


directives.directive('sylvaPvCellRepeat', ['$sanitize', function ($sanitize) {
    return {
        transclude: 'element',
        require: '^sylvaPvRowRepeat',
        scope: {
            row: '='
        },
        link: function(scope, elem, attrs, ctrl, transclude) {

            var childScopes = []
            ,   previous = elem
            ,   childScope
            ,   len = scope.row.length
            ,   tableWidth = ctrl.getTableWidth()
            ,   tableArray = ctrl.getTableArray()
            ,   numCols = tableArray.numCols
            ,   ang = angular.element;

            if (childScopes.length > 0) {

                for (var i=0; i<len; i++) {

                    childScopes[i].element.remove();
                    childScopes[i].scope.$destroy();
                }
                childScopes = [];
            }

            // This should be refactored
            for (var i=0; i<len; i++) {
                var cell = scope.row[i]
                ,   query = cell.displayQuery
                ,   name = cell.name
                ,   colspan = parseInt(cell.colspan)
                ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                ,   block
                ,   demo = cell.demo || false;
                childScope = scope.$new();
                childScope.$index = i;
                childScope.cellStyle = {width: cellWidth};

                // This should be refactored
                if (cell.displayMarkdown) {
                    var showdown = new Showdown.converter({})
                    ,   html = $sanitize(showdown.makeHtml(cell.displayMarkdown))
                    childScope.markdown = html;
                } else {
                    // This is for all cases except new report
                    if (query && demo === false) {
                        // This is preview, we need to run query
                        if (!cell.series) {

                            query = ctrl.getQueries().filter(function (el) {
                                return el.id === query;
                            })[0];
                            var series = query.series;
                        // THis is either builder mode, or history
                        } else {
                            var series = cell.series
                        }
                        name = query.name;

                        var header = series[0]
                        // xSeries is often catagorical, can only be one
                        ,   xSeriesNdx = header.indexOf(cell.xAxis)
                        ,   chartSeries = [];
                        if (xSeriesNdx === -1) xSeriesNdx = 0
                        // Can be multiple y series composed of numeric var
                        // with the xSeries vars, here we build a object for
                        // Each series
                        var yLen = cell.yAxis.length;
                        if (cell.chartType === "pie") yLen = 1
                        for (var j=0; j<yLen; j++) {
                            var ser = []
                            // this is the alias of the ySeries
                            ,   ySeries = cell.yAxis[j]
                            // this is the position of the ySeries in the series arr
                            ,   ndx = header.indexOf(ySeries);
                            if (cell.colors) {

                                var color = cell.colors[ySeries];
                            } else {
                                var color = ""
                            }
                            if (ndx === -1) ndx = j + 1
                            for (var k=1; k<series.length; k++) {
                                var row = series[k]
                                ,   x;
                                x = row[xSeriesNdx];
                                var point = [x, row[ndx]];
                                ser.push(point);
                            }
                            chartSeries.push({name: ySeries, data: ser, color: color});
                        }

                    } else {
                        // This is the new chart demo (demo="true")
                        chartSeries = [{name: "ySeries", data: cell.series}]
                        name = "Rad Chart"
                    }
                    // Here must config chart.
                    childScope.query = query;
                    childScope.chartConfig = {
                        options: {chart: {type: cell.chartType}},
                        xAxis: {catagories: []},
                        series: chartSeries,
                        title: {text: name},
                        loading: false
                    }
                }

                transclude(childScope, function (clone) {
                    previous.after(clone);
                    block = {}
                    block.element = clone
                    block.scope = childScope
                    childScopes.push(block)
                    previous = clone
                });
            }
        }
    }
}]);


directives.directive('syEditableTable',[
    '$compile', 'tableArray', 'DJANGO_URLS', 'breadService', function ($compile, tableArray, DJANGO_URLS, breadService) {
    return {
        transclude: true,
        scope: {
            resp: '=',
            prev: '=',
            editable: '='
        },
        template:   '<div class="editable-table">' +
                      '<div class="pages">' +
                        '<div class="edit-rows">' +
                          '<div sy-et-row-repeat class="editable-row" queries="queries">' +
                            '<div sylva-et-cell-repeat class="tcell" row="row" rownum="rownum">' +
                              '<div sylva-et-cell config="config" class="query" ng-style="cellStyle">' +
                              '</div>' +
                            '</div>' +
                          '</div>' +
                        '</div>' +
                      '</div>' +
                    '</div>' +
                    '<div>' +
                      '<a class="button" href="">{{ buttonText.done }}</a> ' +
                      '<a class="table-button" href="">{{ buttonText.plusrow }}</a>' +
                      '<a class="table-button" href="">{{ buttonText.pluscol }}</a>' +
                      '<a class="table-button" href="">{{ buttonText.minusrow }}</a>' +
                      '<a class="table-button" href="">{{ buttonText.minuscol }}</a>' +
                      '<a class="table-button" href="">{{ buttonText.pagebreak }}</a>' +
                    '</div>',
        controller: function($scope) {

            this.getTableArray = function() {
                return $scope.tableArray;
            }

            this.getQueries = function() {
                return $scope.queries;
            };

            this.getTableWidth = function() {
                return $scope.tableWidth;
            };

            this.editing = function () {
                $scope.prev = $scope.resp;
            };

            this.editable = function () {
                return $scope.editable;
            }

            // Helper functions for sorting query result data types
            this.parseResults = function (results) {
                var catagorical = []
                ,   numeric = [];
                for (var i=0; i<results.length; i++) {
                    var result = results[i]
                    ,   alias = result.alias
                    ,   props = result.properties;
                    for (var j=0; j<props.length; j++) {
                        var prop = props[j]
                        ,   datatype = prop.datatype
                        ,   element = {alias: prop.alias, name: alias, datatype: datatype,
                                       property: prop.property, aggregate: prop.aggregate};
                        if (datatype !== 'number' && datatype !== 'float' &&
                                datatype !== 'auto_increment' &&
                                datatype !== 'auto_increment_update' &&
                                prop.aggregate === false) {
                            catagorical.push(element)
                        } else {
                            numeric.push(element)
                        }
                    }
                }
                return {cat: catagorical, num: numeric}
            }

        },
        link: function(scope, elem, attrs) {

            var ang = angular.element
            ,   pages = ang(ang(elem.children()[0]).children()[0])
            ,   rows = ang(pages.children()[0])
            ,   buttons = ang(elem.children()[1])
            ,   editMeta = ang(buttons.children()[0])
            ,   addRow = ang(buttons.children()[1])
            ,   addCol = ang(buttons.children()[2])
            ,   delRow = ang(buttons.children()[3])
            ,   delCol = ang(buttons.children()[4])
            ,   pagebreak = ang(buttons.children()[5]);


            scope.buttonText = {
                done: gettext('Done'),
                plusrow: gettext('+ row'),
                minusrow: gettext('- row'),
                pluscol: gettext('+ col'),
                minuscol: gettext('- col'),
                pagebreak: gettext("+ pagebreak")
            }

            scope.done = gettext('Done');
            scope.plusrow = gettext('+ row')
            scope.plusrow = gettext('+ row')
            scope.plusrow = gettext('+ row')

            scope.$watch('resp', function (newVal, oldVal) {
                if (newVal === oldVal) return;
                scope.tableArray = tableArray(scope.resp.table);
                scope.tableWidth = 1100;

                scope.queries = [{name: 'markdown', id: 'markdown', group: 'text'}];

                angular.forEach(scope.resp.queries, function (query) {
                    query['group'] = 'queries';
                    scope.queries.push(query);
                });
            });

            editMeta.bind('click', function () {
                scope.$apply(function () {
                    scope.editable = false;
                    breadService.meta();
                });
            });

            addRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addRow();
                    var height = parseInt(pages.css("height"));
                    var newHeight = (height + 202).toString() + "px";
                    pages.css("height", newHeight)
                });
            });

            addCol.bind('click', function () {
                if (scope.tableArray.numCols < 3) {
                    scope.$apply(function () {
                        scope.tableArray.addCol();
                    });
                }
            });

            delRow.bind('click', function () {
                if (scope.tableArray.numRows > 1)  {
                    scope.$apply(function () {
                        scope.tableArray.delRow();
                        removeBreaks();
                        var height = parseInt(pages.css("height"));
                        var newHeight = (height - 202).toString() + "px";
                        pages.css("height", newHeight)
                    });
                }
            });

            delCol.bind('click', function () {
                if (scope.tableArray.numCols > 1)  {
                    scope.$apply(function () {
                        scope.tableArray.delCol();
                    });
                }
            });

            function canMoveUp(ndx) {
                var brNdx = findBreakrowNdx(1, ndx + 1);
                if (ndx > 0 && brNdx[0]) return true;
                return false;
            }

            function canMoveDown(ndx) {
                var brNdx = findBreakrowNdx(ndx + 1, scope.tableArray.numRows);
                if (ndx + 2 < scope.tableArray.numRows && brNdx[0]) return true;
                return false;
            }

            scope.moveUp = function (ndx) {
                var brArr = findBreakrowNdx(1, ndx + 1);
                var brNdx = brArr[brArr.length - 1]
                scope.removeBreak(ndx)
                buildBreakrow(brNdx)
            }

            scope.moveDown = function (ndx) {
                var brNdx = findBreakrowNdx(ndx + 1, scope.tableArray.numRows)[0];
                scope.removeBreak(ndx)
                buildBreakrow(brNdx)
            }

            scope.removeBreak = function (ndx) {
                $("#pagebreak" + ndx.toString()).remove()
                scope.tableArray.pagebreaks[ndx] = false;
                var breakrow = $("#row" + ndx.toString())
                ,   nextrow = $("#row" + (ndx + 1).toString());
                angular.forEach(nextrow.children(), function (elem) {
                    ang(elem).removeClass("top")
                })
                var height = parseInt(pages.css("height"));
                var newHeight = (height - 50).toString() + "px";
                pages.css("height", newHeight)
            }

            pagebreak.bind("click", function () {
                var breakrowNdx = findBreakrowNdx(1, scope.tableArray.numRows)[0]
                if (breakrowNdx) {

                    buildBreakrow(breakrowNdx)
                }

            });

            function buildBreakrow (breakrowNdx) {
                var ndx = breakrowNdx - 1
                ,   pagebreakHtml = $compile("<div class='pagebreak'" +
                                             "id='pagebreak" + ndx.toString() +  "'>" +
                                             "<hr class='breakline' /> " +
                                             "</div>")(scope)
                ,   breakrow = $("#row" + ndx.toString())
                ,   nextrow = $("#row" + (ndx + 1).toString())
                ,   moveUp = "<a href='' ng-click='moveUp(" + ndx + ")'style='font-size: 200%; z-index:10px; position:absolute; right:45%; margin-top:10px;'>&#8593;</a>"
                ,   moveDown = "<a href='' ng-click='moveDown(" + ndx + ")' style='font-size: 200%; z-index:10px; position:absolute; right:55%; margin-top:10px;'>&#8595;</a>"
                ,   del = "<a href='' ng-click='removeBreak(" + ndx + ")' style='font-size: 200%; z-index:10px; position:absolute; right:50%; margin-top:10px;'>X</a>";

                var controlsOn;
                pagebreakHtml.on("click", function () {
                    if (controlsOn) {
                        $("#controls").remove()
                        controlsOn = false;
                    } else {
                        controlsOn = true;
                        var controls = "<span id='controls'>";
                        if (canMoveUp(ndx)) {
                            controls = controls + moveUp
                        }
                        if (canMoveDown(ndx)) {
                            controls = controls + moveDown
                        }
                        controls = controls + del + "</span>"
                        controls = $compile(controls)(scope)
                        ang(this).append(controls)
                    }
                });
                var height = parseInt(pages.css("height"));
                var newHeight = (height + 50).toString() + "px";
                pages.css("height", newHeight)
                angular.forEach(nextrow.children(), function (elem) {
                    ang(elem).addClass("top")
                })
                breakrow.after(pagebreakHtml);
                scope.tableArray.pagebreaks[ndx] = true;
            }

            var removeBreaks = function () {
                angular.forEach(scope.tableArray.pagebreaks, function (v, k) {
                    if (v === true && parseInt(k) + 1 == scope.tableArray.numRows) {
                        $("#pagebreak" + k.toString()).remove();
                        scope.tableArray.pagebreaks[k] = false;
                        var height = parseInt(pages.css("height"));
                        var newHeight = (height - 50).toString() + "px";
                        pages.css("height", newHeight)
                        return;
                    }
                });
            }

            var findBreakrowNdx = function (start, stop) {
                var arr = [];
                for (var i=start; i<stop; i++) {
                    if (!(scope.tableArray.pagebreaks[i - 1])) {
                        arr.push(i)
                    }
                }
                return arr;
            };
        }
    };
}]);


directives.directive('syEtRowRepeat', [function () {
    return {
        transclude: 'element',
        require: '^syEditableTable',
        scope: {},
        link: function(scope, elem, attrs, ctrl, transclude) {

            var childScopes = []
            ,   previous
            ,   block
            ,   childScope
            ,   tableArray
            ,   numScopes
            ,   len;

            scope.$watchCollection(ctrl.getTableArray, function (newVal, oldVal) {

                if (newVal == oldVal) return;
                tableArray = ctrl.getTableArray();
                numScopes = childScopes.length;

                if (!previous) {
                    previous = elem
                    len = tableArray.table.length;

                    for (var i=0; i<len; i++) {
                        var rowId = 'row' + i;
                        childScope = scope.$new();
                        childScope.$index = i;
                        childScope.row = tableArray.table[i];
                        childScope.rownum = i;
                        transclude(childScope, function (clone) {
                            if (i === 0) clone.addClass('top')

                            clone.attr('id', rowId);
                            clone.addClass('trow');
                            previous.after(clone);
                            block = {}
                            block.element = clone
                            block.scope = childScope
                            childScopes.push(block)
                            previous = clone
                        });
                    }
                } else if (newVal.numRows > oldVal.numRows) {
                    childScope = scope.$new();
                    childScope.$index = numScopes;
                    childScope.row = tableArray.table[numScopes];
                    childScope.rownum = newVal.numRows - 1;

                    transclude(childScope, function (clone) {
                        clone.attr('id', 'row' + numScopes);
                        clone.addClass('trow');
                        previous.after(clone);
                        block = {}
                        block.element = clone
                        block.scope = childScope
                        childScopes.push(block)
                        previous = clone
                    });

                } else if (newVal.numRows < oldVal.numRows) {
                    var scopeToRemove = childScopes[numScopes - 1]
                    scopeToRemove.element.remove();
                    scopeToRemove.scope.$destroy();
                    childScopes.splice(numScopes - 1, 1);
                    previous = childScopes[numScopes - 2].element;
                }
            });
        }
    };
}]);


// SHould be able to combine this with sylvaPvCellRepeat
directives.directive('sylvaEtCellRepeat', [function () {
    return {
        transclude: 'element',
        require: '^syEditableTable',
        replace: false,
        scope: {
            row: '=',
            rownum: '='
        },
        link: function(scope, elem, attrs, ctrl, transclude) {

            var previous
            ,   childScope
            ,   len = scope.row.length
            ,   tableWidth
            ,   tableArray
            ,   numCols
            ,   childScopes = []
            ,   numScopes
            ,   block;

            scope.$on('$destroy', function () {
                numScopes = childScopes.length;
                destroyRow();
            })
            function destroyRow() {
                for (var i=0; i<numScopes; i++) {
                    childScopes[i].element.remove();
                    childScopes[i].scope.$destroy();
                    console.log('Scope destroyed:', childScopes[i].scope.$$destroyed)
                }
                childScopes = [];
            }

            scope.$watch('row.length', function (newVal, oldVal) {
                previous = elem;
                tableWidth = ctrl.getTableWidth();
                tableArray = ctrl.getTableArray();
                numCols = tableArray.numCols;
                numScopes = childScopes.length;
                len = scope.row.length;

                destroyRow();
                for (var i=0; i<len; i++) {
                    var cell = scope.row[i]
                    ,   query = cell.displayQuery
                    ,   yAxis = cell.yAxis
                    ,   xAxis = cell.xAxis
                    ,   colspan = parseInt(cell.colspan)
                    ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                    ,   activeQuery = ctrl.getQueries().filter(function (el) {
                        return el.id === query;
                    })[0];

                    if (activeQuery) {
                        var results = ctrl.parseResults(activeQuery.results);
                        var results = results.num.concat(results.cat)
                        var activeX = results.filter(function (el) {
                            return el.alias === xAxis;
                        })[0];

                        // Find all of the active y Series
                        var activeYs = [];

                        for (var j=0; j<yAxis.length; j++) {

                            var y = yAxis[j]
                            ,   activeY = results.filter(function (el) {
                                return el.alias === y;
                            })[0];

                            if (activeY) {
                                activeY.selected = true;
                                activeYs.push(activeY);
                            }
                        }
                    }

                    childScope = scope.$new();
                    childScope.$index = i;
                    childScope.config = {
                        row: scope.rownum,
                        col: i,
                        colspan: cell.colspan,
                        colors: cell.colors,
                        activeX: activeX,
                        activeYs: activeYs,
                        queries: ctrl.getQueries(),
                        activeQuery: activeQuery,
                        chartTypes: ['column', 'scatter', 'pie', 'line'],
                        chartType: cell.chartType,
                        markdown: cell.displayMarkdown
                    };

                    childScope.cellStyle = {width: cellWidth};
                    transclude(childScope, function (clone) {

                        if (i === 0) {clone.addClass('first')}
                        if (scope.rownum == 0) {clone.addClass("top")}
                        clone.attr('id', cell.id)
                        previous.after(clone);
                        block = {};
                        block.element = clone;
                        block.scope = childScope;
                        childScopes.push(block);
                        previous = clone;
                    });
                }
            });
        }
    };
}]);

// THIS DIRECTIVE HAS SOME REPITITION AND WILL REQUIRE CLEANUP
directives.directive('sylvaEtCell', ['$sanitize', '$compile', 'DJANGO_URLS', 'STATIC_PREFIX', '$anchorScroll', '$location', function ($sanitize, $compile, DJANGO_URLS, STATIC_PREFIX, $anchorScroll, $location) {
    return {
        require: '^syEditableTable',
        scope: {
            config: '='
        },
        template:
'<div class="row">' +
    '<label class="chart-select">' +
        '{{ selectText.content }}' +
    '</label>' +
    '<select ng-model="activeQuery" value="query.id" ng-options="query.name group by query.group for query in queries">' +
        '<option value="">-----</option>' +
    '</select> ' +
'</div>' +
//'<hr>' +
'<div ng-hide="md" class="edit-cell-inside">' +
    '<div class="row">' +
        '<div class="col chartcol">' +
            '<label>' +
                '{{ selectText.chartType }}' +
            '</label>' +
            '<div ng-attr-id="{{\'highscroll\' + row + col}}" style="position: relative;"class="highchart-cont">' +
                '<a href="" id="column" ng-click="setChartType(\'column\')"><img ng-src="{{ static_prefix }}app/svg/bar.svg" /></a>' +
                '<a href="" id="line" ng-click="setChartType(\'line\')"><img ng-src="{{ static_prefix }}app/svg/line.svg" /></a>' +
                '<a href="" id="pie" ng-click="setChartType(\'pie\')"><img ng-src="{{ static_prefix }}app/svg/pie.svg" /></a>' +
            '</div>' +
        '</div>' +
        '<div class="col cellcol">' +
            '<div style="margin:2px;">' +
                '<label>{{ selectText.xSeries }}</label>' +
                '<select ng-model="activeX" ng-value="result" ' +
                    'ng-options="result as (result.alias) for result in xSeries' +
                '">' +
                '</select>' +
            '</div>' +
            '<div style="margin:2px;">' +
                '<label>{{ selectText.ySeries }}</label><br>' +
                '<div class="hoverdiv">' +
                    '<div style="margin:5px;">' +
                        '<form>' +
                        '<ul>' +
                        '<li class="checklist" ng-repeat="result in ySeries">' +
                            '<label style="float:left;">' +
                            '<input ng-hide="pie" type="checkbox" ng-model="result.selected" value="{{result}}" />' +
                            '<input ng-show="pie" name="ysergroup" type="radio" ng-model="$parent.yser" ng-value="result.alias" />' +
                            '{{ result.alias }}' +
                            '</label>' +
                            '<div ng-hide="pie" sylva-colpick color="{{colors[result.alias]}}" ng-model="colors[result.alias]" id="colpick{{$index}}" class="colorbox"></div>' +
                        '</li>' +
                        '</ul>' +
                        '</form>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '</div>' +
'</div>' +
'<div ng-show="md">' +
    '<textarea ng-model="mdarea" class="markdown">' +
    '</textarea>' +
'</div>',
        link: function(scope, elem, attrs, ctrl) {
            var ang = angular.element
            ,   mdDiv = ang(elem.children()[3])
            ,   md = ang(ang(ang(mdDiv[0])[0]).children()[0])
            ,   stepChild = ang(ang(ang(elem.children()[1]).children()[0])[0]).children()
            ,   chartCol = ang(stepChild[0])
            ,   cellCol = ang(stepChild[1])
            ,   chartDiv = ang(chartCol.children()[1])
            ,   chartCont = ang(chartDiv.children()[0])
            ,   results
            ,   coords
            ,   arrows = false
            ,   cellWidth
            ,   result_dict
            // Used for binding arrows to click action merge.
            ,   arrowHtml = {
                    left: '<a class="arrow left" title="merge left" ng-href="" ng-click="merge(0)">&#8592</a>',
                    right: '<a class="arrow right" title="merge right" ng-href="" ng-click="merge(2)">&#8594</a>',
                    rightIn: '<a class="arrow right-in" title="collapse right" ng-href="" ng-click="collapse(0)">&#8594</a>',
                    leftIn: '<a class="arrow left-in" title="collapse left" ng-href="" ng-click="collapse(1)">&#8592</a>'
            };

            scope.static_prefix = STATIC_PREFIX;

            // Translation
            scope.selectText = {
                content: gettext('Content'),
                chartType: gettext('Chart Type'),
                xSeries: gettext('X-Series'),
                ySeries: gettext('Y-Series')
            }
            //scope.colors = {};

            scope.$watch("colors", function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.table[scope.row][scope.col]["colors"] = scope.colors
            }, true);

            // Methods for resizing columns
            scope.merge = function(ndx) {
                var merges = [[scope.row, scope.col - 1], [scope.row - 1, scope.col], [scope.row, scope.col + 1], [scope.row + 1, scope.col]];
                scope.tableArray.mergeCol([coords, merges[ndx]]);
            }

            scope.collapse = function (dir) {
                scope.tableArray.collapseCol(coords, dir)
            }

            chartDiv.hover(function () {
            }, function () {
                if (scope.chartType) {
                    chartScroll();
                }

            });

            var chartScroll = function () {
                var chart = $("#highscroll" + scope.row + scope.col);
                if (scope.chartType === 'line') {
                    chart.animate({
                        scrollTop: 150
                    });
                } else if (scope.chartType == 'column'){
                    chart.animate({
                        scrollTop: 0
                    });
                } else if (scope.chartType == 'pie') {
                    chart.animate({
                        scrollTop: 300
                    });
                }
            }

            // Bind cell to click showing/hiding arrows for merge actions
            elem.bind("click", function (event) {
                if (!arrows) {
                    ang('.arrow').remove();
                    var adjs = scope.tableArray.getAdjCells(scope.row, scope.col);
                    angular.forEach(adjs, function (el) {
                        var arrow = $compile(arrowHtml[el])(scope)
                        elem.append(arrow);
                    });

                    if (parseInt(scope.colspan) > 1) {

                        var leftIn = $compile(arrowHtml['leftIn'])(scope)
                        ,   rightIn = $compile(arrowHtml['rightIn'])(scope);
                        elem.append(leftIn);
                        elem.append(rightIn);
                    }

                    arrows = true;
                } else {
                    ang('.arrow').remove();
                    arrows = false;
                }
            });

            // Hmmm idk
            elem.bind("mouseout", function (event) {
                arrows = false
            });

            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row;
                scope.col = scope.config.col;
                scope.colspan = scope.config.colspan;
                coords = [scope.row, scope.col]
                scope.queries = scope.config.queries;
                if (!scope.activeQuery) {
                    scope.activeQuery = scope.config.activeQuery;
                    scope.activeX = scope.config.activeX;
                    scope.chartTypes = scope.config.chartTypes;
                    scope.chartType = scope.config.chartType;

                }
                scope.colors = scope.config.colors || {}
                scope.activeYs = scope.config.activeYs;
                scope.tableArray = ctrl.getTableArray();
                cellWidth = elem.width()
                chartCol.width(cellWidth * 0.4)
                cellCol.width(cellWidth * 0.45)
                scope.$watch(ctrl.editable, function (newVal, oldVal) {
                    if (newVal == oldVal) return;
                    if (!scope.chartType) return;
                    chartScroll();
                });




                // Here is the active query/ xy series code that executes
                // on init for edit report.
                if (scope.activeQuery) {

                    results = scope.activeQuery.results.filter(function (el) {
                        return el.properties.length > 0;
                    });
                    result_dict = ctrl.parseResults(results)

                    if (result_dict.num.length > 1) {
                        scope.xSeries = result_dict.cat.concat(result_dict.num)
                    } else {
                        scope.xSeries = result_dict.cat
                    }
                    if (scope.xSeries) {
                        scope.activeX = scope.xSeries.filter(function (el) {
                            return el.alias === scope.activeX.alias;
                        })[0];
                    }
                    if (!scope.activeX) scope.activeX = scope.xSeries[0]
                    if (scope.xSeries.length == 1) scope.activeX = scope.xSeries[0]

                    // Deal with multiple activeYs

                    if (scope.activeYs) {

                        for (var i=0; i<result_dict.num.length; i++) {
                            var num_alias = result_dict.num[i].alias;
                            for (var j=0; j<scope.activeYs.length; j++) {
                                var activeY_alias = scope.activeYs[j].alias
                                scope.xSeries = scope.xSeries.filter(function (el) {
                                    return el.alias !== activeY_alias
                                });
                                if (num_alias === activeY_alias) {
                                    result_dict.num[i].selected = true;
                                }
                            }
                        }
                    }
                    scope.ySeries = result_dict.num;
                    scope.ySeries = scope.ySeries.filter(function (el) {
                        return el.alias !== scope.activeX.alias
                    });
                    if (scope.ySeries.length == 1) scope.ySeries[0].selected = true;
                    if (scope.chartType === "pie") {
                        scope.pie = true;
                        scope.yser = scope.activeYs[0].alias
                    }

                } else if (scope.config.markdown) {
                    scope.md = true;
                    scope.mdarea = scope.config.markdown;
                    scope.activeQuery = scope.queries[0];
                }
            });

            // Markdown - broken
            md.on('blur change', function () {

                scope.$apply(function () {
                    scope.tableArray.addMarkdown([scope.row, scope.col], scope.mdarea);
                });
            });

            scope.mdarea = '#Heading 1\n' + '##Heading 2\n' + '###Heading 3\n' +
                            '* A list of items\n' + ' - sub item\n' + '* Unordered list of items\n' + ' - Unordered list of subitems\n';

            scope.mdarea = gettext(scope.mdarea);

            // Active query watch - 1st entry on new report.
            // Full query object group, id, name, fake series etc.
            scope.$watch('activeQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                // Turns off preview mode with Matrix Graph
                ctrl.editing()
                scope.tableArray.table[scope.row][scope.col].ySeries = [];
                var name;
                // Set to no query by user.
                if (newVal != null) {
                    // Find newVal by id
                    name = newVal.id || '';
                    if (name === 'markdown') {
                        // Set active query to empty, turn on md mode
                        // Trace here.
                        scope.md = true;
                        name = '';
                    } else {
                        scope.tableArray.table[scope.row][scope.col].displayMarkdown = "";
                        scope.md = false;
                        results = newVal.results.filter(function (el) {
                            return el.properties.length > 0;
                        });

                        // Sort query results by type.
                        result_dict = ctrl.parseResults(results)

                        if (result_dict.num.length > 1) {
                            scope.xSeries = result_dict.cat.concat(result_dict.num)
                        } else {
                            scope.xSeries = result_dict.cat
                        }
                        // Autoselect catagorical value or first numerical.
                        //if (!scope.activeX) scope.activeX = scope.xSeries[0]
                        //if (scope.xSeries.length == 1) scope.activeX = scope.xSeries[0]
                        scope.ySeries = result_dict.num.map(function  (el) {el.selected = ''; return el}) // ySeries must be numerical
                        //if (scope.ySeries.length == 1) scope.ySeries[0].selected = true;
                        //if (!scope.activeYs) scope.ySeries[0].selected = true;
                        scope.ySeries[0].selected = true;
                        scope.activeX = scope.xSeries[0]
                    }
                } else {
                    name = '';
                }
                scope.tableArray.addQuery([scope.row, scope.col], name);
            });

            scope.$watch('activeX', function (newVal, oldVal) {
                if (!newVal || newVal == oldVal) return;
                scope.tableArray.addAxis([scope.row, scope.col], 'x', newVal.alias)
                scope.ySeries = result_dict.num
                scope.ySeries = scope.ySeries.filter(function (el) {
                    return el.alias !== newVal.alias;
                });
            })

            scope.$watch('ySeries', function (newVal, oldVal) {
                if (!newVal || newVal === oldVal) return;
                for (var i=0; i<newVal.length; i++) {
                    var val = newVal[i];
                    scope.xSeries = scope.xSeries.filter(function (el) {
                        return el.alias !== val.alias;
                    });
                    if (val.selected === true) {
                        scope.tableArray.addAxis([scope.row, scope.col], 'y', val.alias)
                    } else if (val.selected === false) {
                        scope.tableArray.removeAxis([scope.row, scope.col], 'y', val.alias)
                        scope.xSeries.push(val);
                    }
                }
            }, true)

            scope.setChartType = function (type) {
                scope.chartType = type;
            };


            scope.$watch('yser', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                angular.forEach(scope.ySeries, function (el) {
                    scope.tableArray.removeAxis([scope.row, scope.col], 'y', el.alias)
                });
                scope.tableArray.addAxis([scope.row, scope.col], 'y', newVal)
            });

            scope.$watch('chartType', function (newVal, oldVal) {
                if (newVal === oldVal) return;
                if (newVal === "pie") {
                    scope.pie = true;
                    if (scope.yser == undefined) scope.yser = scope.ySeries[0].alias;
                } else {
                    scope.pie = false;
                }
                if (newVal === oldVal) return;
                ctrl.editing()
                scope.tableArray.addChart([scope.row, scope.col], newVal)
            });
        }
    };
}]);


directives.directive('sylvaBreadcrumbs', [
    '$location',
    'parser',
    'GRAPH',
    'DJANGO_URLS',
    function ($location, parser, GRAPH, DJANGO_URLS) {
    return {
        template: '<h2>' +
                    '<a href="/graphs/{{ graphSlug }}/">{{graph}}</a> ' +
                    '<span> &raquo; </span>' +
                    '<a ng-href="#/">{{ breadText.reports }}</a>' +
                    '<span ng-if="reportName"> &raquo; </span>' +
                    '<a  ng-href="#/edit/{{ reportSlug }}">{{ reportName }}</a>' +
                    '<span ng-repeat="crumb in crumbs"> &raquo; {{crumb}} </span>' +
                  '</h2>',
        controller: function ($scope) {

            $scope.graph = GRAPH;
            $scope.graphSlug = parser.parse();
            $scope.crumbs = [];
            $scope.reportName = null;
            $scope.getLocation = function () {
                return $location.path()
            }
        },
        link: function (scope, elem, attrs) {

            scope.breadText = {
                reports: gettext('Reports')
            };

            scope.$watch(scope.getLocation, function (newVal, oldVal) {
                var location = scope.getLocation();
                if (location !== '/' ) {
                    var crumbs = location.split('/')
                    crumbs.splice(0, 1)
                    scope.reportSlug = crumbs.splice(crumbs.length - 1, 1)[0]
                    if (crumbs[0]) crumbs[0] = crumbs[0].charAt(0).toUpperCase() + crumbs[0].slice(1);
                    scope.crumbs = crumbs
                } else {
                    scope.reportName = null;
                    scope.crumbs = [];
                }

            });

            scope.$on('design', function () {
                scope.crumbs.push('Design');
            });

            scope.$on('meta', function () {
                scope.crumbs.pop();
            });

            scope.$on('name', function (e, name) {
                scope.reportName = name;
            });
        }
    };
}]);
