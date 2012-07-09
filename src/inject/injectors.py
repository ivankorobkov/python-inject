'''Injectors are central part in C{python-inject}. They are used
by injection points (C{inject.attr}, C{inject.param}, etc.) to get bindings.
Injectors stores bindings in specific scopes which coordinate objects 
life-cycle.

An injector must be instantiated and registered before any injection point
is accessed. Only one injector can be registered at one time::

    >>> injector = Injector()
    >>> injector.register()
    
    >>> # or
    >>> injector = inject.create()

It can (and should) be used to configure application scoped
bindings, yet it delegates them to L{ApplicationScope}.

    >>> class A(object): pass
    >>> injector.bind(A, to=A())
    
    >>> # is equivalent to
    >>> scope = injector.get(ApplicationScope)
    >>> scope.bind(A, to=A())

Injection points use the L{Injector.get} method to get bindings for types.

    >>> class A(object): pass
    >>> a = A()
    >>> injector.bind(A to=a)
    >>> a2 = injector.get(A)
    >>> a is a2
    True

An injector by default creates and binds all scopes: L{ApplicationScope},
L{ThreadScope}, and L{RequestScope}. An injector cannot be used without
a bound application scope. Scopes are stored in a stack. By default,
they are accessed in this order: [application, thread, request].

'''
import logging
import threading
from functools import update_wrapper

from inject.exc import InjectorAlreadyRegistered, NoInjectorRegistered, \
    NotBoundError, AutobindingFailed
from inject.log import configure_stdout_handler
from inject.scopes import ApplicationScope, ThreadScope, RequestScope
import collections


logger = logging.getLogger('inject')


class Injector(object):
    
    '''C{Injector} provides injection points with bindings, delegates storing
    bindings to specific scopes which coordinate objects life-cycle.
    
    @warning: Not thread-safe.
    '''
    
    logger = logging.getLogger('inject.Injector')
    
    def __init__(self, autobind=True, echo=False):
        '''Create a new injector instance.
        
        @ivar autobind: Whether to autobind not bound types, 
            the default is true. 
        
        @ivar echo: When set to true creates a default C{inject} logger,
            adds an stdout handler, and sets the logging level to DEBUG.
            It affects all injectors.
        '''
        self.autobind = autobind
        if echo:
            configure_stdout_handler()
        
        self._init()
    
    def _init(self):
        '''Initialize the injector, create and bind ApplicationScope,
        and load the default configuration.
        '''
        self._scopes = {}
        self._scopes_stack = []
        
        self._app_scope = ApplicationScope()
        self.bind_scope(ApplicationScope, self._app_scope)
        
        self._default_config()
    
    def _default_config(self):
        '''Bind Injector to self, and create and bind ThreadScope
        and RequestScope.
        '''
        self.bind(Injector, to=self)
        
        thread_scope = ThreadScope()
        self.bind_scope(ThreadScope, thread_scope)
        
        reqscope = RequestScope()
        self.bind_scope(RequestScope, reqscope)
        
        self.logger.info('Loaded the default configuration.')
    
    def clear(self):
        '''Remove all bindings and scopes and reinit the injector.'''
        self._app_scope = None
        self._scopes = None
        self._scopes_stack = None
        
        self.logger.info('Cleared all bindings.')
        self._init()
    
    def __contains__(self, type):
        '''Return true if type is bound, else return False.'''
        return self.is_bound(type)
    
    def bind(self, type, to=None):
        '''Set a binding for a type in the application scope.'''
        if self.is_bound(type):
            self.unbind(type)
        
        self._app_scope.bind(type, to)
    
    def unbind(self, type):
        '''Unbind the first occurrence of a type in any scope.'''
        for scope in self._scopes_stack:
            if scope.is_bound(type):
                scope.unbind(type)
                return
    
    def is_bound(self, type):
        '''Return true if a type is bound in any scope, else return False.'''
        for scope in self._scopes_stack:
            if scope.is_bound(type):
                return True
        
        return False
    
    def get(self, type, none=False):
        '''Return a binding for a type, or autobind it, or raise an error.
        
        @param none: If true, returns None when no binding is found, does not
            raise an error.
        
        @raise NotBoundError: if there is no binding for a type,
            and autobind is false or the type is not callable.
        '''
        for scope in self._scopes_stack:
            if scope.is_bound(type) or scope.is_factory_bound(type):
                return scope.get(type)
        
        if self.autobind and isinstance(type, collections.Callable):
            try:
                inst = type()
            except Exception as e:
                raise AutobindingFailed(type, e)
            
            self.bind(type, inst)
            return inst
        
        if none:
            return
        
        raise NotBoundError(type)
    
    #==========================================================================
    # Factories
    #==========================================================================
    
    def bind_factory(self, type, factory):
        '''Bind a type factory in the application scope
        (at first, unbind an existing one if present).
        '''
        if self.is_factory_bound(type):
            self.unbind_factory(type)
        
        self._app_scope.bind_factory(type, factory)
    
    def unbind_factory(self, type):
        '''Unbind the first occurrence of a type factory in any scope.'''
        for scope in self._scopes_stack:
            if scope.is_factory_bound(type):
                scope.unbind_factory(type)
                return
    
    def is_factory_bound(self, type):
        '''Return true if there is a bound type factory in any scope,
        else return false.
        '''
        for scope in self._scopes_stack:
            if scope.is_factory_bound(type):
                return True
        
        return False
    
    #==========================================================================
    # Scopes
    #==========================================================================
    
    def bind_scope(self, scope_type, scope):
        '''Bind a new scope, unbind another one if present.'''
        self.unbind_scope(scope_type)
        
        self.bind(scope_type, scope)
        self._scopes[scope_type] = scope
        self._scopes_stack.append(scope)
        
        self.logger.info('Bound scope %r to %r.', scope_type, scope)
    
    def unbind_scope(self, scope_type):
        '''Unbind a scope.'''
        if scope_type not in self._scopes:
            return
        
        self.unbind(scope_type)
        scope = self._scopes[scope_type]
        del self._scopes[scope_type]
        self._scopes_stack.remove(scope)
        
        self.logger.info('Unbound scope %r.', scope)
    
    def is_scope_bound(self, scope_type):
        '''Return true if a scope is bound.'''
        return scope_type in self._scopes
    
    #==========================================================================
    # Registering/unregistering
    #==========================================================================
    
    def register(self):
        '''Register this injector, or raise an error.
        
        @raise InjectorAlreadyRegistered: if another injector is already
            registered.
        '''
        global register
        register(self)

    def unregister(self):
        '''Unregister this injector.'''
        global unregister
        unregister(self)
     
    def is_registered(self):
        '''Return whether this injector is registered.'''
        global is_registered
        return is_registered(self)


