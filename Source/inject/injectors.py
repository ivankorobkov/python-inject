'''Injectors store providers configurvation. They allow to use advanced 
configuration, but are optional. It is possible to create multiple injectors,
one of which can be registered as the main injector. Other injectors can
be used directly to create specific injections (C{injector.attr(...)}, etc.)

If you want to use C{inject} in a project which will be used by other projects
(for example, a library, a framework, etc.) B{always create an explicit
injector}, and use its C{attr}, C{param}, and C{invoker} methods to create
injections.

Tutorial
========

Create an injector, and add providers to it.

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
import warnings

from inject import providers
from inject.points import InjectionPoint
from inject.scopes import get_default_scope


class NoInjectorRegistered(Exception):
    
    '''NoInjectorRegistered is raised when there is no injector registered,
    and the injections try to use it.
    '''


class NoProviderError(Exception):
    
    '''NoProviderError is raised when there is no provider bound to a key.'''
    
    def __init__(self, key):
        msg = 'There is no provider for %s.' % str(key)
        Exception.__init__(self, msg)


class CantCreateProviderError(Exception):
    
    '''CantCreateProviderError is raised when to is not given and type is
    not callable.
    '''


class ScopeNotBoundError(Exception):
    
    '''ScopeNotBound is raised when a scope is used, but it is not bound
    in the injector.
    '''
    
    def __init__(self, scope_class):
        msg = 'The scope %r is not bound in the injector.' % scope_class
        Exception.__init__(self, msg)


class Injector(object):
    
    '''Injector stores configuration for providers.
    
    @ivar providers: Types to providers mapping.
    @ivar bound_scopes: Scopes to bound scopes mapping.
    '''
    
    provider_class = providers.ProvidersFactory
    
    def __init__(self, create_default_providers=True):
        self.providers = {}
        self.bound_scopes = {}
        
        self.create_default_providers = create_default_providers
    
    def configure(self, *configs):
        '''Configure the injector using the provided callable configs;
        call them with the injector as an argument.
        '''
        for config in configs:
            config(self)
    
    def bind(self, type, to=None, scope=None):
        '''Specify a binding for a type.
        
        @raise CantCreateProviderError.
        '''
        provider = self._create_provider(type, to=to, scope=scope)
        self._add_provider(type, provider)
    
    def bind_scope(self, scope, to):
        '''Bind a scope key to an instance.'''
        self.bound_scopes[scope] = to
    
    def get_provider(self, type):
        '''Return a provider, or raise NoProviderError.
        
        If create_default_providers flag is True, and no binding exist for 
        a type, and the type is callable, return it.
        
        @raise NoProviderError.
        @raise CantCreateProviderError.
        '''
        bindings = self.providers
        
        if type not in bindings:
            if self.create_default_providers:
                provider = self._create_default_provider(type)
                self._add_provider(type, provider)
            else:
                raise NoProviderError(type)
        
        return bindings[type]
    
    def get_instance(self, type):
        '''Return an instance for a type using the injector providers.
        
        @raise NoProviderError.
        @raise CantCreateProviderError.
        '''
        return self.get_provider(type)()
    
    #==========================================================================
    # Private methods
    #==========================================================================
    
    def _add_provider(self, type, provider):
        '''Add a provider for a type.'''
        if type in self.providers:
            warnings.warn('Overriding an existing binding for %s.' % type)
        self.providers[type] = provider
    
    def _create_provider(self, type, to=None, scope=None):
        '''Create a new provider for a type and return it.
        If to is None, and type is callable, use it as a provider.
        
        @raise CantCreateProviderError.
        '''
        if to is None:
            if callable(type):
                to = type
            else:
                raise CantCreateProviderError('To is not give and type %r is '
                                              'not callable.' % type)
        
        provider = self.provider_class(to=to)
        return self._scope_provider(provider, scope=scope)
    
    def _create_default_provider(self, type):
        '''Create a default provider for a type.'''
        return self._create_provider(type, to=None, scope=None)
    
    def _scope_provider(self, provider, scope=None):
        '''Get a scope for a provider, and if it is not None use it to scope
        the provider, return the provider.
        '''
        if scope is None:
            scope = self._get_default_scope(provider)
        
        if scope is not None:
            bound_scope = self._get_bound_scope(scope)
            provider = bound_scope.scope(provider)
        
        return provider
    
    def _get_bound_scope(self, scope=None):
        '''Return a bound scope or raise ScopeNotBoundError.
        
        @raise ScopeNotBoundError.
        '''
        try:
            return self.bound_scopes[scope]
        except KeyError:
            raise ScopeNotBoundError(scope)
    
    _get_default_scope = staticmethod(get_default_scope)
    
    #==========================================================================
    # Registering/unregistering
    #==========================================================================
    
    def register(self):
        '''Register the injector as the main injector.'''
        return register(self)
    
    def unregister(self):
        '''Unregister the injector if it is registered.'''
        return unregister(self)
    
    def is_registered(self):
        '''Return whether the injector is registered.'''
        return is_registered(self)


def register(injector):
    '''Register an injector as the main injector.'''
    if InjectionPoint.injector is not None:
        warnings.warn('Overriding an already registered main injector %s '
                      'with %s.' % (InjectionPoint.injector, injector))
    InjectionPoint.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If None, unregister any registered injector.
    '''
    if InjectionPoint.injector is injector or injector is None:
        InjectionPoint.injector = None


def is_registered(injector):
    '''Return whether an injector is registered.'''
    return InjectionPoint.injector is injector


def get_instance(type):
    '''Return an instance from the registered injector.
    
    @raise NoInjectorRegistered.
    '''
    injector = InjectionPoint.injector
    if injector is None:
        raise NoInjectorRegistered()
    
    return injector.get_instance(type)
