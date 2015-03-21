// Create a page object
var page, system, url, filename, domain, csrfToken, sessionId, secret;

page = require('webpage').create();
system = require('system');

url = system.args[1];
filename = system.args[2];
domain = system.args[3];
csrfToken = system.args[4];
sessionId = system.args[5];
secret = system.args[6];

phantom.addCookie({'domain': domain, 'name':'csrftoken',
                         'value': csrfToken});
phantom.addCookie({'domain': domain, 'name':'sessionid', 'value': sessionId});

// Set the page size and orientation
page.paperSize = {
    format: 'A4',
    orientation: 'landscape'};

var body = "secret=" + secret;
page.open(url, 'POST', body, function (status) {
    if (status !== 'success') {
        // If PhantomJS failed to reach the address, print a message
        console.log('Unable to load the address!', url);
        phantom.exit();
    } else {
        // If we are here, it means we rendered page successfully
        // Use "evaluate" method of page object to manipulate the web page
        // Notice I am passing the data into the function, so I can use
        // them on the page
        //page.evaluate(function(data) {
        //}, data);
        console.log('opened page')
        // Now create the filename file and exit PhantomJS
        window.setTimeout(function () {
        	page.render(filename);
        	phantom.exit();
        }, 1000);
    }
});
