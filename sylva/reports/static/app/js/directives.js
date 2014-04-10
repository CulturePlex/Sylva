'use strict'


var directives = angular.module('reports.directives', []);


directives.directive('syUpdateText', function () {
    return {
        link:function(scope) {
            scope.$watch('report.name', function (newVal, oldVal) {
                scope.report.nameHtml = '<h2>' + newVal + '</h2>';
            });
        }
    };
});


directives.directive('syDatepicker', function () {
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


directives.directive('syEditableTable', ['$compile', function ($compile) {
    return {
        restrict: 'A',
        link: function(scope, elem, attrs) {
            var ang = angular.element
            ,   table = ang(elem.children()[0])
            ,   rowCont = ang(table.children()[0])
            ,   rowWidth = parseInt(rowCont.css('width'))
            ,   buttons = ang(table.children()[1])
            ,   addRow = ang(buttons.children()[0])
            ,   addCol = ang(buttons.children()[1])
            ,   numRows = 2
            ,   numCols = 2
            ,   tarray = new TableArray(rowCont);
            setTimeout(function () {
                scope.report.tarray = tarray;    
            }, 1000)
           

            addRow.bind('click', function () {
                var cells = ''
                ,   yndx = numRows
                ,   id = numRows * numCols
                ,   lastRow = rowCont.children()[numRows - 1]
                ,   width = rowWidth / numCols - ((numCols + 1) * 2 / numCols) + 'px';
                ang('.tcell').css('width', width);
                ang('.tcell-final').css('width', width);
                ang(lastRow).removeClass('bottom');
                for (var i = 0; i < numCols; i++) {
                    if (i === numCols - 1) {
                        cells += 
                            '<div sy-droppable sy-merge-cells class="tcell final" id="cell' + 
                            id++ + 
                            '" style="width:' + 
                            width + 
                            ';" row="' +
                            yndx +
                            '" rowspan="' +
                            1 +
                            '" col="' +
                            i +
                            '" colspan="' +
                            1 + 
                            '">';
                    } else {
                        // compile cells during this step???
                        cells += 
                            '<div sy-droppable sy-merge-cells class="tcell" id="cell' + 
                            id++ + 
                            '" style="width:' + 
                            width + 
                            ';" row="' +
                            yndx +
                            '" rowspan="' +
                            1 +
                            '" col="' +
                            i +
                            '" colspan="' +
                            1 + 
                            '"></div>';
                    }
                }
                var bottomRow = $compile('<div class="trow bottom">' + cells + '</div>')(scope)
                rowCont.append(bottomRow);
                // add row method here for model data structure instead of new array
                scope.$apply(function () {
                    scope.report.tarray = new TableArray(rowCont)
                });
                numRows++;
            });


            addCol.bind('click', function () {
                //if (numCols < 4) {     
                    var rows = rowCont.children()
                    ,   id = 0
                    ,   width = rowWidth / (numCols + 1) - ((numCols + 2) * 2 / (numCols + 1)) + 'px';
                    for (var i = 0; i < rows.length; i++) {
                        var row = rows[i]
                        ,   cells = ang(row).children();
                        ang(cells[cells.length - 1]).removeClass('final');
                        for (var k = 0; k < cells.length; k++) {
                            var cellClass = ang(cells[k])[0].classList[0];
                            ang(cells[k]).attr('id', 'cell' + id).css('width', width);
                            id++;
                        }
                        var cell = $compile(
                            '<div sy-droppable sy-merge-cells class="tcell final" id="cell' + 
                            id + 
                            '" style="width:' + 
                            width + 
                            '" row="' +
                            i +
                            '" rowspan="' +
                            1 +
                            '" col="' +
                            row.length +
                            '" colspan="' +
                            1 +
                            '">'
                        )(scope);
                        ang(row).append(cell);
                        id++;
                    }
                    numCols++;
                    scope.$apply(function () {
                        scope.report.tarray = new TableArray(rowCont);
                     });
                //} else {
                //    alert('Max 4 Columns, add as many rows as you want')
                //}
            });


            //This should be a provider
            function TableArray(table) {
                this.tableArray = [];
                var self = this
                ,   rows = ang(table.children());
                angular.forEach(rows, function (el) {
                    var row = rowMapper(el)
                    self.tableArray.push(row);
                });
            };

            TableArray.prototype.findAdjCells = function(row, col) {
                var adjs = [];
                if (this.tableArray[row][col - 1]) adjs.push('left');
                if (row !== 0 && this.tableArray[row - 1][col]) adjs.push('up');
                if (this.tableArray[row][col + 1]) adjs.push('right');
                if (row < this.tableArray.length - 1 && this.tableArray[row + 1][col]) adjs.push('down');
                return adjs;
            };

            TableArray.prototype.addRow = function(tr) {
                var row = rowMapper(tr);
                this.tableArray.push(row);                
            };

            TableArray.prototype.addCol = function() {
                this.tableArray.map(function (el) {
                    el.push('<td sy-droppable sy-merge-cells></td>')
                });
            };

            TableArray.prototype.jsonify = function() {
                console.log('jsonify')
            }


            function rowMapper(tr) {
                var row = []
                ,   tr = ang(tr).children();
                for(var i=0; i<tr.length; i++) {
                    var cell = ang(tr[i]);
                    if (cell[0].classList[0] !== 'divider') {
                        var cellObj = {
                            id: cell.attr('id'),
                            xndx: cell.attr('row'),
                            yndx: cell.attr('col'),
                            rowspan: cell.attr('rowspan'),
                            colspan: cell.attr('colspan')
                        };
                        row.push(cellObj);
                    }
                }
                return row;
            }    
        }
    } 
}]);


directives.directive('syMergeCells', ['$parse', '$window', function ($parse, $window) {
    return {
        link: function (scope, elem, attrs) {

            var ang = angular.element
            ,   win = angular.element($window)
            ,   arrows = false
            ,   arrowHtml = {
                    left: '<a class="arrow">&#8592</a>', 
                    up: '<a class="arrow">&#8593</a>',
                    right: '<a class="arrow">&#8594</a>',
                    down: '<a class="arrow">&#8595</a>'
            };
            

            elem.bind("mouseover", function (event) {
                if (!arrows) {
                    console.log(elem.attr('row'))
                    var row = parseInt(elem.attr('row'))
                    ,   col = parseInt(elem.attr('col'))
                    ,   adjs = scope.report.tarray.findAdjCells(row, col);
                    angular.forEach(adjs, function (el) {
                        elem.append(arrowHtml[el]);
                    });
                    arrows = true;   
                }  
            });


            elem.bind("mouseout", function (event) {
                elem.remove('#arrow')
                ang('.arrow').remove()
                arrows = false;
            });
        }
    }
}]);


directives.directive('syDroppable', function() {
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