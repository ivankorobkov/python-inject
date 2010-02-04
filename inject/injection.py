from inject import errors
from inject.key import Key


class Injection(object):
    
    __slots__ = ('key', 'type', 'provider')
    
    injector = None    
    key_class = Key
    provider_class = None
    
    def __init__(self, type, annotation=None, scope=None, bindto=None):
        self.key = self.key_class(type, annotation)
        self.type = type
        
        provider = None
        if bindto is not None:
            provider = self.provider_class(bindto, scope=scope)
        elif callable(type):
            provider = self.provider_class(type, scope)
        
        self.provider = provider
    
    def get_instance(self):
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


from inject import providers
Injection.provider_class = providers.Factory