'''Scopes configure how objects are reused.

ApplicationScope has bindings for the whole application.
ThreadScope stores instances for each thread.
RequestScope stores 
'''
import logging
import threading
from inject.exc import NoRequestError


class AbstractScope(object):
    
    logger = None
    
    def __init__(self):
        self._bindings = {}
    
    def __contains__(self, type):
        return type in self._bindings
    
    def bind(self, type, to):
        if type in self._bindings:
            self.logger.info('Overriding an existing binding: ',
                'type=%r, binding=%r.', type, self._bindings[type])
        
        self._bindings[type] = to
        self.logger.info('Bound %r to %r.', type, to)
    
    def unbind(self, type):
        if type in self._bindings:
            del self._bindings[type]
        
        self.logger.info('Unbound %r.', type)
    
    def is_bound(self, type):
        return type in self._bindings
    
    def get(self, type):
        return self._bindings.get(type)


class ApplicationScope(AbstractScope):
    
    '''ApplicationScope scope caches instances for an application (a process).
    It can be called a singleton scope.
    '''
    
    logger = logging.getLogger('inject.ApplicationScope')


class ThreadScope(threading.local, ApplicationScope):
    
    '''ThreadScope is a thread-local scope.'''
    
    logger = logging.getLogger('inject.ThreadScope')


class RequestScope(ThreadScope):
    
    '''RequestScope is a request-local thread-local scope which supports
    the context manager protocol (the with statement, 2.5+) or must
    be explicitly started/ended for every request.
    
    To use it start and end the requests, usually using the with statement,
    or try/finally.
    WSGI example::
    
        @inject.param('scope', RequestScope)
        def python25(environ, startresponse, scope):
            with scope:
                startresponse()
                return 'Response'
        
        @inject.param('scope', RequestScope)
        def python24(environ, startresponse, scope):
            scope.start()
            try:
                startresponse()
                return 'Response'
            finally:
                scope.end()
    
    '''
    
    logger = logging.getLogger('inject.RequestScope')
    
    def __init__(self):
        self._bindings = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        return False
    
    def start(self):
        '''Start a new request.'''
        self._bindings = {}
    
    def end(self):
        '''End the request and clear the bindings.'''
        self._bindings = None
    
    def bind(self, type, to):
        self._request_required()
        return super(RequestScope, self).bind(type, to)
    
    def unbind(self, type):
        self._request_required()
        return super(RequestScope, self).unbind(type)
    
    def is_bound(self, type):
        self._request_required()
        return super(RequestScope, self).is_bound(type)
    
    def get(self, type):
        self._request_required()
        return super(RequestScope, self).get(type)
    
    def _request_required(self):
        if self._bindings is None:
            raise NoRequestError()
