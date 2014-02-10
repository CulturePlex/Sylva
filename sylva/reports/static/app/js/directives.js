'use strict'


var directives = angular.module('reports.directives', []);


directives.directive('syUpdateText', function () {
    return {
        link:function(scope) {
            scope.$watch('report.name', function (newVal, oldVal) {
                scope.report.nameHtml = '<h2>' + newVal + '</h2>';
            });
        }
    }
});


directives.directive('syDatepicker', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModelCtrl) {
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


directives.directive('droppable', function() {
    return {
        scope: {
            drop: '&',
            bin: '='
        },
        link: function(scope, element) {
        // again we need the native object
            var el = element[0];
          
            el.addEventListener(
                'dragover',
                function(e) {
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
                    // Stops some browsers from redirecting.
                    if (e.stopPropagation) e.stopPropagation();
                    this.classList.remove('over');
                    var binId = this.id;
                    var item = document.getElementById(e.dataTransfer.getData('Text'));
                    scope.$apply(function(scope) {
                        var fn = scope.drop();
                        if ('undefined' !== typeof fn) {            
                            fn(binId, item.id);
                        }
                  });
                  return false;
                }, false
            );
        }
    }
});
