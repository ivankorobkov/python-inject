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
    
    '''noscope decorator.'''
    
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
    
    '''appscope decorator.'''
    
    scope_class = ApplicationScope


class RequestScope(threading.local, ScopeInterface):
    
    '''RequestScope is a request-local thread-local scope which caches
    instances for each request.
    
    To use it start and end the requests, usually using try/finally.
    For example::
    
        def myapp(environ, startresponse):
            reqscope.start()
            try:
                startresponse()
                return 'Response'
            finally:
                reqscope.end()
    
    '''
    
    cache = None
    
    def start(self):
        '''Start a new request.'''
        self.cache = {}
    
    def end(self):
        '''End a request and clear the instances.'''
        del self.cache
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        def scopedprovider():
            cache = self.cache
            if cache is None:
                raise NoRequestStartedError()
            
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


class reqscope(AbstractScopeDecorator):
    
    '''reqscope decorator.'''
    
    scope_class = RequestScope
