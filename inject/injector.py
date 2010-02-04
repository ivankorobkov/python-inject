import warnings

from inject import errors, providers
from inject.injection import Injection


def register(injector):
    Injection.injector = injector


def unregister(injector):
    if Injection.injector is injector:
        Injection.injector = None


class IInjector(object):
    
    bindings = None
    
    def bind(self, type, annotation=None, scope=None, to=None,to_instance=None,
             to_provider=None):
        pass
    
    def get_instance(self, type, annotation):
        pass


class Injector(IInjector):
    
    provider_class = providers.Factory
    
    def __init__(self):
        self.bindings = {}
    
    def bind(self, type, annotation=None, to=None, scope=None):
        if annotation is not None:
            key = self.key_class(type, annotation)
        else:
            key = type
        
        provider = self.provider_class(to, scope=scope)
        
        if key in self.bindings:
            warnings.warn('Overriding an exising binding for key %s.'
                          % key)
        self.bindings[key] = provider
    
    def get_key(self, type, annotation):
        if annotation is not None:
            key = self.key_class(type, annotation)
        else:
            key = type
        return key
    
    def get_provider(self, key):
        bindings = self.bindings
        if key in bindings:
            provider = bindings[key]
        elif type in bindings:
            provider = bindings[type]
        else:
            provider = None
        
        return provider
    
    def get_instance(self, type, annotation=None):
        key = self.get_key(type, annotation)
        provider = self.get_provider(key)
        if provider is None:
            raise errors.NoProviderError(key)