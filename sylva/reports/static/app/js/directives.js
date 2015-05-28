'use strict'


var directives = angular.module('reports.directives', []);


var gettext = window.gettext || String;


directives.directive('sylvaAutoComplete', ['DJANGO_URLS', function (DJANGO_URLS) {
    return {
        require: 'ngModel',
        scope: {collabs: "=", precollabs: "="},
        link: function(scope, elem, attrs, ngModelCtrl) {

            var params = {
                minChars: 2,
                prePopulate: [],
                propertyToSearch: "display",
                tokenLimit: 10,
                preventDuplicates: true,
                tokenValue: "id",
                onAdd: function (el) {
                    scope.$apply(function () {
                         scope.collabs.push(el);
                    });
                },
                onDelete: function (el) {
                    scope.$apply(function () {
                        scope.collabs = scope.collabs.filter(function (elem) {
                            return elem.id != el.id;
                        });
                    });
                }
            };

            scope.$watchCollection("precollabs", function (newVal, oldVal) {
                if (newVal === null) {
                    elem.tokenInput(DJANGO_URLS.collabs, params);
                    return;
                };
                if (newVal == oldVal) return;
                scope.collabs = angular.copy(scope.precollabs);
                params.prePopulate = newVal;
                elem.tokenInput(DJANGO_URLS.collabs, params)
            });
        }
    }
}]);


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
                    colorScheme: 'light',
                    layout: 'hex',
                    submitText: 'Ok',
                    color: attrs.color.substr(1),
                    onChange: function(hsb, hex, rgb, el, bySetColor) {
                        $(el).css('background-color','#' + hex.toUpperCase());
                        // Fill the text box just if the color was set using the picker, and not the colpickSetColor function.
                        if(!bySetColor) $(el).val(hex.toUpperCase());
                        scope.$apply(function () {
                            ngModelCtrl.$setViewValue('#' + hex.toUpperCase());
                        });
                    },
                    onSubmit: function(hsb, hex, rgb, el) {
                        element.colpickHide();
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


directives.directive('sylvaPvRowRepeat', ['tableArray', '$compile', '$sanitize', function (tableArray, $compile, $sanitize) {
    return {
        scope: {
            resp: '=',
            prev: '='
        },
        link: function (scope, elem, attrs) {
            var aspectRatio = 1.25
            ,   tableWidth = parseInt(attrs.width)
            ,   canvasWidth = parseInt(angular.element(elem.parents()[0]).css('width'))
            ,   tArray;

            var rowHeight = function (pagebreaks) {
                var heights = {}
                ,   rows = [];
                angular.forEach(pagebreaks, function (v, k) {
                    rows.push(k)
                    if (v === true || parseInt(k) === tArray.numRows - 1) {
                        var numRows = rows.length;
                        for (var i=0; i<numRows; i++) {
                            var row = rows[i]
                            ,   pageHeight = tableWidth * aspectRatio
                            ,   height = pageHeight / numRows;
                            heights[row] = height;
                        }
                        rows = [];
                    }
                });
                return heights;
            }
            scope.$watch('resp', function (newVal, oldVal) {
                if (!(newVal) && newVal == oldVal) return;
                // This executes on server response
                elem.empty()
                var resp = angular.copy(scope.resp)
                tArray = tableArray(resp.table.layout);
                var contDiv = $("<div class='unbreakable' style='page-break-after:always;'></div>");
                var queries = resp.queries
                ,   rowH = rowHeight(resp.table.pagebreaks)
                ,   len = tArray.table.length;

                for (var i=0; i<len; i++) {

                    var row = tArray.table[i]
                    ,   rowDiv = $('<div class="row" width="1025"></div>')
                    ,   rowLen = row.length;

                    for (var j=0; j<rowLen; j++) {
                        var cell = row[j]
                        ,   query = cell.displayQuery
                        ,   name = cell.name
                        ,   colspan = parseInt(cell.colspan)
                        ,   cellWidth = (tableWidth / tArray.numCols - ((tArray.numCols + 1) * 2 / tArray.numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                        ,   demo = cell.demo || false
                        ,   colDiv = $("<div class='col'></div>");
                        if (query === "" && !(cell.displayMarkdown)) demo = true;

                        if (cell.displayMarkdown) {
                            var showdown = new Showdown.converter({})
                            ,   html = $sanitize(showdown.makeHtml(cell.displayMarkdown));
                            colDiv.addClass("display-cell")
                        } else {
                            // This is for all cases except new report
                            if (query && demo === false) {

                                // This is preview, we need to run query
                                var series;
                                if (!cell.series) {
                                    query = queries.filter(function (el) {
                                        return el.id === query;
                                    })[0];
                                    series = query.series;

                                // THis is either builder mode, or history
                                } else {
                                    series = cell.series
                                }

                                name = query.name;

                                var header = series[0]
                                // xSeries is often catagorical, can only be one
                                ,   xSeriesNdx = header.indexOf(cell.xAxis.alias)
                                ,   chartSeries = [];
                                if (xSeriesNdx === -1) xSeriesNdx = 0

                                // Can be multiple y series composed of numeric var
                                // with the xSeries vars, here we build a object for
                                // each series
                                var yLen = cell.yAxis.length;
                                if (cell.chartType === "pie") yLen = 1;
                                for (var k=0; k<yLen; k++) {
                                    var ser = []

                                    // this is the alias of the ySeries
                                    ,   ySeries = cell.yAxis[k].alias
                                    ,   display_alias = cell.yAxis[k].display_alias

                                    // this is the position of the ySeries in the series arr

                                    ,   ndx = header.indexOf(ySeries)
                                    ,   color;
                                    if (cell.colors) {
                                        color = cell.colors[ySeries];
                                    } else {
                                        color = ""
                                    }

                                    if (ndx === -1) ndx = k + 1

                                    for (var m=1; m<series.length; m++) {
                                        var serRow = series[m]
                                        ,   x = serRow[xSeriesNdx]
                                        ,   point = [x, serRow[ndx]];
                                        ser.push(point);
                                    }
                                    chartSeries.push({name: display_alias, data: ser, color: color});
                                }
                            var chartType = cell.chartType

                            } else {
                                //This is the new chart demo (demo="true")
                                if (!cell.series) {
                                    cell["series"] = [
                                       ['Keanu Reeves',36],
                                       ['Linus Torvalds',24],
                                       ['Tyrion Lannister',20],
                                       ['Morpheus',1],
                                       ['Félix Lope de Vega Carpio',156],
                                       ['Javier de la Rosa',24]
                                   ];
                                }

                                var chartTypes = ["pie", "line", "column"]
                                // Random chart type
                                ,   ndx = Number(Math.floor(Math.random() * chartTypes.length))
                                ,   chartType = chartTypes[ndx]
                                ,   query = "demo";
                                chartSeries = [{name: "ySeries", data: cell.series}]
                                name = "Demo Chart";

                            }
                            var childScope = scope.$new();
                            var size;
                            if (scope.prev) {
                                size = {}
                            } else {
                                size = {
                                    height: parseInt(angular.copy(rowH[cell.row])),
                                    width: parseInt(cellWidth)
                                }
                            }
                            childScope.chartConfig = {
                                options: {chart: {type: chartType}},
                                xAxis: {catagories: []},
                                series: chartSeries,
                                title: {text: name},
                                loading: false,
                                size: size
                            }
                            var chartHtml = '<div highchart class="hchartDiv" config="chartConfig"></div>'

                            ,   html = $compile(chartHtml)(childScope);
                            html.height(rowH[cell.row])
                        }

                        colDiv.width(cellWidth)
                        colDiv.height(rowH[cell.row])
                        colDiv.append(html)
                        rowDiv.append(colDiv)

                    }
                    contDiv.append(rowDiv);
                    if (resp.table.pagebreaks[i]) {
                        elem.append(contDiv);
                        var contDiv = $("<div class='unbreakable' style='page-break-after:always;'></div>");
                    }
                }
                contDiv.css('page-break-after', '')
                elem.append(contDiv);
                var contDiv = $("<div class='unbreakable' style='page-break-after:always;></div>");
            }, true);
        }
    };
}]);


directives.directive('syEditableTable',[
    '$compile', 'tableArray', 'breadService', function ($compile, tableArray, breadService) {
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
            };

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
            };

            this.getRowHeight = function () {
                return $scope.resp.rowHeight
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
                        ,   element = {alias: prop.alias, display_alias: prop.display_alias, datatype: datatype,
                                       property: prop.property, aggregate: prop.aggregate};
                        if (datatype !== 'number' && datatype !== 'float' &&
                                datatype !== 'auto_increment' &&
                                datatype !== 'auto_increment_update' &&
                                prop.aggregate === false) {
                            element["catagorical"] = true;
                            element["numeric"] = false;
                            catagorical.push(element);
                        } else {
                            element["catagorical"] = false;
                            element["numeric"] = true;
                            numeric.push(element);
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
                scope.tableArray = tableArray(scope.resp.table.layout);
                scope.tableWidth = 1100;

                scope.queries = [{name: 'markdown', id: 'markdown', group: 'text'}];

                angular.forEach(scope.resp.queries, function (query) {
                    query['group'] = 'queries';
                    scope.queries.push(query);
                });

                var numBreaks = 0;
                angular.forEach(scope.resp.table.pagebreaks, function (v, k) {
                        if (v === true) numBreaks++
                });


                setTimeout(function () {
                    angular.forEach(scope.resp.table.pagebreaks, function (val, key) {
                        if (val === true) {
                            buildBreakrow(parseInt(key) + 1);
                        }
                    });
                    var height = (numBreaks * 50) + (scope.tableArray.numRows * 202);
                    pages.css("height", height);

                }, 500)

                // scope.resp.rowHeight = rowHeight(scope.resp.table.pagebreaks)
            });

            scope.$watch("resp.table.pagebreaks", function (newVal, oldVal) {
                if (newVal === oldVal) return;
                // scope.resp.rowHeight = rowHeight(scope.resp.table.pagebreaks)
            }, true);

            scope.$on('editing', function (e, newVal) {
                if (newVal != scope.editable && scope.editable != undefined) {
                    scope.editable = newVal;
                    breadService.meta();
                }

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
                    scope.resp.table.pagebreaks[scope.tableArray.numRows - 1] = false;
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
                        delete scope.resp.table.pagebreaks[scope.tableArray.numRows]
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
                var brArr = findBreakrowNdx(1, ndx + 1)
                ,   brNdx = brArr[brArr.length - 1];
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
                scope.resp.table.pagebreaks[ndx] = false;
                var breakrow = $("#row" + ndx.toString())
                ,   nextrow = $("#row" + (ndx + 1).toString());
                angular.forEach(nextrow.children(), function (elem) {
                    ang(elem).removeClass("top")
                })
                var height = parseInt(pages.css("height"));
                var newHeight = (height - 50).toString() + "px";
                pages.css("height", newHeight)
                // scope.$apply(function () {
                //     // scope.resp.rowHeight = rowHeight(scope.resp.table.pagebreaks)
                // });
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
                var height = parseInt(pages.css("height"))
                ,   newHeight = (height + 50).toString() + "px";
                pages.css("height", newHeight)
                angular.forEach(nextrow.children(), function (elem) {
                    ang(elem).addClass("top")
                })
                breakrow.after(pagebreakHtml);
                //scope.$apply(function () {
                scope.resp.table.pagebreaks[ndx] = true;
                    // scope.resp.rowHeight = rowHeight(scope.resp.table.pagebreaks)
                //});
            }

            var removeBreaks = function () {
                angular.forEach(scope.resp.table.pagebreaks, function (v, k) {
                    if (v === true && parseInt(k) + 1 == scope.tableArray.numRows) {
                        $("#pagebreak" + k.toString()).remove();
                        scope.resp.table.pagebreaks[k] = false;
                        var height = parseInt(pages.css("height"));
                        var newHeight = (height - 50).toString() + "px";
                        pages.css("height", newHeight)
                        // scope.resp.rowHeight = rowHeight(scope.resp.table.pagebreaks)
                        return;
                    }
                });
            }

            var findBreakrowNdx = function (start, stop) {
                var arr = [];
                for (var i=start; i<stop; i++) {
                    if (!(scope.resp.table.pagebreaks[i - 1])) {
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
                    previous = elem;
                    len = tableArray.table.length;

                    for (var i=0; i<len; i++) {
                        var rowId = 'row' + i;
                        childScope = scope.$new();
                        childScope.$index = i;
                        childScope.row = tableArray.table[i];
                        childScope.rownum = i;
                        transclude(childScope, function (clone) {
                            //if (i === 0) clone.addClass('top')
                            clone.attr('id', rowId);
                            clone.addClass('trow');
                            previous.after(clone);
                            block = {};
                            block.element = clone;
                            block.scope = childScope;
                            childScopes.push(block);
                            previous = clone;
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
                        block = {};
                        block.element = clone;
                        block.scope = childScope;
                        childScopes.push(block);
                        previous = clone;
                    });

                } else if (newVal.numRows < oldVal.numRows) {
                    var scopeToRemove = childScopes[numScopes - 1];
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
                    console.log('Scope destroyed:', childScopes[i].scope.$$destroyed);
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
                        var resultsDict = ctrl.parseResults(activeQuery.results)
                        ,   results = resultsDict.num.concat(resultsDict.cat)
                        ,   activeX = results.filter(function (el) {
                            return el.alias === xAxis.alias;
                        })[0];

                        // Find all of the active y Series
                        var activeYs = [];

                        for (var j=0; j<yAxis.length; j++) {
                            var y = yAxis[j]
                            ,   activeY = results.filter(function (el) {
                                return el.alias === y.alias;
                            })[0];

                            if (activeY) {
                                activeY.selected = true;
                                activeYs.push(activeY);
                            }
                        }
                    }

                    var childScope = scope.$new();
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
                        results: results,
                        resultsDict: resultsDict,
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
directives.directive('sylvaEtCell', ['$sanitize', '$compile', 'STATIC_PREFIX', '$anchorScroll', '$location', function ($sanitize, $compile, STATIC_PREFIX, $anchorScroll, $location) {
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
        '<option ng-attr-id="{{\'empty\' + row + col}}" value="">-----</option>' +
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
                    'ng-options="result as (result.display_alias) for result in xSeries' +
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
                            '<span ng-hide="pie" >' +
                            '<i class="fa fa-eye-slash" id="eye{{$index}}{{row}}{{col}}" ng-click="select(result, $index, row, col)" value="{{result}}" style="margin-right: 3px; width: 1em; height: 1em; cursor: pointer; vertical-align: -2px;" />' +
                            '</span>' +
                            '<div ng-hide="pie" sylva-colpick color="{{colors[result.alias]}}" ng-model="colors[result.alias]" id="colpick{{$index}}" class="colorbox"></div>' +
                            '<input ng-show="pie" name="ysergroup" type="radio" ng-model="$parent.yser.alias" ng-value="result.alias" />' +
                            '{{ result.display_alias }}' +
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
            ,   mdDiv = ang(elem.children()[2])
            ,   md = ang(ang(ang(ang(mdDiv[0])[0])[0]).children()[0])
            ,   stepChild = ang(ang(ang(elem.children()[1]).children()[0])[0]).children()
            ,   chartCol = ang(stepChild[0])
            ,   cellCol = ang(stepChild[1])
            ,   chartDiv = ang(chartCol.children()[1])
            ,   chartCont = ang(chartDiv.children()[0])
            ,   coords
            ,   arrows = false
            ,   cellWidth
            ,   previousSelected
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

            // This fires on load or with edits. Sets up the cell params.
            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row;
                scope.col = scope.config.col;
                scope.colspan = scope.config.colspan;
                coords = [scope.row, scope.col]
                scope.queries = scope.config.queries;
                scope.chartTypes = scope.config.chartTypes;
                if (!scope.activeQuery) {
                    scope.activeQuery = scope.config.activeQuery;
                    scope.activeX = scope.config.activeX;
                    scope.chartType = scope.config.chartType;
                    scope.results = scope.config.results;
                    scope.resultsDict = scope.config.resultsDict
                    scope.activeYs = scope.config.activeYs || [];
                }
                scope.colors = scope.config.colors;
                scope.tableArray = ctrl.getTableArray();
                cellWidth = elem.width();
                chartCol.width(cellWidth * 0.4);
                cellCol.width(cellWidth * 0.45);

                // Here is the active query/ xy series code that executes
                // on init for edit report.
                if (scope.activeQuery) {
                    var resultsDict = scope.resultsDict;

                    // Set up xSeries options and activeX
                    if (resultsDict.num.length > 1) {
                        scope.xSeries = resultsDict.cat.concat(resultsDict.num);
                    } else {
                        scope.xSeries = resultsDict.cat;
                    }

                    // This either uses the assigned activeX or the first x
                    // in the series.
                    if (scope.xSeries) {
                        scope.activeX = scope.xSeries.filter(function (el) {
                            return el.alias === scope.activeX.alias;
                        })[0];
                    }
                    if (!scope.activeX) scope.activeX = scope.xSeries[0];

                    // Case of only one option
                    if (scope.xSeries.length == 1) scope.activeX = scope.xSeries[0];

                    // Deal with multiple activeYs
                    if (scope.activeYs.length > 0) {

                        // These nested loops compare activeY aliases with
                        // results aliases
                        for (var j=0; j<scope.activeYs.length; j++) {
                            var activeYAlias = scope.activeYs[j].alias;

                            // Get any activeYs out of the possible xSeries
                            scope.xSeries = scope.xSeries.filter(function (el) {
                                return el.alias !== activeYAlias;
                            });

                            for (var i=0; i<resultsDict.num.length; i++) {
                                var numAlias = resultsDict.num[i].alias;
                                // Select the activeY series
                                if (numAlias === activeYAlias) {
                                    resultsDict.num[i].selected = true;
                                    previousSelected = i;
                                }
                            } // Inside for
                        } // Outside for
                    } // if

                    // Remove active x from ySeries options
                    scope.ySeries = resultsDict.num.filter(function (el) {
                        return el.alias !== scope.activeX.alias;
                    });

                    // Autoselect series, remove slash, add eyball
                    if (scope.ySeries.length == 1) {
                        setTimeout(function () {
                            scope.ySeries[0].selected = true;
                            var eye = $("#eye0" + scope.row.toString() + scope.col.toString());
                            eye.removeClass("fa-eye-slash");
                            eye.addClass("fa-eye");
                        }, 250)
                    } else {
                        // Remove eye slashes and add eyeballs
                        setTimeout(function () {
                            for (var i=0; i<scope.ySeries.length; i++) {
                                if (scope.ySeries[i].selected === true) {
                                    var eye = $("#eye" + i.toString() + scope.row.toString() + scope.col.toString());
                                    eye.removeClass("fa-eye-slash");
                                    eye.addClass("fa-eye");
                                }
                            }
                        }, 250)
                    }
                    // Pies are annoying.
                    if (scope.chartType === "pie") {
                        scope.pie = true;
                        scope.yser = scope.activeYs[0];
                    }
                // Prep for markdown. This does show/hide with primative
                // true on scope, and also is watched below.
                } else if (scope.config.markdown) {
                    scope.md = true;
                    scope.mdarea = scope.config.markdown;
                    scope.activeQuery = scope.queries[0];
                }
            });

            // Active query watch - 1st entry on new report.
            // Full query object group, id, name, fake series etc.
            scope.$watch('activeQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                // Use jQuery to get rid of empty select val.
                var id = "#empty" + scope.row.toString() + scope.col.toString();
                $(id).remove();
                // Turns ctrl.editing() turns off preview mode with Demo
                ctrl.editing()
                // Reset table params.
                scope.tableArray.table[scope.row][scope.col].ySeries = [];
                scope.tableArray.table[scope.row][scope.col].xAxis = "";
                scope.tableArray.table[scope.row][scope.col].yAxis = [];
                scope.tableArray.table[scope.row][scope.col].series = "";
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
                        // Is necessary to set to ""
                        scope.tableArray.table[scope.row][scope.col].displayMarkdown = "";
                        scope.md = false;

                        // Make sure the results all can be processed.
                        var results = newVal.results.filter(function (el) {
                            return el.properties.length > 0;
                        });

                        // Sort query results by type.
                        var resultsDict = ctrl.parseResults(results)

                        if (scope.colors == undefined) {
                            // Randomly assign colors to the results.
                            scope.colors = {};
                            var results = resultsDict.cat.concat(resultsDict.num);
                            angular.forEach(results, function (elem) {
                                var col = simpleColors[Math.floor(Math.random() * simpleColors.length)];
                                if(!(elem.alias in scope.colors)) scope.colors[elem.alias] = col;
                            });
                        }
                        var xSeries;
                        if (resultsDict.num.length > 1) {
                            xSeries = resultsDict.cat.concat(resultsDict.num);
                        } else {
                            xSeries = resultsDict.cat;
                        }
                        // Set select to "", then select first y
                        scope.ySeries = resultsDict.num.map(function  (el) {el.selected = ''; return el}) // ySeries must be numerical
                        scope.ySeries[0].selected = true;
                        setTimeout(function () {
                            var eye = $("#eye0" + scope.row.toString() + scope.col.toString());
                            eye.removeClass("fa-eye-slash");
                            eye.addClass("fa-eye");
                        }, 100)

                        // Remove activeY out of the xSeries
                        scope.xSeries = xSeries.filter(function (el) {
                            return el.alias !== scope.ySeries[0].alias;
                        });
                        scope.activeX = scope.xSeries[0]
                    }
                } else {
                    name = '';
                    scope.xSeries = [];
                    scope.ySeries = [];
                    scope.activeX = "";
                    scope.activeYs = [];
                }
                scope.tableArray.addQuery([scope.row, scope.col], name);
            });

            scope.$watch('ySeries', function (newVal, oldVal) {
                if (!newVal || newVal == oldVal) return;

                // Always have a selected y
                if (newVal.length === 1) {
                    newVal[0].selected = true;
                }

                // Keep track if there is a selected y.
                var selected = false;
                scope.tableArray.table[scope.row][scope.col]['yAxis'] = [];

                for (var i=0; i<newVal.length; i++) {
                    var val = newVal[i];

                    if (val.selected === true) {
                        selected = true;
                        previousSelected = i;
                        scope.tableArray.addAxis([scope.row, scope.col], 'y', {"alias": val.alias, "display_alias": val.display_alias});
                        var eye = $("#eye" + i.toString() + scope.row.toString() + scope.col.toString());
                        eye.removeClass("fa-eye-slash");
                        eye.addClass("fa-eye");
                        scope.xSeries = scope.xSeries.filter(function (el) {
                            return el.alias !== val.alias;
                        });

                    } else if (val.selected === false) {
                        // This is a hack
                        scope.xSeries = scope.xSeries.filter(function (elem) {
                            return elem.alias != val.alias;
                        })
                        scope.xSeries.push(val);
                        var eye = $("#eye" + i.toString() + scope.row.toString() + scope.col.toString());
                        eye.removeClass("fa-eye");
                        eye.addClass("fa-eye-slash");
                    }
                }
                // Well, this makes sure one of the yseries items is selected.
                // It always favors the previous element in the series though
                // it's the safest way I suppose.
                if (selected === false) {
                    if (previousSelected === 0) {
                        newVal[1].selected = true;
                    } else {
                        newVal[previousSelected - 1].selected = true;
                    }
                }
            }, true)

            scope.$watch('activeX', function (newVal, oldVal) {
                if (!newVal || newVal == oldVal) return;
                scope.tableArray.addAxis([scope.row, scope.col], 'x', {"alias": newVal.alias, "display_alias": newVal.display_alias});
                if (newVal.numeric === true) {
                    scope.ySeries = scope.ySeries.filter(function (elem) {
                        return elem.alias != newVal.alias;
                    });
                }
                if (oldVal && oldVal.numeric === true) scope.ySeries.push(oldVal);
            });

            scope.$watch('yser', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.table[scope.row][scope.col]['yAxis'] = [];
                scope.tableArray.addAxis([scope.row, scope.col], 'y', {"alias": newVal.alias, "display_alias": newVal.display_alias});
            });

            scope.$watch('chartType', function (newVal, oldVal) {
                if (newVal === oldVal) return;
                if (newVal === "pie") {
                    scope.pie = true;
                    if (scope.yser == undefined) {
                        scope.yser = scope.ySeries[0];
                    }
                } else {
                    scope.pie = false;
                }
                // Idk if i need this...
                ctrl.editing();
                scope.tableArray.addChart([scope.row, scope.col], newVal);
            });

            scope.$watch("colors", function (newVal, oldVal) {
                // Just maintain a map of {alias: color} on the table object.
                if (newVal == oldVal) return;
                scope.tableArray.table[scope.row][scope.col]["colors"] = scope.colors;
            }, true);

            md.on('blur change', function () {
                scope.$apply(function () {
                    scope.tableArray.addMarkdown([scope.row, scope.col], scope.mdarea);
                });
            });

            scope.mdarea = '#Heading 1\n' + '##Heading 2\n' + '###Heading 3\n' +
                            '* A list of items\n' + ' - sub item\n' + '* Unordered list of items\n' + ' - Unordered list of subitems\n';

            scope.mdarea = gettext(scope.mdarea);

            scope.select = function (result, ndx, row, col) {
                if (result.selected) {
                    result.selected = false;
                } else {
                    result.selected = true;
                }
            }

            scope.setChartType = function (type) {
                scope.chartType = type;
            };

            // All sorts of UI code.
            // Methods for resizing columns
            scope.merge = function(ndx) {
                var merges = [[scope.row, scope.col - 1], [scope.row - 1, scope.col],
                              [scope.row, scope.col + 1], [scope.row + 1, scope.col]];
                scope.tableArray.mergeCol([coords, merges[ndx]]);
            }

            scope.collapse = function (dir) {
                scope.tableArray.collapseCol(coords, dir);
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
                        var arrow = $compile(arrowHtml[el])(scope);
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
                arrows = false;
            });

            // This was in config watch?
            scope.$watch(ctrl.editable, function (newVal, oldVal) {
                // This scrolls to proper chart when user switches
                // to design mode. Can't be done on load due to hidden
                // elements.
                if (newVal == oldVal) return;
                if (!scope.chartType) return;
                chartScroll();
            });
        }
    };
}]);


