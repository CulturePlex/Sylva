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


directives.directive('sylvaDisplayTable', ['tableArray', 'api', function (tableArray, api) {
    return {
        restrict: 'A',
        //templateUrl: '/static/app/partials/directives/display_table.html',
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   rows = ang(elem.children()[0])
            ,   rowWidth = parseInt(rows.css('width'))
            // need a display
            try {
                var html = scope.tableArray.displayHtml(rowWidth);
                rows.html(html);
            } catch (e) {
                api.reports.query({
                    graphSlug: scope.graph,
                    slug: scope.report.slug  
                }, function (data) {
                    scope.report = data[0];
                    scope.tableArray = tableArray(scope.report.table)
                    var html = scope.tableArray.displayHtml(rowWidth);
                    rows.html(html);
                });
            }
            console.log('dir', scope.tableDisplay)
            scope.$watch('editable', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                var html = scope.tableArray.displayHtml(rowWidth);
                rows.html(html); 
            });
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
                console.log('newVal', newVal)
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

            scope.query = scope.tableArray.table[row][col].query;
            scope.$watch('query', function (newVal, oldVal) {
                if (newVal == oldVal) return;
                scope.tableArray.addQuery([row, col], newVal)
                if (newVal === 'markdown') {
                    scope.markdown = true;
                } else {
                    scope.markdown = false;
                }
            }); 

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


directives.directive('sylvaDroppable', function() {
    return {
        require: '^sylvaEditableTable',
        restrict: 'A',
        link: function(scope, elem, attrs, sylvaEditableTableCtrl) {
        // again we need the native object
            var row = parseInt(elem.attr('row')) //this can be moved to scope.merge if necessary
            ,   col = parseInt(elem.attr('col'))
            ,   el = elem[0];
            el.addEventListener('dragover', function(e) {
                console.log('dragover')
                e.dataTransfer.dropEffect = 'move';
                // allows us to drop
                if (e.preventDefault) e.preventDefault();
                this.classList.add('over');
                return false;
            }, false);
          
            el.addEventListener('dragenter', function(e) {
                console.log('dragcenter')
                this.classList.add('over');
                return false;
            }, false);
          
            el.addEventListener('dragleave', function(e) {
                this.classList.remove('over');
                return false;
            }, false);
          
            el.addEventListener('drop', function(e) {
                if (e.stopPropagation) e.stopPropagation();
                this.classList.remove('over');
                var binId = this.id;
                var item = document.getElementById(e.dataTransfer.getData('Text'));
                console.log('drop', this, item)
                scope.$apply(function(scope) {
                    scope.tableArray.addQuery([row, col], item.id);
                    sylvaEditableTableCtrl.setHtml();    
                });
              return false;
            }, false);  
        }
    }
});


directives.directive('draggable', function() {
    return function(scope, element) {
        // this gives us the native JS object
        var el = element[0];
    
        el.draggable = true;
        
        el.addEventListener(
            'dragstart',
            function(e) {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('Text', this.id);
                this.classList.add('drag');
                return false;
            }, false
        );
        
        el.addEventListener(
            'dragend',
            function(e) {
                this.classList.remove('drag');
                return false;
            }, false
        );
    }
});