'''Providers are callable objects which return instances. So all normal 
callables can be used as providers.

The module has only two providers: an instance provider, which is a callable
wrapper around any instance, and a factory. The factory creates and returns 
a specific provider, or an invoker depending on the passed arguments. It also
scopes it if a scope is given.
'''
from inject.invokers import Invoker


class InstanceProvider(object):
    
    '''InstanceProvider returns an instance when called.'''
    
    __slots__ = ('inst',)
    
    def __init__(self, to=None):
        self.inst = to
    
    def __call__(self):
        return self.inst


class ProvidersFactory(object):
    
    '''ProvidersFactory creates a specific provider depending on the type,
    and the binding.
    '''
    
    instance_class = InstanceProvider
    invoker_class = Invoker
    
    def __new__(cls, to=None):
        '''Create provider for a C{type}.
        
        @raise CantCreateProviderError.
        '''
        if callable(to):
            provider = cls._create_callable_provider(to)
        else:
            provider = cls._create_instance_provider(to)
        
        return provider
    
    @classmethod
    def _create_callable_provider(cls, to):
        if hasattr(to, 'im_self') and to.im_self is None:
            # Unbound method.
            return cls.invoker_class(to)
        
        return to
    
    @classmethod
    def _create_instance_provider(cls, to):
        return cls.instance_class(to)
