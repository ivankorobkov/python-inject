'''WSGI inject middleware a bit more complex example.

You don't have to install the inject package to run the example.

Run:
    python wsgi_complex.py
Then open http://127.0.0.1:8000/ in a browser.

Every time you reload a page, requests counter increases by 2. 
It is not a bug, don't forget about every browser making a request 
for a favicon.
'''
try:
    import inject
except ImportError:
    # Must be running as an example without 
    # installing the inject package.
    import os
    import sys
    cwd = os.getcwd()
    parent = os.path.normpath(os.path.join(cwd, os.pardir, 'Source'))
    sys.path.append(parent)
    import inject

from datetime import datetime
from inject.middleware import WsgiInjectMiddleware
from wsgiref.simple_server import make_server


#==============================================================================
# WSGI Application 
#==============================================================================

class Hello(object):
    
    '''Hello string with a request counter.'''
    
    counter = 0
    
    def __init__(self):
        self.__class__.counter += 1
    
    def __str__(self):
        s = ''
        if self.counter == 1:
            s = 'Hello! This is the first request.'
        else:
            s = 'Hello! I have served %s requests.' % self.counter
        s += '\nDon\' forget about favicon requests.\n\n'
        return s


class Application(object):
        
    @inject.param('started_at', 'app_started_at')
    def __init__(self, environ, start_response, started_at=None):
        start_response('200 OK', [])
    
    def __iter__(self):
        yield self.hello()
        yield self.text1()
        yield self.text2()
        yield self.text3()
        yield self.text4()
    
    @inject.param('hello', Hello)
    def hello(self, hello):
        return str(hello)
    
    @inject.param('started_at', 'app_started_at')
    def text1(self, started_at):
        return 'The application started serving requests at %s.\n\n' \
               'This value is application scoped. In other words,\n' \
               'it has been created only once for the whole\n' \
               'application.\n\n' % started_at
    
    @inject.param('started_at', 'request_started_at')
    def text2(self, started_at):
        return 'The request started at %s.\n\n' % started_at
    
    def text3(self):
        return 'This value is request scoped. In other words,\n' \
               'it is created only once for each request.\n\n'
    
    @inject.param('started_at', 'request_started_at')
    @inject.param('ended_at', datetime, bindto=datetime.now)
    def text4(self, started_at, ended_at):
        return 'The request ended at %s,\n' \
               'but started at %s.\n' \
               'It took %s to serve the request.\n\n' \
               'There are two datetime object here, but the first\n' \
               'is not request scoped (ended_at), while the second\n' \
               '(started_at) is.' % (ended_at, started_at, 
                                     ended_at - started_at)


#==============================================================================
# Bindings which are injected in more than one function.
#==============================================================================
# We use an injector, so that we can configure application started_at and 
# request started_at only once (not everytime they are injected).
# All other instances are injected only once and are configured in place.
injector = inject.Injector()
injector.bind('app_started_at', to=datetime.now, scope=inject.appscope)
injector.bind('request_started_at', to=datetime.now, scope=inject.reqscope)

# Register an injector, so that it is used to get instances.
inject.register(injector)


#==============================================================================
# Wrap the application with the request scope middleware.
#==============================================================================
app = WsgiInjectMiddleware(Application)


#==============================================================================
# Start a server.
#==============================================================================
httpd = make_server('', 8000, app)
print 'Serving HTTP on port 8000...'
httpd.serve_forever()