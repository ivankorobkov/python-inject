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

from inject.exc import InjectorAlreadyRegistered, NoInjectorRegistered, \
    NotBoundError, FactoryNotBoundError
from inject.log import configure_stdout_handler
from inject.scopes import ApplicationScope, ThreadScope, RequestScope


class Injector(object):
    
    '''Injector stores configuration for providers.
    
    @ivar echo: If set to True creates a default logger, adds an stdout
        handler, and sets the level to DEBUG. The flag affects only this
        injector logging.
    
    @ivar _bindings: Types to providers mapping.    
    '''
    
    logger = logging.getLogger('inject.Injector')
    injector = None
    
    @classmethod
    def create(cls, autobind=True, default_config=True, echo=False):
        '''Instantiate a new injector, register it, and return it.'''
        injector = cls(autobind=autobind, default_config=default_config,
                       echo=echo)
        injector.register()
        return injector
    
    @classmethod
    def cls_get_injector(cls):
        '''Return a registered injector or raise an exception.
        
        @raise NoInjectorRegistered: if no injector is registered.
        '''
        injector = cls.injector
        if injector is None:
            raise NoInjectorRegistered()
        
        return injector
    
    @classmethod
    def cls_register(cls, injector):
        another = cls.injector
        if another is not None:
            raise InjectorAlreadyRegistered(another)
        
        cls.injector = injector
        cls.logger.info('Registered %r.', injector)
    
    @classmethod
    def cls_unregister(cls, injector=None):
        if injector and cls.injector is not injector:
            return
        
        latter = cls.injector
        cls.injector = None
        cls.logger.info('Unregistered %r.', latter)
    
    @classmethod
    def cls_is_registered(cls, injector=None):
        if injector:
            return cls.injector is injector
        
        return cls.injector is not None
    
    def __init__(self, autobind=True, default_config=True, echo=False):
        self._autobind = autobind
        self._default_config = default_config
        if echo:
            configure_stdout_handler()
        
        self._init()
    
    def _init(self):
        self._scopes = {}
        self._scopes_stack = []
        
        self._app_scope = ApplicationScope()
        self.bind_scope(ApplicationScope, self._app_scope)
        
        if self._default_config:
            self._load_default_config()
    
    def _load_default_config(self):
        self.bind(Injector, to=self)
        
        thread_scope = ThreadScope()
        self.bind_scope(ThreadScope, thread_scope)
        
        reqscope = RequestScope()
        self.bind_scope(RequestScope, reqscope)
        
        self.logger.info('Loaded the default configuration.')
    
    def clear(self):
        '''Remove all bindings and scopes.'''
        self._app_scope = None
        self._scopes = None
        self._scopes_stack = None
        
        self.logger.info('Cleared all bindings.')
        self._init()
    
    def __contains__(self, type):
        '''Return True if type is bound, else return False.'''
        return self.is_bound(type)
    
    def bind(self, type, to=None):
        '''Specify a binding for a type in the application scope.'''
        if self.is_bound(type):
            self.unbind(type)
        
        self._app_scope.bind(type, to)
    
    def unbind(self, type):
        '''Unbind type in all scopes.
        
        @raise NotBoundError: if the type is not bound.
        '''
        for scope in self._scopes_stack:
            if scope.is_bound(type):
                scope.unbind(type)
                return
        
        raise NotBoundError(type)
    
    def is_bound(self, type):
        '''Return True if the type is bound in any scope, else return False.'''
        for scope in self._scopes_stack:
            if scope.is_bound(type):
                return True
        
        return False
    
    def get(self, type, none=False):
        '''Return a bound instance for a type or raise an error.
        
        @param none: If true, returns None when no binding is found, does not
            raise an error.
        
        @raise NotBoundError: if there is no binding for a type,
            and autobind is False or the type is not callable.
        '''
        for scope in self._scopes_stack:
            if scope.is_bound(type) or scope.is_factory_bound(type):
                return scope.get(type)
        
        if self._autobind and callable(type):
            inst = type()
            self.bind(type, inst)
            return inst
        
        if none:
            return
        
        raise NotBoundError(type)
    
    #==========================================================================
    # Factories
    #==========================================================================
    
    def bind_factory(self, type, factory):
        '''Bind a type factory in the application scope.'''
        if self.is_factory_bound(type):
            self.unbind_factory(type)
        
        self._app_scope.bind_factory(type, factory)
    
    def unbind_factory(self, type):
        '''Unbind a type factory in all scopes.
        
        @raise FactoryNotBoundError: if there is no bound type factory.
        '''
        for scope in self._scopes_stack:
            if scope.is_factory_bound(type):
                scope.unbind_factory(type)
                return
        
        raise FactoryNotBoundError(type)
    
    def is_factory_bound(self, type):
        '''Return True if there is a bound type factory in any scope,
        else return False.
        '''
        for scope in self._scopes_stack:
            if scope.is_factory_bound(type):
                return True
        
        return False
    
    #==========================================================================
    # Scopes
    #==========================================================================
    
    def bind_scope(self, scope_type, scope):
        self.unbind_scope(scope_type)
        
        self.bind(scope_type, scope)
        self._scopes[scope_type] = scope
        self._scopes_stack.append(scope)
        
        self.logger.info('Bound scope %r to %r.', scope_type, scope)
    
    def unbind_scope(self, scope_type):
        if scope_type not in self._scopes:
            return
        
        self.unbind(scope_type)
        scope = self._scopes[scope_type]
        del self._scopes[scope_type]
        self._scopes_stack.remove(scope)
        
        self.logger.info('Unbound scope %r.', scope)
    
    def is_scope_bound(self, scope_type):
        return scope_type in self._scopes
    
    #==========================================================================
    # Registering/unregistering
    #==========================================================================
    
    def register(self):
        '''Register this injector.
        
        @raise InjectorAlreadyRegistered: if another injector is already
            registered.
        '''
        self.cls_register(self)
    
    def unregister(self):
        '''Unregister this injector.'''
        self.cls_unregister(self)
    
    def is_registered(self):
        '''Return whether this injector is registered.'''
        return self.cls_is_registered(self)


def get_instance(type, none=False):
    '''Return an instance from the registered injector.
    
    @raise NoInjectorRegistered: if no injector is registered.
    '''
    injector = Injector.cls_get_injector()
    return injector.get(type, none=none)


def register(injector):
    Injector.cls_register(injector)


def unregister(injector=None):
    Injector.cls_unregister(injector)


def is_registered(injector=None):
    return Injector.cls_is_registered(injector)
