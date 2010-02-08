'''Providers are callable objects which return instances. So all normal 
callables can be used as providers.

The module has only two providers: an instance provider, which is a callable
wrapper around any instance, and a factory. The factory creates and returns 
a specific provider, or an invoker depending on the passed arguments. It also
scopes it if a scope is given.
'''
from inject import errors
from inject.invoker_ import Invoker


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
        from inject.scopes import no as noscope, SCOPE_ATTR
        
        if scope is None and hasattr(bindto, SCOPE_ATTR):
            scope = bindto._inject_scope
        
        if callable(bindto):
            if hasattr(bindto, 'im_self') and bindto.im_self is None:
                # Unbound method.
                provider = cls.invoker_class(bindto)
            else:
                # Simple callable.
                provider = bindto
            
            # Create a scoped provider, if scope is given.
            if scope is not None and scope is not noscope:
                provider = scope.scope(provider)
        else:
            # Not a callable, create an instance provider.
            provider = cls.instance_class(bindto)
            # It's ok when scope is "noscope" or None,
            # otherwise raise an error.
            if scope is not None and scope is not noscope:
                raise errors.CantBeScopedError(bindto)
        
        return provider