import unittest

import inject
from inject.injectors import Injector, register, unregister, is_registered, \
    get_instance, NoInjectorRegistered, NoProviderError, ScopeNotBoundError, \
    CantCreateProviderError
from inject.points import InjectionPoint
from inject.scopes import ScopeInterface, set_default_scope, \
    clear_default_scopes


class ModuleFunctionsTestCase(unittest.TestCase):
    
    injector_class = Injector
    point_class = InjectionPoint
    
    register_injector = staticmethod(register)
    unregister_injector = staticmethod(unregister)
    is_registered = staticmethod(is_registered)
    get_instance = staticmethod(get_instance)
    
    def tearDown(self):
        inject.unregister()
    
    def testRegisterUnregister(self):
        '''Register/unregister should set injections injector.'''
        inj = self.point_class('inj')
        self.assertTrue(inj.injector is None)
        
        injector = self.injector_class()
        injector2 = self.injector_class()
        
        self.register_injector(injector)
        self.assertTrue(inj.injector is injector)
        
        self.unregister_injector(injector2)
        self.assertTrue(inj.injector is injector)
        
        self.unregister_injector(injector)
        self.assertTrue(inj.injector is None)
        
        self.register_injector(injector)
        self.unregister_injector()
        self.assertTrue(inj.injector is None)
    
    def testIsRegistered(self):
        '''Is_registered should return whether an injector is registered.'''
        injector = self.injector_class()
        injector2 = self.injector_class()
        
        self.assertFalse(self.is_registered(injector))
        self.assertFalse(self.is_registered(injector2))
        
        self.register_injector(injector)
        self.assertTrue(self.is_registered(injector))
        self.assertFalse(self.is_registered(injector2))
    
    def testGetInstance(self):
        '''Get_instrance should return an instance from an injector.'''
        class A(object): pass
        
        self.assertRaises(NoInjectorRegistered, self.get_instance, A)
    
    def testGetInstanceNoInjectorRegistered(self):
        '''Get_instance should raise NoInjectorRegistered.'''
        class A(object): pass
        
        a = A()
        injector = self.injector_class(create_default_providers=True)
        injector.bind(A, to=a)
        self.register_injector(injector)
        
        a2 = self.get_instance(A)
        self.assertTrue(a2 is a)


