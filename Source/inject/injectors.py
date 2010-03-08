'''Injector stores configuration for bindings. It is optional and should be
used only when advanced configuratio is required.

Tutorial
========

Create an injector, B{register it}, and add bindings to it.
    >>> injector = Injector()
    >>> register(injector)
    >>> injector.bind(cls, annotation='text', to=MyClass, scope=appscope)

'''
import warnings

from inject import errors, providers
from inject.key import Key
from inject.injection import Injection


def register(injector):
    '''Register an injector so that it is used by all injections
    to get instances.
    '''
    Injection.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If an injector is None, unregister any registered injector.
    '''
    if Injection.injector is injector or injector is None:
        Injection.injector = None


class IInjector(object):
    
    '''Injector interface.'''
    
    bindings = None
    
    def bind(self, type, annotation=None, to=None, scope=None):
        '''Specify a binding for a type and an optional annotation.'''
        pass
    
    def get_instance(self, type, annotation=None):
        '''Return an instance for a type and an optional annotation, using
        the injector bindings, or raise NoProviderError.
        
        If an annotation is given, first, try to get an instance for 
        Key(type, annotation), then for a type alone.
        
        This is a utility method, it must be possible to get providers
        directly from injector's bindings by keys.
        '''
        pass


class Injector(IInjector):
    
    '''Injector stores configuration for bindings.'''
    
    key_class = Key
    provider_class = providers.Factory
    
    def __init__(self):
        self.bindings = {}
    
    def bind(self, type, annotation=None, to=None, scope=None):
        '''Specify a binding for a type and an optional annotation.'''
        if annotation is not None:
            key = self.key_class(type, annotation)
        else:
            key = type
        
        if to is None:
            if callable(type):
                to = type
            else:
                raise errors.NoProviderError(key)
        
        provider = self.provider_class(to, scope=scope)
        
        if key in self.bindings:
            warnings.warn('Overriding an exising binding for %s.' % key)
        self.bindings[key] = provider
    
    def get_instance(self, type, annotation=None):
        '''Return an instance for a type and an optional annotation, using
        the injector bindings, or raise NoProviderError.
        
        If an annotation is given, first, try to get an instance for 
        Key(type, annotation), then for a type alone.
        '''
        bindings = self.bindings
        key = self.key_class(type, annotation)
        
        if key in bindings:
            return bindings[key]()
        
        if type in bindings:
            return bindings[type]()
        
        raise errors.NoProviderError(key)