class LazyInjector(object):
    
    '''C{LazyInjector} creates, registers and configures a real injector
    on the first dependency injection. It provides lazy loading of bindings
    so that C{python-inject} can be used inside C{django}'s C{settings.py}. 
    
    C{LazyInjector} is thread-safe.
    
    Example::
        # at the bottom of settings.py
        def configure_bindings(injector):
            import bindings
            bindings.configure(injector)
        
        # Django settings can be imported multiple times.
        # Skip, if another injector is already registered.
        if not inject.is_registered():
            inject.create_lazy(configure_bindings)
        
        # bindings.py
        from django.conf import settings
        
        def configure(injector):
            # Access django settings without circular dependency errors.
            my_inst = MyClass(settings.MY_SETTING)
            injector.bind(MyClass, my_inst)
    
    '''
    
    logger = logging.getLogger('inject.LazyInjector')
    ATTRS = ('config', 'factory', 'args', 'kwargs')
    
    def __init__(self, config, factory=Injector, *args, **kwargs):
        '''Create a new lazy injector.
        
        @param config: A callable which takes an injector and configures
            its bindings.
        @param factory: An injector factory which is used to create
            a real injector.
        @param args: Positional arguments which are passed to the factory.
        @param kwargs: Keyword arguments which are passed to the factory.
        '''
        self.config = config
        self.factory = factory
        self.args = args
        self.kwargs = kwargs
    
    def __getattr__(self, key):
        injector = self._init_real_injector()
        return getattr(injector, key)
    
    def __setattr__(self, key, value):
        if key in self.ATTRS:
            return super(LazyInjector, self).__setattr__(key, value)
        
        injector = self._init_real_injector()
        setattr(injector, key, value)
    
    def _init_real_injector(self):
        '''Create, register and configure a real injector.'''
        global register, _REG_LOCK
        
        with _REG_LOCK:
            self.logger.info('Creating a real injector using %s.', self.factory)
            injector = self.factory(*self.args, **self.kwargs)
            
            unregister(self)
            register(injector)
            
            self.logger.info('Configuring %s with %s.', injector, self.config)
            self.config(injector)
            
            return injector


_REG_LOCK = threading.RLock()
_INJECTOR = None


def get_injector():
    '''Return the current registered injector.'''
    return _INJECTOR


def get_instance(type, none=False):
    '''Return an instance from the registered injector.
    
    @raise NoInjectorRegistered: if no injector is registered.
    '''
    injector = _INJECTOR
    if injector is None:
        raise NoInjectorRegistered()
    
    return injector.get(type, none=none)


def _synchronized(func):
    def wrapper(*args, **kwargs):
        with _REG_LOCK:
            return func(*args, **kwargs)
    
    update_wrapper(wrapper, func)
    return wrapper


@_synchronized
def create(autobind=True, echo=False):
    '''Create, register and return a new injector.
    
    @raise InjectorAlreadyRegistered: if another injector is already registered.
    '''
    injector = Injector(autobind=autobind, echo=echo)
    register(injector)
    return injector


@_synchronized
def create_lazy(config, factory=Injector, autobind=True, echo=False):
    '''Create, register and return a new lazy injector.'''
    injector = LazyInjector(config, factory=factory, autobind=autobind,
                            echo=echo)
    register(injector)
    return injector


@_synchronized
def register(injector):
    '''Register an injector.'''
    global _INJECTOR
    if _INJECTOR is not None:
        raise InjectorAlreadyRegistered(_INJECTOR)
    
    _INJECTOR = injector
    logger.info('Registered %r.', injector)


@_synchronized
def unregister(injector=None):
    '''Unregister an injector if given, or any injector.'''
    global _INJECTOR
    if injector and _INJECTOR is not injector:
        return
    
    latter = _INJECTOR
    _INJECTOR = None
    logger.info('Unregistered %r.', latter)


@_synchronized
def is_registered(injector=None):
    '''Return true if a given injector, or any injector is registered.'''
    registered = _INJECTOR
    if injector:
        return registered is injector
    
    return registered is not None
