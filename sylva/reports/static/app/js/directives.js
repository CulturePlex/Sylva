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


//  TOMORROW:
//  addColumn method
//  assign ids to cells
//  write merge methods 1 - check for possibles 2 - merge 

directives.directive('syEditableTable', ['$compile', function ($compile) {
    return {
        restrict: 'A',
        link: function(scope, elem, attrs) {

            var ang = angular.element
            ,   children = elem.children()
            ,   table = ang(children[0])
            ,   tbody = ang(table.children()[1])
            ,   addRow = ang(children[1])
            ,   addCol = ang(children[2])
            ,   numRows = 2
            ,   numCols = 2
            ,   tarray = new TableArray(table);

            setTimeout(function () {
                scope.report.tarray = tarray;    
            }, 1000)
            
           
            addRow.bind('click', function () {
                //if (!scope.report.tarray) scope.report.tarray = 
                var cells = new Cells()
                ,   row = cells.getRow();
                tbody.append(row);
                scope.$apply(function () {scope.report.tarray = new TableArray(ang(elem.children()[0]))});
                //scope.$apply(function () {scope.report.numRows++});
                numRows++;
                console.log('added row', scope.report.tarray)
            });

            addCol.bind('click', function () {
                var rows = tbody.children()
                ,   id = 0;
                angular.forEach(rows, function (el) {
                    var tds = ang(el).children()
                    for (var i=0; i<tds.length; i++) {
                        ang(tds[i]).attr('id', 'cell' + id)
                        id++
                    }
                    var cell = $compile('<td sy-droppable sy-merge-cells id=cell' + id + '></td>')(scope);
                    id++
                    ang(el).append(cell)
                });
                scope.report.tarray = new TableArray(ang(elem.children()[0]))
                console.log('added col', scope.report.tarray)
                numCols++;
            });


            function Cells() {
                this.tds = '';
                var id = numRows * numCols;
                for (var i=0; i<numCols; i++) {
                    this.tds = 
                        this.tds + 
                        '<td sy-droppable sy-merge-cells id=cell' + 
                        id++ + 
                        '></td>';
                }
            };

            Cells.prototype.getRow = function() {
                var row = $compile('<tr>' + this.tds + '</tr>')(scope)
                return row;
            };

            function TableArray(table) {
                this.table = table;
                this.tableArray = [];
                var self = this
                ,   rows = ang(this.table.children()[1]).children();
                angular.forEach(rows, function (el) {
                    var row = rowMapper(el)
                    self.tableArray.push(row);
                });
                console.log('ta', this.tableArray)
            };

            TableArray.prototype.findAdjCells = function() {

            };

            TableArray.prototype.addRow = function(tr) {
                var row = rowMapper(tr);
                this.tableArray.push(row);
                console.log('added row', this.tableArray)
                
            };

            TableArray.prototype.addCol = function() {
                console.log('adding col')
                this.tableArray.map(function (el) {el.push('<td sy-droppable sy-merge-cells></td>')})
            };

            TableArray.prototype.jsonify = function() {
                console.log('jsonify')
            }

            function rowMapper(tr) {
                var row = []
                ,   tr = ang(tr).children();
                for(var i=0; i<tr.length; i++) {
                    var cell = ang(tr[i]);
                    var cellObj = {
                        id: cell.attr('id'),
                        xndx: cell.attr('row'),
                        yndx: cell.attr('col'),
                        rowspan: cell.attr('rowspan'),
                        colspan: cell.attr('colspan')
                    };
                    row.push(cellObj);
                }
                return row;
            }

            
        }
    } 
}]);

// mRENAME
directives.directive('syMergeCells', ['$parse', '$window', function ($parse, $window) {
    return {
        link: function (scope, elem, attrs) {

            var ang = angular.element
            ,   win = angular.element($window);

            elem.bind('contextmenu', function (event) {
                console.log(elem.css('width'))
                event.preventDefault();
                if (scope.report.openCtxMenu) ang("div.custom-menu").hide();
                scope.$apply(function () {
                    console.log('width', parseFloat(elem.css('width')) /  scope.report.numRows)
                    var ctxMenuEl = ang(ctxMenu)
                    elem.append(ctxMenuEl)
                    scope.report.openCtxMenu = true;  
                });
            });

            elem.bind("click", function(event) {
                console.log('click')
                ang("div.custom-menu").hide();
                scope.report.openCtxMenu = true;
            });

            win.bind('keyup', function(event) {
                if (scope.report.openCtxMenu && event.keyCode === 27) 
                    ang("div.custom-menu").hide();  
            });

            var ctxMenu = "<div class='custom-menu' title='right click to merge'><ul>" + 
                          "<li><a href=''>merge up</a><br></li>" +
                          "<li><a href=''>merge down</a><br></li>" +
                          "<li><a href=''>merge right</a><br></li>" +
                          "<li><a href=''>merge left</a><br></li>" +
                          "</ul></div>";
        }
    }
}]);

directives.directive('contextMenu', ['$window', '$parse', function($window, $parse) {
    return {
      restrict: 'A',
      link: function($scope, element, attrs) {
        var opened = false,
            openTarget,
            disabled = $scope.$eval(attrs.contextMenuDisabled),
            win = angular.element($window),
            menuElement = angular.element(document.getElementById(attrs.target)),
            fn = $parse(attrs.contextMenu);

        function open(event, element) {
          element.addClass('open');
          element.css('top', event.pageY + 'px');
          element.css('left', event.pageX + 'px');
          opened = true;
        }

        function close(element) {
          opened = false;
          element.removeClass('open');
        }

        menuElement.css('position', 'absolute');

        element.bind('contextmenu', function(event) {
          if (!disabled) {
            openTarget = event.target;
            event.preventDefault();
            event.stopPropagation();
            $scope.$apply(function() {
              fn($scope, { $event: event });
              open(event, menuElement);
            });
          }
        });

        win.bind('keyup', function(event) {
          if (!disabled && opened && event.keyCode === 27) {
            $scope.$apply(function() {
              close(menuElement);
            });
          }
        });

        function handleWindowClickEvent(event) {
          if (!disabled && opened && (event.button !== 2 || event.target !== openTarget)) {
            $scope.$apply(function() {
              close(menuElement);
            });
          }
        }

        // Firefox treats a right-click as a click and a contextmenu event while other browsers
        // just treat it as a contextmenu event
        win.bind('click', handleWindowClickEvent);
        win.bind('contextmenu', handleWindowClickEvent);
      }
    };
  }]);

directives.directive('syDroppable', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
        // again we need the native object
            var el = element[0];
            //console.log('attr', attrs)

            //console.log('link', element);
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


directives.directive('syBreadcrumbs', function () {
    return {
        controller: function($scope, breadcrumbs) {
            console.log('bread', breadcrumbs)
            console.log($scope.breadcrumb)
            $scope.$watch(breadcrumbs.breadcrumb, function (newVal, oldVal) {
                $scope.breadcrumb = newVal
            }, true);
        },
        link: function(scope, elem, attrs) {
            console.log('syBreadcrumbs')
        }
    };
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



