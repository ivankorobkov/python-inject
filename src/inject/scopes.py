'''Scope is a specific container/context for bindings (any objects) and their
factories. L{Injector} accesses a stack of scopes when getting a specific binding.

    - L{AbstractScope} implements all bindings and factroies methods.
    - L{ApplicationScope} stores bindings (singletons) for the whole application.
    - L{NoScope} stores bindings (singletons) for the whole application,
        but does not store autobound objects and objects created by factories.
    - L{ThreadScope} stores unique bindings for each thread.
    - L{RequestScope} stores unique bindings for each thread/request.

ApplicationScope vs NoScope
---------------------------

ApplicationScope stores bindings which are created by factories,
so that they are created only once. NoScope uses factories
to create a new object every time a binding is accessed.

'''
import logging
import threading
from inject.exc import NoRequestError, FactoryNotCallable
import collections


class AbstractScope(object):
    
    '''Abstract scope implements all bindings and factories methods.
    
    Subclassing:
        - Pass the C{bindings} param to the super constructor, the param
          can be any object which supports the base dict interface
          (see L{ThreadLocalBindings} for example).
        - Set the C{logger} class attribute to a specific logger instance.
    
    '''
    
    logger = None
    
    def __init__(self, bindings):
        self._bindings = bindings
        self._factories = {}
    
    def __contains__(self, type):
        return self.is_bound(type)
    
    def bind(self, type, to):
        '''Create a binding for a type, override an existing binding if present.
        '''
        if self.is_bound(type):
            self.logger.info('Overriding an existing binding for %r.', type)
            self.unbind(type)
        
        self._bindings[type] = to
        self.logger.info('Bound %r to %r.', type, to)
    
    def unbind(self, type):
        '''Unbind a binding for a type if it is preset, else do nothing.'''
        if type in self._bindings:
            del self._bindings[type]
            self.logger.info('Unbound %r.', type)
    
    def is_bound(self, type):
        '''Return true if there is a binding for a type.
        
        If there is a factory for the given type but it has not been
        instantiated than return false.
        '''
        return type in self._bindings
    
    def bind_factory(self, type, factory):
        '''Bind a factory for a type, which will be used to create an instance
        when a *not present* binding is accessed.
        
        The factory is bound for the whole scope, i.e. TheadScope
        and RequestScope can have multiple bindings for each thread/request,
        but only one factory for a type. However, the factory is instantiated
        for each thread/request.
        '''
        if not isinstance(factory, collections.Callable):
            raise FactoryNotCallable(factory)
        
        if self.is_factory_bound(type):
            self.logger.info('Overriding an existing factory for %r.', type)
            self.unbind_factory(type)
        
        self._factories[type] = factory
        self.logger.info('Bound factory for %r to %r.', type, factory)
    
    def unbind_factory(self, type):
        '''Unbind a factory for a type if it is present, else do nothing.'''
        if type in self._factories:
            del self._factories[type]
            self.logger.info('Unbound factory for %r.', type)
    
    def is_factory_bound(self, type):
        '''Return true if there is a bound factory for a given type.'''
        return type in self._factories
    
    def get(self, type):
        '''Return a bound object for a given type, or instantiate and bind
        it using a factory if it is present, or return None.
        '''
        if type in self._bindings:
            return self._bindings.get(type)
        
        elif type in self._factories:
            factory = self._factories[type]
            inst = factory()
            self.bind(type, inst)
            return inst


class NoScope(AbstractScope):
    
    '''NoScope stores bindings (singletons) for the whole application
    as ApplicationScope, but NoScope does not store autobound objects
    and objects which are created by factories.
    '''
    
    logger = logging.getLogger('inject.NoScope')
    
    def __init__(self):
        super(NoScope, self).__init__({})
    
    def get(self, type):
        '''Return a bound object for a given type, or instantiate
        but *do not bind* it using a factory if it is present,
        or return None.
        '''
        if type in self._bindings:
            return self._bindings.get(type)
        
        elif type in self._factories:
            factory = self._factories[type]
            return factory()


class ApplicationScope(AbstractScope):
    
    '''ApplicationScope stores bindings (singletons) for the whole
    application (a process).
    '''
    
    logger = logging.getLogger('inject.ApplicationScope')
    
    def __init__(self):
        super(ApplicationScope, self).__init__({})


class ThreadLocalBindings(threading.local):
    
    '''ThreadLocalBindings class implements the base dict interface
    and stores unique bindings for each thread.
    '''
    
    def __init__(self):
        self._data = {}
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key):
        return self._data.get(key)
    
    def __len__(self):
        return len(self._data)
    
    def clear(self):
        self._data = {}


class ThreadScope(AbstractScope):
    
    '''ThreadScope stores unique bindings for each thread, but shares factories
    between threads.
    '''
    
    logger = logging.getLogger('inject.ThreadScope')
    
    def __init__(self):
        super(ThreadScope, self).__init__(ThreadLocalBindings())


class RequestLocalBindings(ThreadLocalBindings):
    
    '''RequestLocalBindings class subclasses L{ThreadLocalBindings} and can
    track whether a request has been started or not.
    ''' 
    
    def __init__(self):
        super(RequestLocalBindings, self).__init__()
        self.request_started = False
    
    def start_request(self):
        self.request_started = True
    
    def end_request(self):
        self.clear()
        self.request_started = False


class RequestScope(ThreadScope):
    
    '''RequestScope is a request-local thread-local scope which stores unique
    bindings for each thread/request but shares the factories between
    threads/requests.
    
    It must be explicitly started/ended for every request.
    
    It supports the context manager protocol (the with statement, Python 2.5+).
    
    The L{bind}, L{unbind} and L{get} methods raise L{NoRequestError} if
    there is no request, i.e. the scope L{start} method has not been called.
    
    To use the scope start and end requests, usually using the C{with}
    statement, or C{try/finally}.
    
    WSGI example::
    
        @inject.param('scope', inject.reqscope)
        def python25(environ, startresponse, scope):
            with scope:
                startresponse()
                return 'Response'
        
        @inject.param('scope', inject.reqscope)
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
        # Calling super for ThreadScope because we need to call AbstractScope
        # constructor here.
        super(ThreadScope, self).__init__(RequestLocalBindings())
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        return False
    
    def start(self):
        '''Start a new request.'''
        self._bindings.start_request()
    
    def end(self):
        '''End the request and clear the bindings.'''
        self._bindings.end_request()
    
    def bind(self, type, to):
        '''Create a binding for a type, override an existing binding if present.
        
        @raise NoRequestError: if no request.
        '''
        self._request_required()
        return super(RequestScope, self).bind(type, to)
    
    def unbind(self, type):
        '''Unbind a binding for a type if it is preset, else do nothing.
        
        @raise NoRequestError: if no request.
        '''
        self._request_required()
        return super(RequestScope, self).unbind(type)

    def get(self, type):
        '''Return a bound object for a given type, or instantiate and bind
        it using a factory if it is present, or return None.
        
        @raise NoRequestError: if no request.
        '''
        self._request_required()
        return super(RequestScope, self).get(type)
    
    def _request_required(self):
        '''Check whether a request has been started or raise an error.
        
        @raise NoRequestError: if a request has not been started.
        '''
        if not self._bindings.request_started:
            raise NoRequestError()


'''
@var appscope: ApplicationScope alias.
@var noscope: NoScope alias.
@var threadscope: ThreadScope alias.
@var reqscope: RequestScope alias.
'''
appscope = ApplicationScope
noscope = NoScope
threadscope = ThreadScope
reqscope = RequestScope
