'use strict'


var directives = angular.module('reports.directives', []);


directives.directive('sylvaUpdateText', function () {
    return {
        link:function(scope) {
            scope.$watch('report.name', function (newVal, oldVal) {
                scope.report.name = newVal;
            });
        }
    };
});


directives.directive('sylvaDatepicker', function () {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function(scope, element, attrs, ngModelCtrl) {
            $(function(){
                element.datepicker({
                    dateFormat:'dd/mm/yy',
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

            scope.$watch('resp', function (newVal, oldVal) {

                if (newVal == oldVal) return;

                scope.queries = scope.resp.queries;
                scope.tableArray = tableArray(scope.resp.table);
                scope.tableWidth = parseInt(angular.element(elem.parents()[0]).css('width'));
                

                var previous = elem
                ,   childScope
                ,   len = scope.tableArray.table.length;
                for (var i=0; i<len; i++) {
                    childScope = scope.$new();
                    childScope.$index = i;

                    transclude(childScope, function (clone) {
                        childScope.row = scope.tableArray.table[i];
                        previous.after(clone);
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

            scope.$watch(ctrl.getQueries, function (newVal, oldVal) {
                console.log('transclude')
                //if (newVal == oldVal) return;
                var previous = elem
                ,   childScope
                ,   len = scope.row.length
                ,   tableWidth = ctrl.getTableWidth()
                ,   tableArray = ctrl.getTableArray()
                ,   numCols = tableArray.numCols;
                console.log('stuff', tableArray)
                for (var i=0; i<len; i++) {

                    var cell = scope.row[i]
                    ,   query = cell.displayQuery
                    ,   cellWidth = tableWidth / numCols * parseInt(cell.colspan) - (numCols + 1) * 15 + 'px'
                    ,   series = ctrl.getQueries().filter(function (el) {
                        return el.name === query;
                    })[0].series;
                    

                    childScope = scope.$new();
                    childScope.$index = i;
                    childScope.cellStyle = {width: cellWidth, height: '500px'};

                    childScope.chartConfig = {
                        options: {chart: {type: cell.chartType}},
                        xAxis: {catagories: []},
                        series: [{data: series}],
                        title: {text: query},     
                        loading: false
                    };
                    console.log('row', childScope.chartConfig)
                    transclude(childScope, function (clone) {
                        previous.after(clone);
                        previous = clone
                    });
                } 
            });
        }
    };
}]);



directives.directive('syEditableTable', ['$compile', 'tableArray', function ($compile, tableArray) {
    return {
        transclude: true,
        scope: {
            resp: '='
        },
        templateUrl: '/static/app/partials/directives/editable_table.html',
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
        },
        link: function(scope, elem, attrs) {

            var ang = angular.element
            ,   rows = ang(elem.children()[0])
            ,   rowWidth = parseInt(rows.css('width'))
            ,   buttons = ang(elem.children()[1])
            ,   addRow = ang(buttons.children()[0])
            ,   addCol = ang(buttons.children()[1])
            ,   delRow = ang(buttons.children()[2])
            ,   delCol = ang(buttons.children()[3]);

            scope.$watch('resp', function (newVal, oldVal) {  

                if (newVal === oldVal) return;
                scope.queries = scope.resp.queries;
                scope.tableArray = tableArray(scope.resp.table);

                scope.tableWidth = parseInt(angular.element(elem.children()[0]).css('width'));
        
            }, true);

            addRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addRow();
                    console.log('addRow', scope.tableArray)
                });
            });

            addCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addCol();
                    console.log('addCol', scope.tableArray)
                });
            });

            delRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delRow();
                    console.log('delRow', scope.tableArray)
                });
            });

            delCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delCol();
                    console.log('delRow', scope.tableArray)
                });
            });
        }
    };
}]);


