from inject import scopes


class WsgiInjectMiddleware(object):
    
    '''WSGI inject middleware registers a request scope for each request,
    and unregisters it after returning the response.
    
    @warning: WSGI inject middleware requires Python2.5+ because the later
        versions do not support yield inside a try...finally statement.
    
    '''
    
    def __init__(self, app, reqscope=scopes.req):
        self.app = app
        self.reqscope = reqscope
    
    def __call__(self, environ, start_response):
        try:
            self.reqscope.register(environ)
            # We have to manually iterate over the response,
            # so that all its parts have been generated before
            # the request is unregistered.
            for s in iter(self.app(environ, start_response)):
                yield s
        finally:
            self.reqscope.unregister(environ)


class DjangoInjectMiddleware(object):
    
    '''Django inject middleware registers a request scope for each request,
    and unregisters it for a response.
    
    It is recommended to put it before any other middleware. Otherwise, it is
    possible that you will use injection in another middleware when the request
    scope has been already unregistered. In this case NoRequestRegisteredError
    is raised.
    '''
    
    scope = scopes.req
    
    def process_request(self, request):
        '''Register a request scope for a request.'''
        self.scope.register(request.META)
    
    def process_response(self, request, response):
        '''Unregister a request scope.'''
        self.scope.unregister(request.META)
        return response