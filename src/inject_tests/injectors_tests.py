import unittest

import inject
from inject.injections import InjectionPoint, NoInjectorRegistered
from inject.injectors import Injector, register, unregister, is_registered, \
    get_instance, NotBoundError, ScopeNotBoundError, CantCreateProviderError
from inject.scopes import ScopeInterface
from inject.exc import CantGetInstanceError


class ModuleFunctionsTestCase(unittest.TestCase):
    
    def tearDown(self):
        inject.unregister()
    
    def testRegisterUnregister(self):
        '''Register/unregister should set injections injector.'''
        inj = InjectionPoint('inj')
        self.assertTrue(inj.injector is None)
        
        injector = Injector()
        injector2 = Injector()
        
        register(injector)
        self.assertTrue(inj.injector is injector)
        
        unregister(injector2)
        self.assertTrue(inj.injector is injector)
        
        unregister(injector)
        self.assertTrue(inj.injector is None)
        
        register(injector)
        unregister()
        self.assertTrue(inj.injector is None)
    
    def testIsRegistered(self):
        '''Is_registered should return whether an injector is registered.'''
        injector = Injector()
        injector2 = Injector()
        
        self.assertFalse(is_registered(injector))
        self.assertFalse(is_registered(injector2))
        
        register(injector)
        self.assertTrue(is_registered(injector))
        self.assertFalse(is_registered(injector2))

    def testGetInstance(self):
        '''Get_instance should return an instance from an injector.'''
        class A(object): pass
        
        self.assertRaises(NoInjectorRegistered, get_instance, A)
    
    def testGetInstanceNoInjectorRegistered(self):
        '''Get_instance should raise NoInjectorRegistered.'''
        class A(object): pass
        
        a = A()
        injector = Injector(create_default_providers=True)
        injector.bind(A, to=a)
        register(injector)
        
        a2 = get_instance(A)
        self.assertTrue(a2 is a)


