import unittest

import inject
from inject import errors, scopes
from inject.injectors import Injector, register, unregister
from inject.injection import Injection
from inject.errors import NoProviderError


class RegisteringTestCase(unittest.TestCase):
    
    injector_class = Injector
    injection_class = Injection
    
    register_injector = staticmethod(register)
    unregister_injector = staticmethod(unregister)
    
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


class InjectorTestCase(unittest.TestCase):
    
    injector_class = Injector
    
    def tearDown(self):
        inject.unregister()
    
    def testBind(self):
        '''Injector should bind type to a provider.'''
        class A(object): pass
        class B(object): pass
        class C(object): pass
        injector = self.injector_class()
        
        # Use type as a key.
        injector.bind(A, to=B)
        self.assertTrue(injector.bindings[A] is B)
        
        # Bind to the type.
        injector.bind(C)
        key = (C)
        self.assertTrue(injector.bindings[key] is C)
    
    def testConfigure(self):
        '''Injector should be configurable using callables.'''
        class A(object): pass
        class A2(object): pass
        def config(injector):
            injector.bind(A, to=A2)
        
        injector = self.injector_class()
        injector.configure(config)
        
        self.assertTrue(A in injector.bindings)
    
    def testProvider(self):
        '''Injector should create an [inst, scoped] provider for a binding.'''
        class A(object): pass
        class B(object): pass
        injector = self.injector_class()
        
        # Use a callable as a provider, no scope.
        injector.bind(A, to=B)
        b = injector.bindings[A]()
        b2 = injector.bindings[A]()
        self.assertTrue(isinstance(b, B))
        self.assertTrue(isinstance(b2, B))
        self.assertTrue(b is not b2)
        
        injector.bindings.clear()
        
        # Use a callable as a provider, scope it. 
        injector.bind(A, to=B, scope=scopes.app)
        b = injector.bindings[A]()
        b2 = injector.bindings[A]()
        self.assertTrue(isinstance(b, B))
        self.assertTrue(b is b2)
        
        injector.bindings.clear()
        
        # Convert an instance into an instance provider.
        injector.bind(A, to='My a')
        a = injector.bindings[A]()
        a2 = injector.bindings[A]()
        self.assertEqual(a, 'My a')
        self.assertEqual(a2, 'My a')
        
    def testGetInstance(self):
        '''Injector get_instance should return an instance.'''
        class A(object): pass
        class B(object): pass
        injector = self.injector_class()
        
        injector.bind(A, to=A)
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, A))
    
    def testDefaultProviders(self):
        '''Injector should call type when default_providers is True.'''
        class A(object): pass
        
        injector = self.injector_class(default_providers=True)
        a = injector.get_instance(A)
        
        self.assertTrue(isinstance(a, A))
    
    def testDefaultProvidersNotCallable(self):
        '''Injector should raise an error when type is not callable.'''
        A = 'A'
        
        injector = self.injector_class()
        self.assertRaises(NoProviderError, injector.get_instance, A)
    
    def testDefaultProvidersFalse(self):
        '''Injector should raise an error when default_providers is False.'''
        class A(object): pass
        
        injector = self.injector_class(default_providers=False)
        self.assertRaises(NoProviderError, injector.get_instance, A)
