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
                ,   colspan = parseInt(cell.colspan)
                ,   cellWidth = (tableWidth / numCols - ((numCols + 1) * 2 / numCols)) * colspan + (2 * (colspan - 1)) + 'px'
                ,   block;      
                    
                childScope = scope.$new();
                childScope.$index = i;
                childScope.cellStyle = {width: cellWidth};

                if (query) {
                    var series = ctrl.getQueries().filter(function (el) {
                        return el.name === query;
                    })[0].series;

                    childScope.query = query;
                    childScope.chartConfig = {
                        options: {chart: {type: cell.chartType}},
                        xAxis: {catagories: []},
                        series: [{data: series}],
                        title: {text: query},     
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
            //,   rows = ang(elem.children()[0])
            //,   rowWidth = parseInt(rows.css('width'))
            ,   buttons = ang(elem.children()[1])
            ,   addRow = ang(buttons.children()[0])
            ,   addCol = ang(buttons.children()[1])
            ,   delRow = ang(buttons.children()[2])
            ,   delCol = ang(buttons.children()[3]);

            scope.$watch('resp', function (newVal, oldVal) {  

                if (newVal === oldVal) return;
                scope.tableArray = tableArray(scope.resp.table);
                scope.tableWidth = parseInt(angular.element(elem.children()[0]).css('width'));

                scope.queries = [{name: 'markdown', group: 'text'}];

                angular.forEach(scope.resp.queries, function (query) {
                    query['group'] = 'queries';
                    scope.queries.push(query);
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
        scope: {
            //queries: '='
        },
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
            row: '='
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
                    };
                    childScope.cellStyle = {width: cellWidth};

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
            });
        }            
    };
}]);


directives.directive('sylvaEtCell', ['$sanitize', function ($sanitize) {
    return {
        require: '^syEditableTable',
        scope: {
            config: '='
        },
        templateUrl: '/static/app/partials/directives/edit_cell.html',
        link: function(scope, elem, attrs, ctrl) {
            var ang = angular.element
            ,   mdDiv = ang(elem.children()[1])
            ,   md = ang(mdDiv.children()[1]);

            scope.$watch('config', function (newVal, oldVal) {
                scope.row = scope.config.row;
                scope.col = scope.config.col;
                scope.queries = scope.config.queries;
                scope.activeQuery = scope.config.activeQuery;
                scope.chartTypes = scope.config.chartTypes;
                scope.chartType = scope.config.chartType;
                scope.tableArray = ctrl.getTableArray();
            }, true);
    
            md.on('blur', function () {
                console.log('html', md.html())
                var showdown = new Showdown.converter({})
                ,   html = showdown.makeHtml(md.text())
                ,   markdown = $sanitize(html);
         
                scope.$apply(function () {
                    scope.tableArray.addMarkdown([scope.row, scope.col], markdown);
                    console.log(scope.tableArray)
                });
            });

            scope.$watch('activeQuery', function (newVal, oldVal) {
                if (newVal == oldVal) return;

                var name;

                if (newVal != null) {
                    name = newVal.name || '';
                } else {
                    name = '';
                }

                if (name === 'markdown') {
                    scope.md = true;
                    name = '';
                } else {
                    scope.md = false;
                }
                console.log('md', scope.md)
                scope.tableArray.addQuery([scope.row, scope.col], name)
            }); 

            scope.$watch('chartType', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.addChart([scope.row, scope.col], newVal)

            });
        }
    };
}]);


directives.directive('sylvaBreadcrumbs', ['$location', 'parser', 'GRAPH', function ($location, parser, GRAPH) {
    return {
        templateUrl: '/static/app/partials/directives/breadcrumbs.html',
        controller: function ($scope) {

            $scope.graph = GRAPH;
            $scope.graphSlug = parser.parse();

            $scope.getLocation = function () {
                return $location.path()
            }
        },
        link: function (scope, elem, attrs) {
            
            scope.$watch(scope.getLocation, function (newVal, oldVal) {
                var location = scope.getLocation();
                if (location !== '/' ) {
                    scope.crumbs = location.split('/')
                    scope.crumbs.splice(0, 1)
                    scope.crumbs[0] = scope.crumbs[0].charAt(0).toUpperCase() + scope.crumbs[0].slice(1);
                } else {
                    scope.crumbs = [];
                } 
            });
        }
    };
}]);
