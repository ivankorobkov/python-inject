import unittest

from inject import scopes, errors
from inject.injector import Injector
from inject.injection import Injection


class InjectionTestCase(unittest.TestCase):
    
    injector_class = Injector
    injection_class = Injection
    
    def test(self):
        '''Injection should return an instance using a default provider.'''
        class A(object): pass
        inj = self.injection_class(A)
        a = inj.get_instance()
        a2 = inj.get_instance()
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(isinstance(a2, A))
        self.assertTrue(a is not a2)
    
    def testScope(self):
        '''Injection should return an instance using a scoped provider.'''
        class A(object): pass
        inj = self.injection_class(A, scope=scopes.app)
        a = inj.get_instance()
        a2 = inj.get_instance()
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
        
        scopes.app.clear()
    
    def testProviderFromType(self):
        '''If bindto is not given, Injection should use type, if callable.'''
        class A(object): pass
        inj = self.injection_class(A)
        self.assertTrue(inj.provider is A)
    
    def testProviderFromBindTo(self):
        '''Injection should use bindto to create a provider, if given.'''
        class A(object): pass
        class B(object): pass
        inj = self.injection_class(A, bindto=B)
        
        b = inj.get_instance()
        self.assertTrue(isinstance(b, B))
    
    def testGetInstanceFromInjector(self):
        '''If an injector is set, Injection should get an instance from it.'''
        class A(object): pass
        class B(object): pass
        class C(object): pass
        myinjector = self.injector_class()
        
        class MyInjection(self.injection_class):
            injector = myinjector
        
        # Get by type.
        inj = MyInjection(A)
        myinjector.bind(A, to=B)
        b = inj.get_instance()
        self.assertTrue(isinstance(b, B))
        
        # First, try to get by key because annotation is given.
        # Then, by type.
        inj = MyInjection(A, annotation='test') 
        b = inj.get_instance()
        self.assertTrue(isinstance(b, B))
        
        # Get by key.
        inj = MyInjection(A, annotation='test')
        myinjector.bind(A, annotation='test', to=C)
        c = inj.get_instance()
        self.assertTrue(isinstance(c, C))
        
        # No binding, use the default.
        inj = MyInjection(B, annotation='test')
        b = inj.get_instance()
        self.assertTrue(isinstance(b, B))
        
        # No binding and no default, raise NoProviderError.
        inj = MyInjection('type', annotation='test')
        self.assertRaises(errors.NoProviderError, inj.get_instance)