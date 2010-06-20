'''Providers are callable objects which return instances. So all normal 
callables can be used as providers.

The module has only two providers: an instance provider, which is a callable
wrapper around any instance, and a factory. The factory creates and returns 
a specific provider, or an invoker depending on the passed arguments. It also
scopes it if a scope is given.
'''
from inject.invokers import Invoker
from inject.errors import CantBeScopedError, CantCreateProviderError


class Instance(object):
    
    '''Instance provider is constructed with an instance, and returns it
    when called.
    '''
    
    __slots__ = ('inst',)
    
    def __init__(self, inst):
        self.inst = inst
    
    def __call__(self):
        return self.inst


class Factory(object):
    
    '''Factory creates a specific provider depending on the passed object,
    and optionally scopes it.
    '''
    
    instance_class = Instance
    invoker_class = Invoker
    
    def __new__(cls, type, to=None, scope=None):
        '''Create provider for a C{type}, optionally scope it.
        
        If C{to} is None, and C{type} is callable use C{type} as a provider,
        otherwise raise L{CantCreateProviderError}.
        
        If C{to} is an instance, return an L{Instance} provider. It cannot
        be scoped, so if C{scope} is given raise L{CantBeScopedError}.
        
        If C{to} is an unbound method, return an L{Invoker}. It cannot
        be scoped, so if C{scope} is given raise L{CantBeScopedError}.
        
        Otherwise, return a [scoped] C{to}.
        
        @raise CantCreateProviderError.
        @raise CantBeScopedError.
        '''
        to = cls._get_to(type, to=to)
        scope = cls._get_scope(to, scope=scope)
        
        if callable(to):
            provider = cls._create_callable_provider(to, scope=scope)
        else:
            provider = cls._create_instance_provider(to, scope=scope)
        
        return provider
    
    @classmethod
    def _get_to(cls, type, to=None):
        if to is None:
            if callable(type):
                to = type
            else:
                raise CantCreateProviderError(type)
        
        return to
    
    @classmethod
    def _get_scope(cls, to, scope=None):
        from inject.scopes import SCOPE_ATTR
        
        if scope is None and hasattr(to, SCOPE_ATTR):
            scope = to._inject_scope
        
        return scope
    
    @classmethod
    def _create_callable_provider(cls, to, scope=None):
        from inject.scopes import no as noscope
        
        if hasattr(to, 'im_self') and to.im_self is None:
            # Unbound method.
            provider = cls.invoker_class(to)
            if scope is not None and scope is not noscope:
                raise CantBeScopedError(to)
        
        else:
            # Simple callable.
            provider = to
            
            # Create a scoped provider, if scope is given.
            if scope is not None and scope is not noscope:
                provider = scope.scope(provider)
        
        return provider
    
    @classmethod
    def _create_instance_provider(cls, to, scope=None):
        from inject.scopes import no as noscope
        
        # Not a callable, create an instance provider.
        provider = cls.instance_class(to)
        # It's ok when scope is "noscope" or None,
        # otherwise raise an error.
        if scope is not None and scope is not noscope:
            raise CantBeScopedError(to)
        
        return provider