class InjectorTestCase(unittest.TestCase):
    
    def testConfigure(self):
        '''Injector should be configurable.'''
        class A(object): pass
        class A2(object): pass
        def config(injector):
            injector.bind(A, to=A2)
        
        injector = Injector()
        config(injector)
        
        self.assertTrue(A in injector._bindings)
    
    def testClear(self):
        '''Injector.clear should clear its bindings.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        injector.bind(A, to=B)
        self.assertTrue(injector._bindings)
        
        injector.clear(default_config=False)
        self.assertFalse(injector._bindings)
    
    def testBind(self):
        '''Injector.bind should create a provider for a type and save it.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        injector.bind(A, to=B)
        self.assertTrue(injector._bindings[A] is B)
    
    def testBindToNone(self):
        '''Injector.bind_to_none should create a provider which returns None.'''
        class A(object): pass
        
        injector = Injector()
        injector.bind_to_none(A)
        self.assertTrue(injector.get_instance(A) is None)
    
    def testBindToInstance(self):
        '''Injector.bind_to_instance should support binding callable instances.'''
        class A(object):
            def __call__(self):
                pass
        
        a = A()
        
        injector = Injector()
        injector.bind_to_instance(A, a)
        self.assertTrue(injector.get_instance(A) is a)
    
    def testBindScope(self):
        '''Injector.bind should bind a scope class to an instance.'''
        class Scope(object): pass
        scope = Scope()
        
        injector = Injector()
        injector.bind(Scope, scope)
        
        self.assertTrue(injector._get_bound_scope(Scope) is scope)
    
    def testIsBound(self):
        '''Injector.is_bound should return True.'''
        class A(object): pass
        
        injector = Injector()
        injector.bind(A, to=A)
        self.assertTrue(injector.is_bound(A))
    
    def testIsBoundFalse(self):
        '''Injector.is_bound should return False.'''
        class A(object): pass
        
        injector = Injector()
        self.assertFalse(injector.is_bound(A))
    
    def testUnbind(self):
        '''Injector.unbind should remove a binding.'''
        class A(object): pass
        
        injector = Injector()
        injector.bind(A, to=A)
        self.assertTrue(injector.is_bound(A))
        
        injector.unbind(A)
        self.assertFalse(injector.is_bound(A))
    
    def testUnbindNotBoundError(self):
        '''Injector.unbind should raise NotBoundError.'''
        class A(object): pass
        
        injector = Injector()
        self.assertRaises(NotBoundError, injector.unbind, A)
    
    #==========================================================================
    # get_provider tests
    #==========================================================================
    
    def testGetProvider(self):
        '''Injector.get_provider should return a provider.'''
        class A(object): pass
        class B(object): pass
        class C(object): pass
        
        injector = Injector()
        injector.bind(A, to=B)
        
        self.assertTrue(injector.get_provider(A) is B)
    
    def testGetProviderCreateDefaultProviders(self):
        '''Injector.get_provider should create a default provider.'''
        class A(object): pass
        
        injector = Injector(create_default_providers=True)
        provider = injector.get_provider(A)
        self.assertTrue(provider is A)
    
    def testGetProviderNoProviderError(self):
        '''Injector.get_provider should raise NotBoundError.
        
        When create_default_providers is False.
        '''
        class A(object): pass
        
        injector = Injector(create_default_providers=False)
        self.assertRaises(NotBoundError, injector.get_provider, A)
    
    def testAddProvider(self):
        '''Injector._add_provider should add a new provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        injector._add_provider(A, B)
        
        provider = injector.get_provider(A)
        self.assertTrue(provider is B)
    
    def testCreateProvider(self):
        '''Injector._create_provider should create a provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        provider = injector._create_provider(A, B)
        
        self.assertTrue(provider is B)
    
    def testCreateProviderToIsNone(self):
        '''Injector._create_provider should use a callable type, when no to.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        
        provider = injector._create_provider(A)
        self.assertTrue(provider is A)
    
    def testCreateProviderCantCreateProviderError(self):
        '''Injector._create_provider should raise CantCreateProviderError.
        
        When to is None, and type is not callable.
        '''
        injector = Injector()
        self.assertRaises(CantCreateProviderError, injector._create_provider,
                          'type')

    def testCreateDefaultProvider(self):
        '''Inject._create_default_provider should create a default provider.'''
        class A(object): pass
        
        injector = Injector()
        provider = injector._create_default_provider(A)
        
        self.assertTrue(provider is A)
    
    def testCreateProviderScope(self):
        '''Injector._create_provider should scope a provider.
        
        When a scope is given.
        '''
        class A(object): pass
        class Scope(ScopeInterface):
            def scope(self, provider):
                return 'scoped_provider'
        
        scope = Scope()
        
        injector = Injector()
        injector.bind(Scope, to=scope)
        
        scoped_provider = injector._create_provider(A, scope=Scope)
        self.assertEqual(scoped_provider, 'scoped_provider')
    
    def testScopeProvider(self):
        '''Inject._scope_provider should return a scoped provider.'''
        class A(object): pass
        class Scope(ScopeInterface):
            def scope(self, provider):
                return 'scoped_provider'
        
        scope = Scope()
        
        injector = Injector()
        injector.bind(Scope, to=scope)
        
        scoped_provider = injector._scope_provider(A, scope=Scope)
        self.assertEqual(scoped_provider, 'scoped_provider')
    
    def testScopeProviderNotBound(self):
        '''Inject._scope_provider should raise ScopeNotBound.'''
        class A(object): pass
        class Scope(ScopeInterface): pass
        
        injector = Injector()
        self.assertRaises(ScopeNotBoundError, injector._scope_provider,
            A, scope=Scope)
    
    #==========================================================================
    # get_instance tests
    #==========================================================================
    
    def testGetInstance(self):
        '''Injector.get_instance should return an instance.'''
        class A(object): pass
        class B(object): pass
        
        injector = Injector()
        injector.bind(A, to=B)
        
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, B))
    
    def testGetInstanceCreateDefaultProviders(self):
        '''Injector.get_instance should use a default provider.
        
        When create_default_providers is True.
        '''
        class A(object): pass
        
        injector = Injector()
        
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, A))
    
    def testCantGetInstanceError(self):
        '''Injector.get_instance should raise CantGetInstanceError.'''
        class A(object):
            def __init__(self, b):
                pass
        
        injector = Injector()
        self.assertRaises(CantGetInstanceError, injector.get_instance, A)
