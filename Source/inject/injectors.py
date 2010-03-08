'''Injector stores configuration for bindings. It is optional and should be
used only when advanced configuratio is required.

Tutorial
========

Create an injector, and add bindings to it.
    >>> injector = Injector()
    >>> injector.bind(cls, annotation='text', to=MyClass, scope=appscope)

Then 1) B{register it} as the main injector which will be used by all 
injections, or 2) use it to create injector-specific injections.

    >>> class A(object): pass
    >>> class B(object):
    ...     a = inject.attr('a', A)
    >>> register(injector)
    
    >>> # or
    >>> class A(object): pass
    >>> class B(object):
    ...     a = injector.attr('a', A)
    >>>

'''
import new
import warnings

from inject import errors, providers
from inject.key import Key
from inject.invokers import Invoker
from inject.injection import Injection
from inject.injections import Attr, Param


def register(injector):
    '''Register an injector as a main injector.'''
    Injection.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If an injector is None, unregister any registered injector.
    '''
    if Injection.injector is injector or injector is None:
        Injection.injector = None


class Injector(object):
    
    '''Injector stores configuration for bindings.
    
    @ivar attr_class: Attribute injection which uses this injector.
    @ivar param_class: Param injection which uses this injector.
    @ivar invoker_class: Invoker which uses this injector.
    '''
    
    key_class = Key
    provider_class = providers.Factory
    injection_class = None
    
    attr = None
    param = None
    invoker = None
    
    def __init__(self, attr_class=Attr, param_class=Param,
                 invoker_class=Invoker, injection_class=Injection):
        self.injection_class = new.classobj(attr_class.__name__, 
            (injection_class,), {'injector': self})
        
        self.attr_class = new.classobj(attr_class.__name__, (attr_class,),
            {'injection_class': self.injection_class})
        
        self.param_class = new.classobj(attr_class.__name__, (param_class,),
            {'injection_class': self.injection_class})
        
        self.invoker_class = new.classobj(invoker_class.__name__,
            (invoker_class,),   {'injection_class': self.injection_class})
        
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
    
    def attr(self, attr, type=None, annotation=None, bindto=None, scope=None):
        '''Create an injector-specific attribute injection.'''
        return self.attr_class(attr=attr, type=type, annotation=annotation, 
                               bindto=bindto, scope=scope)
    
    def param(self, name, type=None, annotation=None, bindto=None, scope=None):
        '''Create an injector-specific param injection.'''
        return self.param_class(name=name, type=type, annotation=annotation, 
                                bindto=bindto, scope=scope)
    
    def invoker(self, method, scope=None):
        '''Create an injector-specific invoker.'''
        return self.invoker_class(method=method, scope=scope)