class InjectorTestCase(unittest.TestCase):
    
    injector_class = Injector

    def testConfigure(self):
        '''Injector should be configurable using callables.'''
        class A(object): pass
        class A2(object): pass
        def config(injector):
            injector.bind(A, to=A2)
        
        injector = self.injector_class()
        injector.configure(config)
        
        self.assertTrue(A in injector.providers)
    
    def testBind(self):
        '''Injector.bind should create a provider for a type and save it.'''
        class A(object): pass
        class B(object): pass
        injector = self.injector_class()
        
        injector.bind(A, to=B)
        self.assertTrue(injector.providers[A] is B)
    
    def testBindScope(self):
        '''Injector.bind_scope should bind a scope class to an instance.'''
        class Scope(object): pass
        scope = Scope()
        
        injector = self.injector_class()
        injector.bind_scope(Scope, scope)
        
        self.assertTrue(injector.bound_scopes[Scope] is scope)
    
    def testIsBound(self):
        '''Injector.is_bound should return True.'''
        class A(object): pass
        
        injector = self.injector_class()
        injector.bind(A, to=A)
        self.assertTrue(injector.is_bound(A))
    
    def testIsBoundFalse(self):
        '''Injector.is_bound should return False.'''
        class A(object): pass
        
        injector = self.injector_class()
        self.assertFalse(injector.is_bound(A))
    
    #==========================================================================
    # get_provider tests
    #==========================================================================
    
    def testGetProvider(self):
        '''Injector.get_provider should return a provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        injector.bind(A, to=B)
        
        self.assertTrue(injector.get_provider(A) is B)
    
    def testGetProviderCreateDefaultProviders(self):
        '''Injector.get_provider should create a default provider.'''
        class A(object): pass
        
        injector = self.injector_class(create_default_providers=True)
        provider = injector.get_provider(A)
        self.assertTrue(provider is A)
    
    def testGetProviderNoProviderError(self):
        '''Injector.get_provider should raise NoProviderError.
        
        When create_default_providers is False.
        '''
        class A(object): pass
        
        injector = self.injector_class(create_default_providers=False)
        self.assertRaises(NoProviderError, injector.get_provider, A)
    
    def testAddProvider(self):
        '''Injector._add_provider should add a new provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        injector._add_provider(A, B)
        
        provider = injector.get_provider(A)
        self.assertTrue(provider is B)
    
    def testCreateProvider(self):
        '''Injector._create_provider should create a provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        provider = injector._create_provider(A, B)
        
        self.assertTrue(provider is B)
    
    def testCreateProviderToIsNone(self):
        '''Injector._create_provider should use a callable type, when no to.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        
        provider = injector._create_provider(A)
        self.assertTrue(provider is A)
    
    def testCreateProviderCantCreateProviderError(self):
        '''Injector._create_provider should raise CantCreateProviderError.
        
        When to is None, and type is not callable.
        '''
        injector = self.injector_class()
        self.assertRaises(CantCreateProviderError, injector._create_provider,
                          'type')

    def testCreateDefaultProvider(self):
        '''Inject._create_default_provider should create a default provider.'''
        class A(object): pass
        
        injector = self.injector_class()
        provider = injector._create_default_provider(A)
        
        self.assertTrue(provider is A)
    
    def testCreateProviderScope(self):
        '''Injector._create_provider should scope a provider.
        
        When scope is given.
        '''
        class A(object): pass
        class Scope(ScopeInterface):
            def scope(self, provider):
                return 'scoped_provider'
        
        scope = Scope()
        
        injector = self.injector_class()
        injector.bind_scope(Scope, to=scope)
        
        scoped_provider = injector._create_provider(A, scope=Scope)
        self.assertEqual(scoped_provider, 'scoped_provider')
    
    def testScopeProvider(self):
        '''Inject._scope_provider should return a scoped provider.'''
        class A(object): pass
        class Scope(ScopeInterface):
            def scope(self, provider):
                return 'scoped_provider'
        
        scope = Scope()
        
        injector = self.injector_class()
        injector.bind_scope(Scope, to=scope)
        
        scoped_provider = injector._scope_provider(A, scope=Scope)
        self.assertEqual(scoped_provider, 'scoped_provider')
    
    def testScopeProviderNotBound(self):
        '''Inject._scope_provider should raise ScopeNotBound.'''
        class A(object): pass
        class Scope(ScopeInterface): pass
        
        injector = self.injector_class()
        self.assertRaises(ScopeNotBoundError, injector._scope_provider,
            A, scope=Scope)
    
    def testScopeProviderDefaultScope(self):
        '''Inject._scope_provider should get a default scope.
        
        When scope is not given, and the default scope is set.
        '''
        class A(object): pass
        class Scope(ScopeInterface):
            def scope(self, provider):
                return 'scoped_provider'
        
        scope = Scope()
        injector = self.injector_class()
        injector.bind_scope(Scope, to=scope)
        
        set_default_scope(A, Scope)
        try:
            
            scoped_provider = injector._scope_provider(A)
            self.assertEqual(scoped_provider, 'scoped_provider')
        finally:
            clear_default_scopes()
    
    #==========================================================================
    # get_instance tests
    #==========================================================================
    
    def testGetInstance(self):
        '''Injector.get_instance should return an instance.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        injector.bind(A, to=B)
        
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, B))
    
    def testGetInstanceCreateDefaultProviders(self):
        '''Injector.get_instance should use a default provider.
        
        When create_default_providers is True.
        '''
        class A(object): pass
        
        injector = self.injector_class()
        
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, A))
