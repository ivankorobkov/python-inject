'''Scopes configure how objects are instantiated and reused.

By default, a new instance is injected every time. ApplicationScope scope creates
only one instance of a class (a provider) for the whole application. RequestScope 
scope creates unique instances for each HTTP request. RequestScope scope stores
values in a thread-local request-local manner.

C{noscope} can be used to explicitly specify creating new instances for every
injection request.
'''
import threading
from inject.exc import NoRequestStartedError
from inject.functional import update_wrapper


DEFAULT_SCOPE_ATTR = '__inject_default_scope__'


def get_default_scope(provider):
    '''Return the default scope class for a provider, or None.'''
    return getattr(provider, DEFAULT_SCOPE_ATTR, None)


def set_default_scope(provider, scope_class):
    '''Set the __inject_default_scope__ attribute of a provider.'''
    setattr(provider, DEFAULT_SCOPE_ATTR, scope_class)


def clear_default_scope(provider):
    '''Clear the provider default scope attribute if present.'''
    if hasattr(provider, DEFAULT_SCOPE_ATTR):
        delattr(provider, DEFAULT_SCOPE_ATTR)


class ScopeInterface(object):
    
    '''ScopeInterface.'''
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        pass


class AbstractScopeDecorator(object):
    
    '''AbstractScopeDecorator sets the default scope for a provider.'''
    
    scope_class = None
    set_default_scope = staticmethod(set_default_scope)
    
    def __new__(cls, provider):
        '''Decorate a provider and set its default scope,
        return the provider.
        '''
        cls.set_default_scope(provider, cls.scope_class)
        return provider


class NoScope(ScopeInterface):
    
    '''NoScope is a dummy scope which exists only to distinguish between
    None and NoScope.
    '''
    
    def scope(self, provider):
        return provider


class noscope(AbstractScopeDecorator):
    
    '''Decorator which sets the default scope to NoScope.'''
    
    scope_class = NoScope


class ApplicationScope(ScopeInterface):
    
    '''ApplicationScope scope caches instances for an application (a process).
    It can be called a singleton scope.
    '''
    
    def __init__(self):
        self.cache = {}
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        cache = self.cache
        def scopedprovider():
            if provider in cache:
                return cache[provider]
            
            inst = provider()
            cache[provider] = inst
            return inst
        
        return scopedprovider


class appscope(AbstractScopeDecorator):
    
    '''Decorator which sets the default scope to ApplicationScope.'''
    
    scope_class = ApplicationScope


class ThreadScope(threading.local, ScopeInterface):
    
    '''ThreadScope is a thread-local scope.'''
    
    def __init__(self):
        self.cache = {}

    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        def scopedprovider():
            cache = self.cache
            if provider in cache:
                return cache[provider]
            
            inst = provider()
            cache[provider] = inst
            return inst
        
        try:
            update_wrapper(scopedprovider, provider)
        except AttributeError:
            # The update_wrapper must have accessed a non-present
            # attribute. It can be possible when a provider is
            # a user-generated callable object. For example, it can be
            # an instance of a class with __slots__, which does not
            # have the __dict__ attribute.
            pass
        
        return scopedprovider


class threadscope(AbstractScopeDecorator):
    
    '''Decorator which sets the default scope to ThreadScope.'''
    
    scope_class = ThreadScope


class RequestScope(ThreadScope):
    
    '''RequestScope is a request-local thread-local scope which supports
    the context manager protocol (the with statement, 2.5+) or must
    be explicitly started/ended for every request.
    
    To use it start and end the requests, usually using the with statement,
    or try/finally.
    For example::
    
        @inject.param('scope', reqscope)
        def python25(environ, startresponse, scope):
            with scope:
                startresponse()
                return 'Response'
    
        @inject.param('scope', reqscope)
        def python24(environ, startresponse, scope):
            scope.start()
            try:
                startresponse()
                return 'Response'
            finally:
                scope.end()
    
    '''
    
    def __init__(self):
        self.cache = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        return False
    
    def start(self):
        '''Start a new request.'''
        self.cache = {}
    
    def end(self):
        '''End a request and clear the instances.'''
        del self.cache
    
    def _get_cache(self):
        cache = self._cache
        if cache is None:
            raise NoRequestStartedError()
        return cache
    
    def _set_cache(self, value):
        self._cache = value
    
    def _del_cache(self):
        del self._cache
    
    cache = property(_get_cache, _set_cache, _del_cache)


class reqscope(AbstractScopeDecorator):
    
    '''Decorator which sets the default scope to RequestScope.'''
    
    scope_class = RequestScope
