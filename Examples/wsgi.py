'''WSGI inject middleware  example.

You don't have to install the inject package to run the example.

Run:
    python wsgi.py
Then open http://127.0.0.1:8000/ in a browser.
'''
try:
    import inject
except ImportError:
    # Must be running without installing the inject package.
    import os
    import sys
    cwd = os.getcwd()
    parent = os.path.normpath(os.path.join(cwd, os.pardir, 'Source'))
    sys.path.append(parent)
    import inject

from inject.middleware import WsgiInjectMiddleware
from wsgiref.simple_server import make_server


@inject.appscope            # The configuration will be instantiated
class Config(object):       # only once, when injected.
    def __init__(self):
        # Just to demostrate application scope.
        self.title = 'my web app'
        self.version = '0.1'


@inject.reqscope            # The controller will be instantiated only
class Controller(object):   # once per request, when injected.
    
    @inject.param('config', Config)
    def body(self, config):
        return 'This is %s, v.%s.' % (config.title, config.version)


class Controller2(Controller):  # Inherits the default scope.
    
    def header(self):
        return 'Hello, World!'
    
    def footer(self):
        return 'Bye.'
    

class MyApp(object):

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type','text/html')])
        yield self.header()
        yield '<br />'
        yield self.body()
        yield '<br />'
        yield self.footer()
        yield '<br />'
    
    @inject.param('controller', Controller2)
    def header(self, controller):
        return controller.header()
    
    @inject.param('controller', Controller2)
    def body(self, controller):
        return controller.body()
    
    @inject.param('controller', Controller2)
    def footer(self, controller):
        return controller.footer()


myapp = MyApp()
myscopedapp = WsgiInjectMiddleware(myapp)


httpd = make_server('', 8000, myscopedapp)
print 'Serving HTTP on port 8000...'
httpd.serve_forever()