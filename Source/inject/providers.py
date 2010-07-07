'''Providers are callable objects which return instances. So all normal 
callables can be used as providers.

The module has only two providers: an instance provider, which is a callable
wrapper around any instance, and a factory. The factory creates and returns 
a specific provider, or an invoker depending on the passed arguments. It also
scopes it if a scope is given.
'''
from inject.invokers import Invoker


class CantCreateProviderError(Exception):
    
    '''CantCreateProviderError is raised when to is not given and type is
    not callable.
    '''
    
    def __init__(self, type):
        msg = 'Can\'t create a provider for %r.' % type
        Exception.__init__(self, msg)


class InstanceProvider(object):
    
    '''InstanceProvider returns an instance when called.'''
    
    __slots__ = ('inst',)
    
    def __init__(self, type, to=None):
        self.inst = to
    
    def __call__(self):
        return self.inst


class ProvidersFactory(object):
    
    '''ProvidersFactory creates a specific provider depending on the type,
    and the binding.
    '''
    
    instance_class = InstanceProvider
    invoker_class = Invoker
    
    def __new__(cls, type, to=None):
        '''Create provider for a C{type}.
        
        If C{to} is None, and C{type} is a callable use C{type} as a provider,
        otherwise raise L{CantCreateProviderError}.
        
        If C{to} is an instance, return an L{InstanceProvider} provider.
        
        If C{to} is an unbound method, return an L{Invoker}.
        
        Otherwise, return C{to}.
        
        @raise CantCreateProviderError.
        '''
        to = cls._get_to(type, to=to)
        
        if callable(to):
            provider = cls._create_callable_provider(to)
        else:
            provider = cls._create_instance_provider(to)
        
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
    def _create_callable_provider(cls, to):
        if hasattr(to, 'im_self') and to.im_self is None:
            # Unbound method.
            return cls.invoker_class(to)
        
        return to
    
    @classmethod
    def _create_instance_provider(cls, to):
        return cls.instance_class(to)
