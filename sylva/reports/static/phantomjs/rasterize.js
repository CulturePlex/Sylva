// Create a page object
var page, system, address, filename, domain;

page = require('webpage').create();
system = require('system');

url = system.args[1];
filname = system.args[2];
domain = system.args[3].split(':')[0];
csrfToken = system.args[4];
sessionId = system.args[5];

//find domain
phantom.addCookie({'domain': domain, 'name':'csrftoken',
                   'value': csrfToken});
phantom.addCookie({'domain': domain, 'name':'sessionid',
                   'value': sessionId});

// Set the page size and orientation
page.paperSize = {
    format: 'A4',
    orientation: 'landscape'};

// Now we have everything settled, let's render the page
page.open(url, function (status) {
    if (status !== 'success') {
        // If PhantomJS failed to reach the address, print a message
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        // If we are here, it means we rendered page successfully
        // Use "evaluate" method of page object to manipulate the web page
        // Notice I am passing the data into the function, so I can use
        // them on the page
        //page.evaluate(function(data) {
        //}, data);

        // Now create the filname file and exit PhantomJS
        window.setTimeout(function () {
        	page.render(filname);
        	phantom.exit();
        }, 1000);
    }
});