directives.directive('syEtRowRepeat', ['tableArray', '$animate', function (tableArray, $animate) {
    return {
        transclude: 'element',
        require: '^syEditableTable',
        scope: {
            queries: '='
        },
        link: function(scope, elem, attrs, ctrl, transclude) {

            //scope.$watch('queries', function (newVal, oldVal) {
            //    if (newVal == oldVal) return;
            //    drawTable()
            //}, true); 

            // store old child scopes
            var childScopes = {}

            scope.$watch(ctrl.getTableArray, function (newVal, oldVal) {
                if (newVal === oldVal) return;

                var nextTable = {}
                ,   table = false
                ,   rowIds = {}
                ,   previous = elem
                ,   childScope
                ,   tableArray = ctrl.getTableArray()
                ,   len = tableArray.table.length;


                // remove old child scopes and elements on redraw
                for (var j in childScopes) {
                    if (childScopes[j]) {
                        childScopes[j].scope.$destroy() 
                        childScopes[j].element.remove()
                        delete childScopes[j]
                    }
                }

                for (var i=0; i<len; i++) {
                    var rowId = 'row' + i;
                

                    rowIds[rowId] = true;
                    childScope = scope.$new();
                    childScope.$index = i;
                    childScopes[i] = {scope: childScope}
                    childScope.row = tableArray.table[i];

                    transclude(childScope, function (clone) {

                        if (i === len - 1) clone.addClass('bottom')
                        
                        clone.attr('id', rowId);
                        clone.addClass('trow');
                        previous.after(clone);
                        previous = clone
                        childScopes[i].element = previous
                    });
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
            row: '='
        },
        link: function(scope, elem, attrs, ctrl, transclude) {

            var previous = elem
            ,   childScope
            ,   len = scope.row.length
            ,   tableWidth = ctrl.getTableWidth()
            ,   tableArray = ctrl.getTableArray()
            ,   numCols = tableArray.numCols
            ,   childScopes = {};

            for (var i=0; i<len; i++) {
                var cell = scope.row[i];
                var query = cell.displayQuery
                ,   colspan = parseInt(cell.colspan)
                ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                ,   activeQuery = ctrl.getQueries().filter(function (el) {
                    return el.name === query;
                })[0];

                childScope = scope.$new();
                childScope.$index = i;
                childScopes[i] = childScope;
                childScope.config = {
                    row: cell.row,
                    col: cell.col,
                    queries: ctrl.getQueries(),
                    activeQuery: activeQuery,
                    chartTypes: ['column', 'scatter', 'pie', 'line'],
                    chartType: cell.chartType,
                }

                //childScope.id = cell.id
                childScope.cellStyle = {width: cellWidth, height: '175px'},
                transclude(childScope, function (clone) {
                    if (i === len - 1) clone.addClass('final')
                    clone.attr('id', cell.id)
                    previous.after(clone);
                    previous = clone;
                });
            } 
        }
    };
}]);


directives.directive('sylvaEtCell', function () {
    return {
        require: '^syEditableTable',
        scope: {
            config: '='
        },
        templateUrl: '/static/app/partials/directives/edit_cell.html',
        link: function(scope, elem, attrs, ctrl) {

            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row;
                scope.col = scope.config.col;
                scope.queries = scope.config.queries;
                scope.activeQuery = scope.config.activeQuery;
                scope.chartTypes = scope.config.chartTypes;
                scope.chartType = scope.config.chartType;
                scope.tableArray = ctrl.getTableArray();
            }, true);


            scope.$watch('activeQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.addQuery([scope.row, scope.col], newVal.name)
                if (newVal === 'markdown') {
                    scope.markdown = true;
                } else {
                    scope.markdown = false;
                }
            }); 

            scope.$watch('chartType', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.addChart([scope.row, scope.col], newVal)
            });
        }
    };
});


directives.directive('sylvaEtDispalyCell', function () {
    return {
        require: '^syEditableTable',
        scope: {
            config: '='
        },
        templateUrl: '/static/app/partials/directives/display_cell.html',
        link: function(scope, elem, attrs, ctrl) {

            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row
                scope.col = scope.config.col;
                scope.activeQuery = scope.config.activeQuery;
                scope.query = scope.activeQuery.name;
                scope.series = scope.activeQuery.series
                scope.chartType = scope.config.chartType;
                scope.tableArray = ctrl.getTableArray()


                scope.chartConfig = {
                    options: {chart: {type: scope.chartType}},
                    xAxis: {catagories: []},
                    series: [{data: scope.series}],
                    title: {text: scope.query},     
                    loading: false
                };
            }, true);
        }
    };
});