directives.directive('sylvaBreadcrumbs', [
    '$location',
    'parser',
    'GRAPH',
    'breadService',
    'GRAPH_NAME',
    function ($location, parser, GRAPH, breadService, GRAPH_NAME) {
    return {
        template: '<h2>' +
                    '<a href="/graphs/{{ graphSlug }}/">{{ graphName }}</a> ' +
                    '<span> &raquo; </span>' +
                    '<a ng-href="#/">{{ breadText.reports }}</a>' +
                    '<span ng-if="reportName"> &raquo; </span>' +
                    '<a ng-href="#/edit/{{ reportSlug }}" ng-click="done()">{{ reportName | cut:true:20:" ..." }}</a>' +
                    '<span ng-repeat="crumb in crumbs"> &raquo; {{crumb}} </span>' +
                  '</h2>',
        controller: function ($scope) {

            $scope.graph = GRAPH;
            $scope.graphName = GRAPH_NAME;
            $scope.graphSlug = parser.parse();
            $scope.crumbs = [];
            $scope.reportName = null;
            $scope.getLocation = function () {
                return $location.path()
            }

            $scope.done = function () {
                breadService.editing(false);
                if ($scope.crumbs[$scope.crumbs.length - 1] != "Edit") {
                    $scope.crumbs.pop()
                    $scope.crumbs.push("Edit")
                }
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
                scope.crumbs.pop();
                scope.crumbs.push('Design');
            });

            scope.$on('meta', function () {
                scope.crumbs.pop();
                scope.crumbs.push("Edit");
            });

            scope.$on('name', function (e, name) {
                scope.reportName = name;
            });
        }
    };
}]);
