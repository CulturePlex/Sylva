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

            var childScopes = []
            ,   parent = elem.parent();

            console.log('widthattr', attrs.width)
            scope.tableWidth = parseInt(attrs.width)
            //scope.tableWidth = parseInt(angular.element(elem.parents()[0]).css('width'));

            scope.$watch('resp', function (newVal, oldVal) {

                if (newVal == oldVal) return;
                scope.queries = scope.resp.queries;
                scope.tableArray = tableArray(scope.resp.table);

                var scopesLen = childScopes.length;
                if (scopesLen > 0) {
                    for (var i=0; i<scopesLen; i++) {
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


directives.directive('sylvaPvCellRepeat', ['$compile', function ($compile) {
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
            ,   numCols = tableArray.numCols;

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
                ,   colspan = parseInt(cell.colspan)
                ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                ,   block;

                if (query) {
                    var series = ctrl.getQueries().filter(function (el) {
                        return el.name === query;
                    })[0].series;
                }
                    
                childScope = scope.$new();
                childScope.$index = i;
                childScope.cellStyle = {width: cellWidth};
                childScope.query = query;
                childScope.chartConfig = {
                    options: {chart: {type: cell.chartType}},
                    xAxis: {catagories: []},
                    series: [{data: series}],
                    title: {text: query},     
                    loading: false
                };

                console.log('query', childScope.query)
                transclude(childScope, function (clone) {

                    //var test = $compile('<div highchart config="chartConfig" ng-style="cellStyle" class="display-cell"></div>')(childScope)
                    //clone.append(test)
                    previous.after(clone);
                    block = {}
                    block.element = previous
                    block.scope = childScope
                    childScopes.push(block)
                    previous = clone
                });
            } 
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
                });
            });

            addCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addCol();
                });
            });

            delRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delRow();
                });
            });

            delCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.delCol();
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

            var childScopes = [];

            scope.$watch(ctrl.getTableArray, function (newVal, oldVal) {
                if (newVal === oldVal) return;
                console.log('table Array', ctrl.getTableArray())
                var nextTable = {}
                ,   table = false
                ,   previous = elem
                ,   childScope
                ,   tableArray = ctrl.getTableArray()
                ,   len = tableArray.table.length
                ,   scopesLen = childScopes.length;

                if (scopesLen > 0) {
                    for (var i=0; i<scopesLen; i++) {
                        childScopes[i].element.remove();
                        childScopes[i].scope.$destroy();
                    }
                    childScopes = [];
                }

                for (var i=0; i<len; i++) {
                    var rowId = 'row' + i
                    ,   block;
                
                    childScope = scope.$new();
                    childScope.$index = i;
                    childScope.row = tableArray.table[i];

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
            ,   childScopes = []
            ,   scopesLen = childScopes.length
            ,   block;


            if (scopesLen > 0) {
                for (var i=0; i<scopesLen; i++) {
                    childScopes[i].element.remove();
                    childScopes[i].scope.$destroy();
                    
                }
                childScopes = [];
            }

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
                childScope.config = {
                    row: cell.row,
                    col: cell.col,
                    queries: ctrl.getQueries(),
                    activeQuery: activeQuery,
                    chartTypes: ['column', 'scatter', 'pie', 'line'],
                    chartType: cell.chartType,
                }

                childScope.cellStyle = {width: cellWidth},
                transclude(childScope, function (clone) {
                    if (i === len - 1) clone.addClass('final')
                    clone.attr('id', cell.id)
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
                var name;
                console.log('newval', newVal)
                if (newVal != null) {
                    name = newVal.name || '';
                } else {
                    name = '';
                }
                scope.tableArray.addQuery([scope.row, scope.col], name)
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