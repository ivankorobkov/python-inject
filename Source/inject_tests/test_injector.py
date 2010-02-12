import unittest

from inject.key import Key
from inject import errors, scopes
from inject.injector import Injector, register, unregister
from inject.injection import Injection


class RegisteringTestCase(unittest.TestCase):
    
    injector_class = Injector
    injection_class = Injection
    
    register_injector = staticmethod(register)
    unregister_injector = staticmethod(unregister)
    
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
    
    key_class = Key
    injector_class = Injector
    
    def testBind(self):
        '''Injector should bind type [,annotation] to a provider.'''
        class A(object): pass
        class B(object): pass
        class C(object): pass
        injector = self.injector_class()
        
        # Use type as a key.
        injector.bind(A, to=B)
        self.assertTrue(injector.bindings[A] is B)
        
        # Combine type and annotation into a key.
        injector.bind(A, annotation='test', to=B)
        key = self.key_class(A, 'test')
        self.assertTrue(injector.bindings[key] is B)
        
        # Bind to the type.
        injector.bind(C, annotation='test')
        key = self.key_class(C, 'test')
        self.assertTrue(injector.bindings[key] is C)
    
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
        '''Injector get_instance() should return an obj, or raise an error.'''
        class A(object): pass
        class B(object): pass
        injector = self.injector_class()
        
        self.assertRaises(errors.NoProviderError, injector.get_instance, A)
        
        # Get an instance by type.
        injector.bind(A, to=A)
        a = injector.get_instance(A)
        self.assertTrue(isinstance(a, A))
        
        # Get an instance by type, because there is no for Key(type, ann).
        a = injector.get_instance(A, 'test')
        self.assertTrue(isinstance(a, A))
        
        # Get an instance for Key(type, annotation). 
        injector.bind(A, 'test', to=B)
        a = injector.get_instance(A, 'test')
        self.assertTrue(isinstance(a, B))