// Karma configuration
// Generated on Mon Apr 13 2015 14:38:01 GMT-0400 (EDT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: './',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
        'third_party/angular/angular.min.js',
        'third_party/angular/angular-route.min.js',
        'third_party/angular/angular-mocks.js',
        'third_party/angular/*.min.js',
        'third_party/angular/*.js',
        'third_party/*.js',
        '../../../../sylva/static/js/jquery.1.8.3.js',
        'app.js',
        '../../../fixtures/mock_urls.js',
        '*.js'
      ],


    // list of files to exclude
    exclude: [
    'third_party/jquery.ui.timepicker.js'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
        "app.js": "coverage",
        "controllers.js": "coverage" ,
        "directives.js": "coverage",
        "filters.js": "coverage",
        "servicess.js": "coverage"
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage'],

    coverageReporter: {
        type: 'lcov',
        dir: 'coverage/'
    },


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Firefox'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
