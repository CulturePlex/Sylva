import os
import tempfile
from subprocess import Popen, STDOUT, PIPE
from time import time
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse


def phantom_process(scheme, netloc, view, graph_slug, template_slug, domain,
                    csrftoken, sessionid):
    temp_path = os.path.join(tempfile.gettempdir(), str(int(time() * 1000)))
    filename = '{0}.pdf'.format(temp_path)
    raster_path = finders.find('phantomjs/rasterize.js')
    url = '{0}://{1}{2}{3}#/preview/{4}'.format(
        scheme,
        netloc,
        reverse(view, kwargs={'graph_slug': graph_slug}),
        '?pdf=true',
        template_slug
    )
    print("csrftoken:", csrftoken)
    Popen([
        'phantomjs',
        raster_path,
        url,
        filename,
        domain,
        csrftoken,
        sessionid
    ], stdout=PIPE, stderr=STDOUT).wait()
    print("filename", filename)
    return filename