directives.directive('sylvaPreviewCell', ['$routeParams', 'api', 'parser', function ($routeParams, api, parser) {
    return {
        templateUrl: '/static/app/partials/directives/preview_cell.html',
        scope: {
            colspan: '@',
            query: '@',
            chartType: '@'
        },
        link: function (scope, elem, attrs) {
            var graph = parser.parse();
            var slug = $routeParams.reportSlug;
            api.queries.query({ // I want this shit out of the fucking directives
                graphSlug: graph,
                slug: slug
            }, function (data) {
                var queries = data.map(function (el) {
                    return {name: el.name, series: el.series} 
                });
                scope.series = queries.filter(function (el) {
                    return el.name == scope.query
                })[0].series
                scope.config.options.chart.type = scope.chartType;
                scope.config.title.text = scope.query;
                scope.config.series[0].data = scope.series;

            });
            scope.displayQuery = true;
            scope.config = {
                    options: {
                        chart: {
                            type: 'line'
                        }
                    },
                    xAxis: {
                        catagories: []
                    },
                    series: [{
                        data: []
                    }],
                       title: {
                        text: ''
                    },
                    
                    loading: false
                }
        }
    }
}]);


directives.directive('sylvaDisplayTable', ['$compile', 'tableArray', 'api', function ($compile, tableArray, api) {
    return {
        restrict: 'A',
        //templateUrl: '/static/app/partials/directives/display_table.html',
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   rows = ang(elem.children()[0])
            ,   rowWidth = parseInt(rows.css('width'))
            // need to change to full async here
            try {
                var html = scope.tableArray.displayHtml(rowWidth);
                $compile(rows.html(html))(scope);
            } catch (e) {
                api.reports.query({
                    graphSlug: scope.graph,
                    slug: scope.report.slug  
                }, function (data) {
                    scope.report = data[0];
                    scope.tableArray = tableArray(scope.report.table)
                    var html = scope.tableArray.displayHtml(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            }
            scope.$watch('editable', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                var html = scope.tableArray.displayHtml(rowWidth);
                $compile(rows.html(html))(scope); 
            });
        }
    }
}]);

directives.directive('sylvaDisplayCell', ['$compile', function ($compile) {
    return {
        scope: true,
        templateUrl: '/static/app/partials/directives/display_cell.html', 
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   arrows = false
            ,   row = parseInt(elem.attr('row')) 
            ,   col = parseInt(elem.attr('col'));

            scope.$watch('tableArray', function (newVal, oldVal) {
                                
                var cell = scope.tableArray.table[row][col];
                if (cell && cell.displayQuery) {
                    var query = scope.getQuery(cell.displayQuery)[0]
                    
                    ,   series = query.series;
                    scope.displayQuery = cell.displayQuery;
                    scope.config.options.chart.type = cell.chartType;
                    scope.config.title.text = cell.displayQuery.name;
                    scope.config.series[0].data = series;
                } else {
                    scope.displayQuery = ''
                }
            }, true);

            scope.config = {
                options: {
                    chart: {
                        type: 'line'
                    }
                },
                xAxis: {
                    catagories: []
                },
                series: [{
                    data: []
                }],
                   title: {
                    text: ''
                },
                
                loading: false
            }
        }
    }
}]);


