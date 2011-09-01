'''Request scope middleware for WSGI and Django applications. It registers
and unregisters a thread-local storage for each request.
'''
import inject.scopes


class WsgiInjectMiddleware(object):
    
    '''WSGI inject middleware registers a request scope for each request,
    and unregisters it after returning the response.
    
    @warning: WSGI inject middleware requires Python2.5+ because the later
        versions do not support yield inside a try...finally statement.
    
    '''
    
    scope = inject.class_attr(inject.scopes.RequestScope)
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        scope = self.scope
        try:
            scope.start()
            # We have to manually iterate over the response,
            # so that all its parts have been generated before
            # the request is unregistered.
            for s in iter(self.app(environ, start_response)):
                yield s
        finally:
            scope.end()


class DjangoInjectMiddleware(object):
    
    '''Django inject middleware registers a request scope for each request,
    and unregisters it for a response.
    
    It is recommended to put it before any other middleware. Otherwise, it is
    possible that you will use injection in another middleware when the request
    scope has been already unregistered.
    '''
    
    scope = inject.class_attr(inject.scopes.RequestScope)
    
    def process_request(self, request):
        '''Register a request scope for a request.'''
        from django.http import HttpRequest
        
        scope = self.scope
        scope.start()
        scope.bind(HttpRequest, request)
    
    def process_response(self, request, response):
        '''Unregister a request scope.'''
        self.scope.end()
        return response
