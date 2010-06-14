'''Injectors store bindings configuration. They allow to use advanced 
configuration, but are optional. It is possible to create multiple injectors,
one of which can be registered as the main injector. Other injectors can
be used directly to create specific injections (C{injector.attr(...)}, etc.)

If you want to use C{inject} in a project which will be used by other projects
(for example, a library, a framework, etc.) B{always create an explicit
injector}, and use its C{attr}, C{param}, and C{invoker} methods to create
injections.

Tutorial
========

Create an injector, and add bindings to it.

    >>> injector = Injector()
    >>> injector.bind(Class1, to=Class2, scope=appscope)

Or use callables which take the injector as an argument to configure it.

    >>> def config(inj):
    ...     inj.bind(A, to=A2)
    >>> class Config(object):
    ...     def __init__(self, inj):
    ...         inj.bind(B, to=B2)
    >>>
    >>> injector.configure(config, Config)

Then 1) B{register it as the main injector} which will be used by
the injections, 2) B{or create injector-specific injections}.

    >>> # Register the main injector.
    >>> class A(object): pass
    >>> class A2(object): pass
    >>> class B(object):
    ...     a = inject.attr('a', A)
    >>> injector.bind(A, to=A2)
    >>> register(injector)
    
    >>> # Or create injector-specific injections. 
    
    >>> class A(object): pass
    >>> class B(object):
    ...     a = injector.attr('a', A)
    >>> injector.bind(A, to=A2)

'''
import new
import warnings

from inject import errors, providers
from inject.invokers import Invoker
from inject.injection import Injection
from inject.injections import AttributeInjection, Param


def register(injector):
    '''Register an injector as the main injector.'''
    if Injection.injector is not None:
        warnings.warn('Overriding an already registered main injector %s '
                      'with %s.' % (Injection.injector, injector))
    Injection.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If None, unregister any registered injector.
    '''
    if Injection.injector is injector or injector is None:
        Injection.injector = None


class Injector(object):
    
    '''Injector stores configuration for bindings.'''
    
    provider_class = providers.Factory
    injection_class = None
    
    def __init__(self, attr_class=AttributeInjection, param_class=Param,
                 invoker_class=Invoker, injection_class=Injection):
        self.injection_class = new.classobj(attr_class.__name__,
            (injection_class,), {'injector': self})
        
        self.attr_class = new.classobj(attr_class.__name__, (attr_class,),
            {'injection_class': self.injection_class})
        
        self.param_class = new.classobj(attr_class.__name__, (param_class,),
            {'injection_class': self.injection_class})
        
        self.invoker_class = new.classobj(invoker_class.__name__,
            (invoker_class,), {'injection_class': self.injection_class})
        
        self.bindings = {}
    
    def bind(self, type, to=None, scope=None):
        '''Specify a binding for a type.'''
        if to is None:
            if callable(type):
                to = type
            else:
                raise errors.NoProviderError(type)
        
        provider = self.provider_class(to, scope=scope)
        
        if type in self.bindings:
            warnings.warn('Overriding an exising binding for %s.' % type)
        self.bindings[type] = provider
    
    def configure(self, *configs):
        '''Configure the injector using the provided callable configs;
        call them with the injector as an argument.
        '''
        for config in configs:
            config(self)
    
    def get_instance(self, type):
        '''Return an instance for a type, using the injector bindings, 
        or raise NoProviderError.
        '''
        bindings = self.bindings
        if type in bindings:
            return bindings[type]()
        
        raise errors.NoProviderError(type)
    
    #==========================================================================
    # Creating injector-specific injections
    #==========================================================================
    
    def attr(self, attr, type=None):
        '''Create an injector-specific attribute injection.'''
        return self.attr_class(attr=attr, type=type)
    
    def param(self, name, type=None):
        '''Create an injector-specific param injection.'''
        return self.param_class(name=name, type=type)
    
    def invoker(self, method):
        '''Create an injector-specific invoker.'''
        return self.invoker_class(method=method)
    
    #==========================================================================
    # Registering/unregistering
    #==========================================================================
    
    def register(self):
        '''Register the injector as the main injector.'''
        return register(self)
    
    def unregister(self):
        '''Unregister the injector if it is registered.'''
        return unregister(self)