directives.directive('sylvaEditableTable', ['$compile', 'tableArray', 'api', function ($compile, tableArray, api) {
    return {
        restrict: 'A',
        controller: function ($scope) {
            $scope.merge = null;
            $scope.setHtml = 0;

            this.setMerge = function(coords, mergeCoords) {
                $scope.merge = [coords, mergeCoords];
            };

            this.setHtml = function() {
                $scope.setHtml++;
            };
        },
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   rows = ang(elem.children()[0])
            ,   rowWidth = parseInt(rows.css('width'))
            ,   buttons = ang(elem.children()[1])
            ,   addRow = ang(buttons.children()[0])
            ,   addCol = ang(buttons.children()[1])
            ,   delRow = ang(buttons.children()[2])
            ,   delCol = ang(buttons.children()[3])
            
            try {
                var html = scope.tableArray.htmlify(rowWidth);
                // hmmmm no compile here but it seems to be working
                $compile(rows.html(html))(scope);
            } catch (e) {
                api.reports.query({
                    graphSlug: scope.graph,
                    slug: scope.report.slug  
                }, function (data) {
                    scope.report = data[0];
                    scope.tableArray = tableArray(scope.report.table)
                    var html = scope.tableArray.htmlify(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            }

            scope.getMerge = function() {
                return scope.merge;
            };

            scope.getHtml = function() {
                return scope.setHtml;
            } 

            scope.$watchCollection(scope.getMerge, function (newVal, oldVal) {
                if (newVal === oldVal) return;
                var dir = mergeDirection(newVal);
                if (dir === 'col') {
                    scope.tableArray.mergeCol(newVal);
                } else {
                    scope.tableArray.mergeRow(newVal);
                }
                var html = scope.tableArray.htmlify(rowWidth);
                $compile(rows.html(html))(scope);          
            });

            function mergeDirection(merge) {
                var a = merge[0]
                ,   b = merge[1]
                ,   dir;
                if (a[0] === b[0]) {
                    dir = 'col'
                } else {
                    dir = 'row'
                }
                return dir;
            }

            scope.$watch(scope.getHtml, function (newVal, oldVal) {
                if (newVal === oldVal) return;
                var html = scope.tableArray.htmlify(rowWidth);
                $compile(rows.html(html))(scope);
            });

            addRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addRow();
                    var html = scope.tableArray.htmlify(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            });

            addCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addCol();
                    var html = scope.tableArray.htmlify(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            });

            delRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delRow();
                    var html = scope.tableArray.htmlify(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            });

            delCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delCol();
                    var html = scope.tableArray.htmlify(rowWidth);
                    $compile(rows.html(html))(scope);
                });
            });
        }
    } 
}]);


directives.directive('sylvaMergeCells', ['$compile', function ($compile) {
    return {
        require: '^sylvaEditableTable',
        scope: true,
        templateUrl: '/static/app/partials/directives/edit_cell.html', 
        link: function (scope, elem, attrs, sylvaEditableTableCtrl) {
            var ang = angular.element
            ,   arrows = false
            ,   row = parseInt(elem.attr('row')) //this can be moved to scope.merge if necessary
            ,   col = parseInt(elem.attr('col'))
            ,   coords = [row, col]
            ,   arrowHtml = {
                    left: '<a class="arrow left" href="" ng-click="merge(0)">&#8592</a>', 
                    up: '<a class="arrow up" href="" ng-click="merge(1)">&#8593</a>',
                    right: '<a class="arrow right" href="" ng-click="merge(2)">&#8594</a>',
                    down: '<a class="arrow down" href="" ng-click="merge(3)">&#8595</a>'
            };  

            scope.chartType = scope.tableArray.table[row][col].chartType;
            scope.displayQuery = scope.tableArray.table[row][col].displayQuery;

            scope.$watch('displayQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.addQuery([row, col], newVal.name)
                if (newVal === 'markdown') {
                    scope.markdown = true;
                } else {
                    scope.markdown = false;
                }
            }); 

            scope.$watch('chartType', function (newVal, oldVal) {
                //write a method for this on the TableArray
                if (newVal == oldVal) return;
                //scope.$apply(function () {
                    scope.tableArray.addChart([row, col], newVal)
                //})
                

            })

            scope.merge = function(ndx) {
                var merges = [[row, col - 1], [row - 1, col], [row, col + 1], [row + 1, col]];
                sylvaEditableTableCtrl.setMerge(coords, merges[ndx]);
            }

            scope.delQuery = function() {
                scope.tableArray.delQuery([row, col]);
                sylvaEditableTableCtrl.setHtml();
            }

            elem.bind("click", function (event) {
                if (!arrows) {
                    ang('.arrow').remove();
                    var adjs = scope.tableArray.getAdjCells(row, col);
                    angular.forEach(adjs, function (el) {
                        var arrow = $compile(arrowHtml[el])(scope);
                        elem.append(arrow);
                    });
                    arrows = true;
                } else {
                    ang('.arrow').remove();
                    arrows = false;
                }
            });

            elem.bind("mouseout", function (event) {
                arrows = false;
            });
        }

    }
}]);



