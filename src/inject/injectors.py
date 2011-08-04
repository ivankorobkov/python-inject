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

from inject.config import default_configuration
from inject.exc import NotBoundError, CantCreateProviderError, \
    ScopeNotBoundError, CantGetInstanceError, InjectorAlreadyRegistered
from inject.imports import LazyImport
from inject.injections import InjectionPoint, NoInjectorRegistered
from inject.log import configure_stdout_handler, logger
from inject.providers import ProviderFactory


class Injector(object):
    
    '''Injector stores configuration for providers.
    
    @ivar echo: If set to True creates a default logger, adds an stdout
        handler, and sets the level to DEBUG. The flag affects only this
        injector logging.
    
    @ivar _bindings: Types to providers mapping.    
    '''
    
    provider_class = ProviderFactory
    
    def __init__(self, create_default_providers=True, default_config=True,
                 echo=False):
        
        self._logger_name = None
        self._echo = None
        
        self._bindings = {}
        
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
        
        self._default_config = default_config
        if self._default_config:
            default_configuration(self)
    
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
    
    def clear(self, default_config=None):
        '''Remove all bindings.
        
        @param default_config: A flag which indicates whether to set
            the default config after clearing the injector bindings.
            When set to None the injector._default_config flag is used.
        '''
        self._bindings.clear()
        
        if self._debug:
            self._logger.debug('Cleared all bindings.')
        
        if default_config is None:
            default_config = self._default_config
        
        if default_config:
            default_configuration(self)
    
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
        self.bind(type, to=lambda: None)
    
    def bind_to_instance(self, type, inst):
        '''Bind type to an instance.
        
        The method exists because all callables are considered to be providers,
        and some instances can be callable. It wraps an instance with
        a lambda.
        '''
        self.bind(type, to=lambda: inst)
    
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
        '''Return a provider, or raise an error.
        
        If create_default_providers flag is True, and no binding exists for 
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
        @raise CantGetInstanceError.
        @raise CantCreateProviderError.
        '''
        provider = self.get_provider(type)
        try:
            instance = provider()
        except (SystemExit, KeyboardInterrupt), e:
            raise e
        except Exception, e:
            s = 'Failed to get an instance for %r from %r. ' \
                'The exception was: %s: %s. ' \
                'Set injector.echo=True to see the traceback.' % \
                (type, provider, str(e.__class__.__name__), e)
            self._logger.exception(s)
            raise CantGetInstanceError(s)
        
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
        if scope is not None:
            bound_scope = self._get_bound_scope(scope)
            provider = bound_scope.scope(provider)
            
            if self._debug:
                self._logger.debug('Scoped provider %r using scope %r.',
                                  provider, scope)
        
        return provider
    
    def _get_bound_scope(self, scope=None):
        '''Return a bound scope or raise ScopeNotBoundError.
        
        A scope cannot be bound using a default provider.
        
        @raise ScopeNotBoundError.
        '''
        if not self.is_bound(scope):
            raise ScopeNotBoundError(scope)
        
        return self.get_instance(scope)
    
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
    '''Register an injector as the main injector.
    
    @raise InjectorAlreadyRegistered: if another injector is already registered.
    '''
    if InjectionPoint.injector is not None:
        raise InjectorAlreadyRegistered()
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
