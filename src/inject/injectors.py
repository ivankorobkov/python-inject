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
import logging

from inject.config import default_config
from inject.injections import InjectionPoint, NoInjectorRegistered
from inject.log import configure_stdout_handler, logger
from inject.providers import ProviderFactory
from inject.scopes import get_default_scope, appscope
from inject.imports import LazyImport


class NotBoundError(KeyError):
    
    '''NotBoundError extends KeyError, is raised when there is no bound
    provider.
    '''
    
    def __init__(self, key):
        msg = 'No bound provider for %s, use injector.bind to bind it.' \
            % str(key)
        KeyError.__init__(self, msg)


class CantCreateProviderError(Exception):
    
    '''CantCreateProviderError is raised when to is not given and type is
    not callable.
    '''


class ScopeNotBoundError(KeyError):
    
    '''ScopeNotBound extends KeyError, is raised when a scope is used,
    but it is not bound in the injector.
    '''
    
    def __init__(self, scope_class):
        msg = 'Scope %r is not bound, use injector.bind_scope to bind it.' \
            % scope_class
        KeyError.__init__(self, msg)


@appscope
class Injector(object):
    
    '''Injector stores configuration for providers.
    
    @ivar _bindings: Types to providers mapping.
    @ivar _bound_scopes: Scopes to bound scopes mapping.
    @ivar echo: If set to True creates a default logger, adds an stdout
        handler, and sets the level to DEBUG. The flag affects only this
        injector instance logging.
    '''
    
    provider_class = ProviderFactory
    
    def __init__(self, create_default_providers=True,
                 default_config=default_config,
                 echo=False):
        
        self._logger_name = None
        self._echo = None
        
        self._bindings = {}
        self._bound_scopes = {}
        
        self._logger = logging.getLogger(self.logger_name)
        
        # The initial logger level configuration.
        # It is also used when setting echo back to False.
        self._logger_debug_enabled = self._logger.isEnabledFor(logging.DEBUG)
        if self._logger_debug_enabled:
            self._debug = True
        else:
            self._debug = False
        
        # Set echo after getting a logger,
        # because it can change logger's level.
        self.echo = echo
        
        self.create_default_providers = create_default_providers
        if default_config:
            default_config(self)
    
    def _get_logger_name(self):
        if self._logger_name is None:
            self._logger_name = 'inject.%s.%s' % (self.__class__.__name__,
                                                  hex(id(self))[-6:])
        return self._logger_name
    
    def _set_logger_name(self, logger_name):
        self._logger_name = logger_name
    
    def _get_echo(self):
        return self._echo
    
    def _set_echo(self, value):
        if value:
            configure_stdout_handler(self.logger_name)
            self._debug = True
        else:
            self._debug = self._logger_debug_enabled
    
    logger_name = property(_get_logger_name, _set_logger_name)
    echo = property(_get_echo, _set_echo)
    
    def clear(self):
        '''Remove all bindings.'''
        self._bindings.clear()
        
        if self._debug:
            self._logger.debug('Cleared all bindings.')
    
    def bind(self, type, to=None, scope=None):
        '''Specify a binding for a type.
        
        @raise CantCreateProviderError.
        '''
        provider = self._create_provider(type, to=to, scope=scope)
        self._add_provider(type, provider)
        
        if self._debug:
            self._logger.debug('Bound %r to %r, scope %r.', type, to, scope)
    
    def bind_to_none(self, type):
        '''Bind type to None.
        
        The method exists because it is not possible to pass to=None.
        It binds type to a function, which returns None.
        '''
        def none():
            return None
        
        self.bind(type, to=none)
    
    def bind_scope(self, scope, to):
        '''Bind a scope key to an instance.'''
        self._bound_scopes[scope] = to
    
    def is_bound(self, type):
        '''Return True if type is bound, else return False.'''
        return type in self._bindings
    
    def unbind(self, type):
        '''unbind type, if it is bound, else raise NotBoundError.
        
        @raise NotBoundError.
        '''
        try:
            del self._bindings[type]
        except KeyError:
            raise NotBoundError(type)
        
        if self._debug:
            self._logger.debug('Unbound %r.', type)
    
    def get_provider(self, type):
        '''Return a provider, or raise NotBoundError.
        
        If create_default_providers flag is True, and no binding exist for 
        a type, and the type is callable, return it.
        
        @raise NotBoundError.
        @raise CantCreateProviderError.
        '''
        bindings = self._bindings
        
        if type not in bindings:
            if self.create_default_providers:
                provider = self._create_default_provider(type)
                self._add_provider(type, provider)
            else:
                raise NotBoundError(type)
        
        return bindings[type]
    
    def get_instance(self, type):
        '''Return an instance for a type.
        
        @raise NotBoundError.
        @raise CantCreateProviderError.
        '''
        instance = self.get_provider(type)()
        if self._debug:
            self._logger.debug('Got instance %r for %r.' % (instance, type))
        
        return instance
    
    #==========================================================================
    # Private methods
    #==========================================================================
    
    def _add_provider(self, type, provider):
        '''Add a provider for a type.'''
        if type in self._bindings and self._debug:
            self._logger.warn('Overriding an existing binding for %r with %r.',
                              type, provider)
        
        self._bindings[type] = provider
    
    def _create_provider(self, type, to=None, scope=None):
        '''Create a new provider for a type and return it.
        If to is None, and type is callable, use it as a provider.
        
        @raise CantCreateProviderError.
        '''
        if to is None:
            if isinstance(type, LazyImport):
                type = type.obj
            
            if callable(type):
                to = type
            else:
                raise CantCreateProviderError('To is not given and type %r is '
                                              'not callable.' % type)
        
        provider = self.provider_class(to=to)
        return self._scope_provider(provider, scope=scope)
    
    def _create_default_provider(self, type):
        '''Create a default provider for a type.'''
        provider = self._create_provider(type, to=None, scope=None)
        if self._debug:
            self._logger.debug('Created a default provider for %r.', type)
        
        return provider
    
    def _scope_provider(self, provider, scope=None):
        '''Get a scope for a provider, and if it is not None use it to scope
        the provider, return the provider.
        '''
        if scope is None:
            scope = self._get_default_scope(provider)
        
        if scope is not None:
            bound_scope = self._get_bound_scope(scope)
            provider = bound_scope.scope(provider)
            
            if self._debug:
                self._logger.debug('Scoped provider %r using scope %r.',
                                  provider, scope)
        
        return provider
    
    def _get_bound_scope(self, scope=None):
        '''Return a bound scope or raise ScopeNotBoundError.
        
        @raise ScopeNotBoundError.
        '''
        try:
            return self._bound_scopes[scope]
        except KeyError:
            raise ScopeNotBoundError(scope)
    
    _get_default_scope = staticmethod(get_default_scope)
    
    #==========================================================================
    # Registering/unregistering
    #==========================================================================
    
    def register(self):
        '''Register the injector as the main injector.'''
        register(self)
        if self._debug:
            self._logger.debug('Registered %r as the main injector.', self)
    
    def unregister(self):
        '''Unregister the injector if it is registered.'''
        unregister(self)
        if self._debug:
            self._logger.debug('Unregistered injector %r.', self)
    
    def is_registered(self):
        '''Return whether the injector is registered.'''
        return is_registered(self)


def register(injector):
    '''Register an injector as the main injector.'''
    if InjectionPoint.injector is not None:
        logger.warn('Overriding the already registered injector %r '
                    'with %r.', InjectionPoint.injector, injector)
    else:
        logger.debug('Registering injector %r.', injector)
    InjectionPoint.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If None, unregister any registered injector.
    '''
    def _unregister():
        injector = InjectionPoint.injector
        InjectionPoint.injector = None
        logger.debug('Unregistered injector %r.', injector)
    
    existing_injector = InjectionPoint.injector
    
    if existing_injector is injector and existing_injector is not None:
        _unregister()
    else:
        if injector is None:
            if existing_injector is None:
                logger.warn('Nothing to unregister, '
                            'no injector is registered.')
            else:
                _unregister()
        else:
            logger.warn('Can\'t unregister injector %r, because it is '
                        'not registered.', injector)

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
