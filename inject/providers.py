'''Providers instantiate objects.'''
from inject import errors, scopes
from inject.invoker import Invoker


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
    
    def __new__(cls, bindto, scope=None):
        '''Return a provider for a bindto object, optionally scope it.
        
        If C{bindto} is an instance, return an instance provider. It cannot
        be scoped, so if scope is given CantBeScopedError is raised.
        
        If C{bindto} is an unbound method, return a [scoped] invoker.
        
        Otherwise, return a [scoped] bindto.
        '''
        if scope is None and hasattr(bindto, scopes.SCOPE_ATTR):
            scope = bindto._inject_scope
        
        if callable(bindto):
            if hasattr(bindto, 'im_self') and bindto.im_self is None:
                # Unbound method.
                provider = cls.invoker_class(bindto)
            else:
                # Simple callable.
                provider = bindto
            
            # Create a scoped provider, if scope is given.
            if scope is not None and scope is not scopes.no:
                provider = scope.scope(provider)
        else:
            # Not a callable, create an instance provider.
            provider = cls.instance_class(bindto)
            if scope is not None:
                raise errors.CantBeScopedError(bindto)
        
        return provider