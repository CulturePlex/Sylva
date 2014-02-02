var reportsDirectives = angular.module('reportsDirectives', []);

reportsDirectives.directive('resize', ['$window', function ($window) {
    return function (scope, element, attrs) {
        scope.getWinHeight = function() {
            return $window.innerHeight;
        };
 
        var setMapHeight = function(newHeight) {
            element.css('height', newHeight+ 'px');
        };
 
        scope.$watch(scope.getWinHeight, function (newValue, oldValue) {
            scope.mapHeight = scope.getWinHeight() - 200
            setMapHeight(scope.mapHeight);
        }, true);

        angular.element($window).bind('resize', function () {
            scope.$apply();
        });
    };
}]);

reportsDirectives.directive('initReport', ['$timeout', function ($timeout) {
    return function(scope, element, attrs) {
        $timeout(function() {
            scope.$apply(function () {
                console.log(attrs.token);
                scope.init(attrs.graph)
            });
        });
    }
}]);


reportsDirectives.directive('draggable', function() {
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
      },
      false
    );
    
    el.addEventListener(
      'dragend',
      function(e) {
        this.classList.remove('drag');
        return false;
      },
      false
    );
  }
});

reportsDirectives.directive('droppable', function() {
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
            },
            false
          );
          
          el.addEventListener(
            'dragenter',
            function(e) {
              this.classList.add('over');
              return false;
            },
            false
          );
          
          el.addEventListener(
            'dragleave',
            function(e) {
              this.classList.remove('over');
              
              return false;
            },
            false
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
                  fn(item.id);
                }
              });
              return false;
            },
            false
          );
    }
  }
});
