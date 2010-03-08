import unittest

import inject
from inject.key import Key
from inject import errors, scopes
from inject.injectors import Injector, register, unregister
from inject.injection import Injection


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
    
    key_class = Key
    injector_class = Injector
    
    def tearDown(self):
        inject.unregister()
    
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
    
    def testAttr(self):
        '''Injector.attr should create an injector-specific injection.'''
        inj = self.injector_class()
        
        class A(object): pass
        class B(object):
            a = inj.attr('a', A)
        
        b = B()
        self.assertTrue(B.a.injection.injector is inj)
        self.assertTrue(isinstance(b.a, A))
    
    def testInvoker(self):
        '''Injector.invoker should create an injector-specific invoker.'''
        inj = self.injector_class()
        
        class A(object):
            def method(self):
                return 'method'
        
        invoker = inj.invoker(A.method)
        
        self.assertTrue(invoker.injection.injector is inj)
        self.assertEqual(invoker(), 'method')
    
    def testMultipleInjectors(self):
        '''Multiple injectors should not interfere with each other.'''
        inj = self.injector_class()
        inj2 = self.injector_class()
        register(inj2)
        
        class A(object): pass
        class A2(object): pass
        class B(object):
            @inj.param('a', A)
            def __init__(self, a):
                self.a = a
        
        class B2(object):
            @inject.param('a', A)
            def __init__(self, a):
                self.a = a
        
        inj2.bind(A, to=A2)
        
        b = B()
        b2 = B2()
        
        self.assertTrue(isinstance(b.a, A))
        self.assertTrue(isinstance(b2.a, A2))