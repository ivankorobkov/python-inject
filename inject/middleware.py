from inject import scopes


class WsgiInjectMiddleware(object):
    
    '''WSGI inject middleware registers a request scope for each request,
    and unregisters it after returning the response.
    '''
    
    def __init__(self, app, scope=scopes.req):
        self.app = app
        self.scope = scope
    
    def __call__(self, environ, start_response):
        try:
            self.scope.register(environ)
            return iter(self.app(environ, start_response))
        finally:
            self.scope.unregister(environ)


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
        return request
    
    def process_response(self, request, response):
        '''Unregister a request scope.'''
        self.scope.unregister(request.META)
        return response