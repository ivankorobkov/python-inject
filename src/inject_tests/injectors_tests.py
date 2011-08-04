import unittest

from inject.exc import NotBoundError
from inject.injectors import Injector
from inject.scopes import ThreadScope


class InjectorTestCase(unittest.TestCase):
    
    def testClear(self):
        '''Injector.clear should clear its bindings.'''
        class A(object): pass
        a = A()
        
        injector = Injector()
        injector.bind(A, a)
        self.assertTrue(injector.is_bound(A))
        
        injector.clear()
        self.assertFalse(injector.is_bound(A))
    
    def testBind(self):
        '''Injector.bind should create a provider for a type and save it.'''
        class A(object): pass
        a = A()
        
        injector = Injector()
        injector.bind(A, to=a)
        self.assertTrue(injector.get(A) is a)
    
    def testBindToNone(self):
        '''Injector.bind_to_none should create a provider which returns None.'''
        class A(object): pass
        
        injector = Injector()
        injector.bind(A, None)
        self.assertTrue(injector.get(A) is None)
    
    def testIsBound(self):
        '''Injector.is_bound should return True.'''
        class A(object): pass
        a = A()
        
        injector = Injector()
        injector.bind(A, to=a)
        self.assertTrue(injector.is_bound(A))
    
    def testIsNotBound(self):
        '''Injector.is_bound should return False.'''
        class A(object): pass
        
        injector = Injector()
        self.assertFalse(injector.is_bound(A))
    
    def testUnbind(self):
        '''Injector.unbind should remove a binding.'''
        class A(object): pass
        a = A()
        
        injector = Injector()
        injector.bind(A, a)
        self.assertTrue(injector.is_bound(A))
        
        injector.unbind(A)
        self.assertFalse(injector.is_bound(A))
    
    def testUnbindNotBoundError(self):
        '''Injector.unbind should raise NotBoundError.'''
        class A(object): pass
        
        injector = Injector()
        self.assertRaises(NotBoundError, injector.unbind, A)
    
    def testGet(self):
        '''Injector.get should return an instance.'''
        class A(object): pass
        a = A()
        
        injector = Injector()
        injector.bind(A, to=a)
        
        a2 = injector.get(A)
        self.assertTrue(a2 is a)
    
    def testGetMultipleScopes(self):
        class A(object): pass
        a = A()
        
        injector = Injector()
        scope = injector.get(ThreadScope)
        scope.bind(A, a)
        
        self.assertTrue(injector.get(A) is a)


class InjectorScopesTestCase(unittest.TestCase):

    def testBindScope(self):
        class Scope(object): pass
        scope = Scope()
        
        injector = Injector()
        injector.bind_scope(Scope, scope)
        
        self.assertTrue(injector.get(Scope) is scope)
        self.assertTrue(injector.is_scope_bound(Scope))
    
    def testUnbindScope(self):
        class Scope(object): pass
        scope = Scope()
        
        injector = Injector()
        injector.bind_scope(Scope, scope)
        
        injector.unbind_scope(Scope)
        self.assertRaises(NotBoundError, injector.get, Scope)
        self.assertFalse(injector.is_bound(Scope))
        self.assertFalse(injector.is_scope_bound(Scope))


class InjectorRegisterTestCase(unittest.TestCase):
    
    def tearDown(self):
        Injector.cls_unregister()
    
    def testRegisterUnregister(self):
        injector = Injector()
        injector2 = Injector()
        
        injector.register()
        self.assertTrue(Injector.injector is injector)
        
        injector2.unregister()
        self.assertTrue(Injector.injector is injector)
        
        injector.unregister()
        self.assertTrue(Injector.injector is None)
        
        injector.register()
        Injector.cls_unregister()
        self.assertTrue(Injector.injector is None)
    
    def testIsRegistered(self):
        injector = Injector()
        injector2 = Injector()
        
        self.assertFalse(injector.is_registered())
        self.assertFalse(injector2.is_registered())
        
        injector.register()
        self.assertTrue(injector.is_registered())
        self.assertFalse(injector2.is_registered())
