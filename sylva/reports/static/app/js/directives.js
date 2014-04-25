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


directives.directive('sylvaEditableTable', ['$compile', 'tableArray', function ($compile, tableArray) {
    return {
        restrict: 'A',
        controller: function ($scope) {
            $scope.merge = null;

            this.setMerge = function(coords, mergeCoords) {
                $scope.merge = [coords, mergeCoords];
            };
        },
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   rows = ang(elem.children()[0])
            ,   rowWidth = parseInt(rows.css('width'))
            ,   buttons = ang(elem.children()[1])
            ,   addRow = ang(buttons.children()[0])
            ,   addCol = ang(buttons.children()[1])
            ,   table = prepTable(rows)
            ,   tarray = tableArray(table, rowWidth);

            scope.tableArray = tarray; 

            scope.getMerge = function () {
                return scope.merge;
            };

            scope.$watchCollection(scope.getMerge, function (newVal, oldVal) {
                if (newVal === oldVal) return;
                //scope.$apply(function () {
                    
                    scope.tableArray.mergeCol(newVal)
                    var html = scope.tableArray.htmlify()
                    $compile(rows.html(html))(scope)  
                //});
                
            });

            addRow.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addRow()
                    var html = scope.tableArray.htmlify()
                    $compile(rows.html(html))(scope)
                });
            });

            addCol.bind('click', function () {
                scope.$apply(function () {
                    scope.tableArray.addCol()
                    var html = scope.tableArray.htmlify()
                    //console.log('html', html)
                    $compile(rows.html(html))(scope)
                });
            });

            function prepTable(table) {
                var tableArray = [];
                var rowArr = ang(rows).children()
                console.log('rowArr', rowArr)
                angular.forEach(rowArr, function (el) {
                    var row = mapper(el);
                    tableArray.push(row);
                });
                return tableArray;
            };

            function mapper(tr) {
                var row = []
                ,   tr = ang(tr).children();
                for(var i=0; i<tr.length; i++) {
                    var cell = ang(tr[i])
                    ,   cellObj = {
                        id: cell.attr('id'),
                        row: cell.attr('row'),
                        col: cell.attr('col'),
                        rowspan: cell.attr('rowspan'),
                        colspan: cell.attr('colspan')
                    };
                    row.push(cellObj);        
                }
                return row;
            };
        }
    } 
}]);


directives.directive('sylvaMergeCells', ['$parse', '$compile', function ($parse, $compile) {
    return {
        require: '^sylvaEditableTable',
        scope: true,
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

            scope.merge = function(ndx) {
                var merges = [[row, col - 1], [row - 1, col], [row, col + 1], [row + 1, col]];
                console.log('dir', coords, merges[ndx])
                sylvaEditableTableCtrl.setMerge(coords, merges[ndx]);
            }

            elem.bind("click", function (event) {
                if (!arrows) {
                    ang('.arrow').remove();
                    var adjs = scope.tableArray.getAdjCells(row, col);
                    angular.forEach(adjs, function (el) {
                        var arrow = $compile(arrowHtml[el])(scope)
                        elem.append(arrow);
                    });
                    arrows = true;
                } else {
                    console.log('else', elem.children())
                    ang('.arrow').remove();
                    arrows = false;
                }
            });

            elem.bind("mouseout", function (event) {
                arrows = false
            });
        }
    }
}]);


directives.directive('sylvaDroppable', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
        // again we need the native object
            var el = element[0];
            el.addEventListener(
                'dragover',
                function(e) {
                    console.log('dragover')
                    e.dataTransfer.dropEffect = 'move';
                    // allows us to drop
                    if (e.preventDefault) e.preventDefault();
                        this.classList.add('over');
                    return false;
                }, false
            );
          
            el.addEventListener(
                'dragenter',
                function(e) {
                    console.log('dragcenter')
                    this.classList.add('over');
                    return false;
                }, false
            );
          
            el.addEventListener(
                'dragleave',
                function(e) {
                    this.classList.remove('over');
                    return false;
                }, false
            );
          
            el.addEventListener(
                'drop',
                function(e) {
                    if (e.stopPropagation) e.stopPropagation();
                    this.classList.remove('over');
                    var binId = this.id;
                    var item = document.getElementById(e.dataTransfer.getData('Text'));
                    scope.$apply(function(scope) {
                        scope.handleDrop(binId, item.id);      
                });
                  return false;
                }, false
            );
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