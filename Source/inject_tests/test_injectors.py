import unittest
from mock import Mock

import inject
from inject.injection import Injection
from inject.errors import NoInjectorRegistered, NoProviderError
from inject.injectors import Injector, register, unregister, is_registered, \
    get_instance


class ModuleFunctionsTestCase(unittest.TestCase):
    
    injector_class = Injector
    injection_class = Injection
    
    register_injector = staticmethod(register)
    unregister_injector = staticmethod(unregister)
    is_registered = staticmethod(is_registered)
    get_instance = staticmethod(get_instance)
    
    def tearDown(self):
        inject.unregister()
    
    def testRegisterUnregister(self):
        '''Register/unregister should set injections injector.'''
        inj = self.injection_class('inj')
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
        '''Get_instrance should return an instance, or raise an error.'''
        class A(object): pass
        
        self.unregister_injector()
        self.assertRaises(NoInjectorRegistered, self.get_instance, A)
        
        a = A()
        injector = Mock()
        injector.get_instance.return_value = a
        
        self.register_injector(injector)
        self.assertTrue(self.get_instance(A) is a)


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
        
        self.assertTrue(A in injector.bindings)
    
    def testBind(self):
        '''Injector.bind should create a provider for a type and save it.'''
        class A(object): pass
        class B(object): pass
        injector = self.injector_class()
        
        injector.bind(A, to=B)
        self.assertTrue(injector.bindings[A] is B)
    
    #==========================================================================
    # get_provider tests
    #==========================================================================
    
    def testGetProvider(self):
        '''Injector.get_provider should return a provider.'''
        class A(object): pass
        class B(object): pass
        
        injector = self.injector_class()
        injector.bindings[A] = B
        
        self.assertTrue(injector.get_provider(A) is B)
    
    def testGetProviderNoProviderError(self):
        '''Injector.get_provider should raise NoProviderError.'''
        class A(object): pass
        
        injector = self.injector_class(default_providers=False)
        self.assertRaises(NoProviderError, injector.get_provider, A)
    
    def testGetProviderDefaultProvider(self):
        '''Injector.get_provider should create a default provider.'''
        class A(object): pass
        
        injector = self.injector_class(default_providers=True)
        self.assertTrue(injector.get_provider(A) is A)
        self.assertTrue(A in injector.bindings)
    
    #==========================================================================
    # get_instance tests
    #==========================================================================
    
    def testGetInstance(self):
        '''Injector.get_instance should get a provider and call it.'''
        class A(object): pass
        class B(object): pass
        class MyInjector(self.injector_class):
            def get_provider(self, type):
                return B
        
        injector = MyInjector()
        
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, B))
    
    #==========================================================================
    # private methods tests
    #==========================================================================
    
    def testAddProvider(self):
        '''Injector._add_provider should store a provider in the bindings.'''
        injector = self.injector_class()
        injector._add_provider('a', 'b')
        
        self.assertTrue('a' in injector.bindings)
        self.assertEqual(injector.bindings['a'], 'b')
    
    def testCreateProvider(self):
        '''Injector._create_provider should instantiate a provider_class.'''
        class A(object): pass
        class B(object): pass
        class Provider(object):
            def __init__(self, type, to, scope):
                self.type = type
                self.to = to
                self.scope = scope
        
        class MyInjector(self.injector_class):
            provider_class = Provider
        
        injector = MyInjector()
        
        p = injector._create_provider(A, to=B, scope='scope')
        self.assertTrue(p.to is B and p.scope == 'scope')
        
        p2 = injector._create_provider(A, to=B)
        self.assertTrue(p2.to is B and p2.scope is None)
    
    def testCreateAddDefaultProvider(self):
        '''Injector._create_add_default_provider.'''
        class A(object): pass
        class Provider(object):
            def __init__(self, type, to, scope):
                self.type = type
                self.to = to
                self.scope = scope
        
        class MyInjector(self.injector_class):
            provider_class = Provider
        
        injector = MyInjector()
        injector._create_add_default_provider(A)
        
        self.assertTrue(A in injector.bindings)
        
        p = injector.bindings[A]
        self.assertTrue(p.type is A and p.to is None and p.scope is None)
