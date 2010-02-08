'''Injection serves injection requests, it provides the core functionality.'''
from inject import errors
from inject.key import Key


class Injection(object):
    
    '''Injection serves injection requests.
    
    Resolving flow:
        
        1. If an injector is registered, try to get an instance from it.
            - If an annotation exists, try to get an instance for Key(type, 
              annotation).
            - If no instance is returned, try to get an instance for type.
            - Return an instance, or continue.
        2. If the injection has a provider (either from a callable type,
           or from a bindto argument), use it to get an instance and return it.
        3. Otherwise, raise NoProviderError.
    
    '''
    
    __slots__ = ('key', 'type', 'provider')
    
    injector = None    
    key_class = Key
    provider_class = None  # Set below to prevent circular imports.
    
    def __init__(self, type, annotation=None, bindto=None, scope=None):
        self.key = self.key_class(type, annotation)
        self.type = type
        
        provider = None
        if bindto is not None:
            provider = self.provider_class(bindto, scope=scope)
        elif callable(type):
            provider = self.provider_class(type, scope)
        
        self.provider = provider
    
    def get_instance(self):
        '''Return an instance, or raise NoProviderError.'''
        key = self.key
        type = self.type
        injector = self.injector
        
        provider = None
        
        if injector:
            bindings = injector.bindings
            if key in bindings:
                provider = bindings[key]
            elif type in bindings:
                provider = bindings[type]
        
        if provider is None:
            provider = self.provider
            if provider is None:
                raise errors.NoProviderError(key)
        
        return provider()


from inject.providers import Factory
Injection.provider_class = Factory