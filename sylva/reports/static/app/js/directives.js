'use strict'


var directives = angular.module('reports.directives', []);


var gettext = window.gettext || String;


directives.directive('sylvaUpdateText', ['breadService', function (breadService) {
    return {
        link:function(scope) {
            scope.$watch('template.name', function (newVal, oldVal) {
                breadService.updateName(newVal);
                scope.template.name = newVal
            });
        }
    };
}]);


directives.directive('sylvaDatepicker', function () {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function(scope, element, attrs, ngModelCtrl) {
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


directives.directive('sylvaPvCellRepeat', [function () {
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

            for (var i=0; i<len; i++) {
                var cell = scope.row[i]
                ,   query = cell.displayQuery
                ,   series = cell.series
                ,   name = cell.name
                ,   colspan = parseInt(cell.colspan)
                ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                ,   block;      
                    
                childScope = scope.$new();
                childScope.$index = i;
                childScope.cellStyle = {width: cellWidth};

                if (query) {
                    if (!series) {
                        query = ctrl.getQueries().filter(function (el) {
                                return el.id === query;
                            })[0];
                        series = query.series;
                        name = query.name;
                    }
                    childScope.query = query;
                    childScope.chartConfig = {
                        options: {chart: {type: cell.chartType}},
                        xAxis: {catagories: []},
                        series: [{data: series}],
                        title: {text: name},     
                        loading: false
                    };
                } else if (cell.displayMarkdown) {
                    childScope.markdown = cell.displayMarkdown;
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
    };
}]);


directives.directive('syEditableTable',['tableArray', 'DJANGO_URLS', 
                                        'breadService', 
                                        function (tableArray, DJANGO_URLS, breadService) {
    return {
        transclude: true,
        scope: {
            resp: '=',
            prev: '=',
            editable: '='
        },
        template:   '<div class="editable-table">' +
                        '<div class="edit-rows">' + 
                          '<div sy-et-row-repeat class="editable-row" queries="queries">' + 
                            '<div sylva-et-cell-repeat class="tcell" row="row" rownum="rownum">' + 
                              '<div sylva-et-cell config="config" class="query" ng-style="cellStyle">' + 
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
        },
        link: function(scope, elem, attrs) {

            var ang = angular.element
            //,   rows = ang(elem.children()[0])
            //,   rowWidth = parseInt(rows.css('width'))
            ,   rows = ang(ang(elem.children()[0]).children()[0])
            ,   buttons = ang(elem.children()[1])
            ,   editMeta = ang(buttons.children()[0])
            ,   addRow = ang(buttons.children()[1])
            ,   addCol = ang(buttons.children()[2])
            ,   delRow = ang(buttons.children()[3])
            ,   delCol = ang(buttons.children()[4]);

            scope.buttonText = {
                done: gettext('Done'),
                plusrow: gettext('+ row'),
                minusrow: gettext('- row'),
                pluscol: gettext('+ col'),
                minuscol: gettext('- col')
            }

            scope.done = gettext('Done');
            scope.plusrow = gettext('+ row')
            scope.plusrow = gettext('+ row')
            scope.plusrow = gettext('+ row')

            scope.$watch('resp', function (newVal, oldVal) {  
                if (newVal === oldVal) return;
                scope.tableArray = tableArray(scope.resp.table);
                scope.tableWidth = parseInt(rows.css('width'));

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
                });
            });

            addCol.bind('click', function () {
                if (scope.tableArray.numCols < 4) {
                    scope.$apply(function () {
                        scope.tableArray.addCol();
                    });
                }
            });

            delRow.bind('click', function () {
                if (scope.tableArray.numRows > 1)  {
                    scope.$apply(function () {
                        scope.tableArray.delRow();
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
                            if (i === len - 1) clone.addClass('bottom')
                            
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
                    childScopes[numScopes - 1].element.removeClass('bottom')

                    transclude(childScope, function (clone) {
                        clone.addClass('bottom')
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
                    childScopes.splice(numScopes - 1, 1)
                    childScopes[numScopes - 2].element.addClass('bottom');
                    previous = childScopes[numScopes - 2].element
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
                        var activeX = activeQuery.results.filter(function (el) {
                            return el.alias === xAxis;
                        })[0];
                        var activeY = activeQuery.results.filter(function (el) {
                            return el.alias === yAxis;
                        })[0];
                    }
                    childScope = scope.$new();
                    childScope.$index = i;
                    childScope.config = {
                        row: scope.rownum,
                        col: i,
                        colspan: cell.colspan,
                        activeX: activeX,
                        activeY: activeY,
                        queries: ctrl.getQueries(),
                        activeQuery: activeQuery,
                        chartTypes: ['column', 'scatter', 'pie', 'line'],
                        chartType: cell.chartType,
                    };
                    
                    childScope.cellStyle = {width: cellWidth};
                    transclude(childScope, function (clone) {

                        if (i === len - 1) {clone.addClass('final')}
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
directives.directive('sylvaEtCell', ['$sanitize', '$compile', 'DJANGO_URLS', function ($sanitize, $compile, DJANGO_URLS) {
    return {
        require: '^syEditableTable',
        scope: {
            config: '='
        },
        template:   '<div class="row">' +
                        '<label class="chart-select">' + 
                            '{{ selectText.content }}' + 
                        '</label>' + 
                        '<select ng-model="activeQuery" value="query.id" ng-options="query.name group by query.group for query in queries">' + 
                            '<option value="">-----</option>' + 
                        '</select> ' + 
                    '</div>' + 
                    '<hr>' +
                    '<div ng-hide="md" class="edit-cell-inside">' +
                        '<div class="row">' +
                            '<div class="col chartcol">' +
                                '<label>' + 
                                    '{{ selectText.chartType }}' + 
                                '</label>' + 
                                '<div class="highchart-cont">' +
                                    '<div ng-repeat="(chartType, options) in selectConfig">' + 
                                        '<div highchart config=options></div>' +
                                    '</div>' + 
                                '</div>' +
                            '</div>' +
                            '<div class="col cellcol">' +
                                '<label>{{ selectText.xSeries }}</label>' +
                                '<select ng-model="activeX" ng-value="result" ng-options="result.trueAlias for result in xSeries">' + 
                                '</select>' +
                                '<label>{{ selectText.ySeries }}</label><br>' + 
                                '<label ng-repeat="result in ySeries">' + 
                                    '<input type="checkbox" ng-model="result.selected" value="{{result.alias}}" />' + 
                                        '{{ result.trueAlias }} ' +
                                '</label>' +
                                '<br>' + 
                                '</select>' +  
                            '</div>' +
                        '</div>' +
                    '</div>' + 
                    '<div ng-show="md">' +  
                      '<textarea ng-model="mdarea" class="markdown">' + 
                      '</textarea>' + 
                      '</div>' + 
                    '</div>',
        link: function(scope, elem, attrs, ctrl) {
            var ang = angular.element
            ,   mdDiv = ang(elem.children()[1])
            ,   md = ang(mdDiv.children()[1])
            ,   stepChild = ang(ang(ang(elem.children()[2]).children()[0])[0]).children()
            ,   chartCol = ang(stepChild[0])
            ,   cellCol = ang(stepChild[1])
            ,   results
            ,   coords
            ,   arrows = false
            ,   cellWidth

            ,   arrowHtml = {
                    left: '<a class="arrow left" title="merge left" ng-href="" ng-click="merge(0)">&#8592</a>',
                    right: '<a class="arrow right" title="merge right" ng-href="" ng-click="merge(2)">&#8594</a>',
                    rightIn: '<a class="arrow right-in" title="collapse right" ng-href="" ng-click="collapse(0)">&#8594</a>',
                    leftIn: '<a class="arrow left-in" title="collapse left" ng-href="" ng-click="collapse(1)">&#8592</a>'
            };

            //console.log('elem', ang(ang(elem.parent()[0])[0]))

            scope.selectConfig = {
                bar: {
                    options: {
                        chart: {
                            type: 'bar'
                        } 
                    },
                    series: [{
                        data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]],
                    }],

                    size: {
                        width: 200,
                        height: 200
                    },
                    title: {text: 'bar'}
                },
                scatter: {
                    options: {
                        chart: {
                            type: 'scatter'
                        } 
                    },
                    series: [{
                        data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]],
                    }],

                    size: {
                        width: 200,
                        height: 200
                    },
                    title: {text: 'scatter'}
                },
                line: {
                    options: {
                        chart: {
                            type: 'line'
                        } 
                    },
                    series: [{
                        data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]],
                    }],

                    size: {
                        width: 200,
                        height: 200
                    },
                    title: {text: 'line'}
                },
                pie: {
                    options: {
                        chart: {
                            type: 'pie'
                        } 
                    },
                    series: [{
                        data: [[1, 6], [2, 6.5], [3, 7], [4, 7.5]],
                    }],

                    size: {
                        width: 200,
                        height: 200
                    },
                    title: {text: 'pie'}
                }
            }
                
            scope.selectText = {
                content: gettext('Content'),
                chartType: gettext('Chart Type'),
                xSeries: gettext('X-Series'),
                ySeries: gettext('Y-Series')
            }

            scope.merge = function(ndx) {

                var merges = [[scope.row, scope.col - 1], [scope.row - 1, scope.col], [scope.row, scope.col + 1], [scope.row + 1, scope.col]];
                scope.tableArray.mergeCol([coords, merges[ndx]]);
            }

            scope.collapse = function (dir) {
                scope.tableArray.collapseCol(coords, dir)
            }


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

            elem.bind("mouseout", function (event) {
                arrows = false
            });


            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row;
                scope.col = scope.config.col;
                scope.colspan = scope.config.colspan;
                coords = [scope.row, scope.col]
                scope.queries = scope.config.queries;
                scope.activeQuery = scope.config.activeQuery;
                if (!scope.activeX) scope.activeX = scope.config.activeX;
                //if (scope.config.activeY) scope.config.activeY.selected = true;
                scope.activeY = scope.config.activeY;
                scope.chartTypes = scope.config.chartTypes;
                scope.chartType = scope.config.chartType;
                scope.tableArray = ctrl.getTableArray();
                cellWidth = elem.width()
                chartCol.width(cellWidth * 0.4)
                cellCol.width(cellWidth * 0.4)
                if (scope.activeQuery) {
                    results = scope.activeQuery.results.filter(function (el) {
                            return el.properties.length > 0;
                        });
                    trueAlias(results)
                    var result_dict = findCatagorical(results)
                    scope.xSeries = result_dict.cat.concat(result_dict.num)
                    if (!scope.activeX) scope.activeX = scope.xSeries[0]
                    scope.ySeries = result_dict.num
                    console.log('resultsY', scope.ySeries)
                }
            }, true);

            var findCatagorical = function (results) {
                var catagorical = []
                ,   numeric = [];
                for (var i=0; i<results.length; i++) {
                    var result = results[i]
                    ,   props = result.properties[0]
                    ,   datatype = props.datatype;
                    if (datatype !== 'number' && datatype !== 'float' && 
                            datatype !== 'auto_increment' &&
                            datatype !== 'auto_increment_update' && 
                            props.aggregate === false) {
                        catagorical.push(result)
                    } else {
                        numeric.push(result)
                    }
                }
                return {cat: catagorical, num: numeric}
            }

            var trueAlias = function (results) {
                for (i=0; i<results.length; i++) {
                    var result = results[i]
                    ,   agg;
                    if (result.properties[0].aggregate) {
                        agg = result.properties[0].aggregate + ' of '
                    } else {
                        agg = ''
                    }
                    results[i]['trueAlias'] = result.alias + '. ' + agg + result.properties[0].property;
                }
            }
    

            md.on('blur keyup change', function () {
                
                var showdown = new Showdown.converter({})
                ,   html = $sanitize(showdown.makeHtml(scope.mdarea))
                ,   markdown = html;
                //,   markdown = html);
                scope.$apply(function () {
                    scope.tableArray.addMarkdown([scope.row, scope.col], markdown);    
                });
            });

            //// OK do somehting like this
            // Then make the markdown rendering a function 
            // Call when user calls markdown
            scope.mdarea = '#Heading 1\n' + 'Heading 1\n========\n'+ '##Heading 2\n' + 'Heading 2\n--------------\n' + '###Heading 3\n' +
                            '1. First item\n' + '2. Second item\n\n' + '+ Unordered items\n' + '- Unordered items\n' + '* Unordered items\n';

            scope.mdarea = gettext(scope.mdarea);

            scope.$watch('activeQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.activeQuery = newVal
                ctrl.editing()
                var name;
                if (newVal != null) {
                    name = newVal.id || '';
                    if (name === 'markdown') {
                        scope.md = true;
                        name = '';
                    } else {
                        scope.md = false;
                        results = newVal.results.filter(function (el) {
                            return el.properties.length > 0;
                        });
                        trueAlias(results);
                        var result_dict = findCatagorical(results)
                        scope.xSeries = result_dict.cat.concat(result_dict.num)
                        if (!scope.activeX) scope.activeX = scope.xSeries[0]
                        scope.ySeries = result_dict.num

                    }
                } else {
                    name = '';
                }

                scope.tableArray.addQuery([scope.row, scope.col], name)
            }); 

            scope.$watch('activeX', function (newVal, oldVal) {
                if (!newVal) return;  
                scope.tableArray.addAxis([scope.row, scope.col], 'x', newVal.alias)
            })

            scope.$watch('ySeries', function (newVal, oldVal) {  
                console.log('newVal', newVal)
                if (!newVal) return;
                if (newVal[0].selected === true) {
                    scope.tableArray.addAxis([scope.row, scope.col], 'y', newVal[0].alias)
                    console.log('ta', scope.tableArray)
                } else {
                    scope.tableArray.removeAxis([scope.row, scope.col], 'y')
                    console.log('rmoveta', scope.tableArray)
                }
            }, true)

            scope.$watch('chartType', function (newVal, oldVal) {
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
                    '<span ng-repeat="crumb in crumbs">&raquo; {{crumb}} </span>' +
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
                if (newVal === oldVal) return;
                var location = scope.getLocation();
                if (location !== '/' ) {
                    var crumbs = location.split('/')
                    
                    crumbs.splice(0, 1)
                    scope.reportSlug = crumbs.splice(crumbs.length - 1, 1)[0]
                    
                    crumbs[0] = crumbs[0].charAt(0).toUpperCase() + crumbs[0].slice(1);
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
