'''Providers are callable objects which return instances. Any python callable
can be used as a provider.

The module has only two providers: an instance provider, which is a callable
wrapper around any object, and a factory. The factory returns a callable,
an instance provider, or an invoker.
'''
from inject.invokers import Invoker


class InstanceProvider(object):
    
    '''InstanceProvider returns an instance when called.'''
    
    __slots__ = ('_instance', '_hash')
    
    def __init__(self, instance=None):
        self._instance = instance
        self._hash = None
    
    def __call__(self):
        return self._instance
    
    def __hash__(self):
        _hash = self._hash
        if _hash is None:
            _hash = hash(self._instance)
            self._hash = _hash
        
        return _hash
    
    def __eq__(self, other):
        return self._instance == other
    
    def __ne__(self, other):
        return self._instance != other


class ProviderFactory(object):
    
    '''ProviderFactory creates a specific provider.
    
    If C{to} is callable, return it.
    If C{to} is an unbound method, return an invoker for it.
    If C{to} is not callable, return an instance provider.
    '''
    
    instance_class = InstanceProvider
    invoker_class = Invoker
    
    def __new__(cls, to=None):
        '''Create provider for C{to}.'''
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
