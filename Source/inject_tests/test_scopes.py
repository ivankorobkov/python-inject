import sys
import weakref
import unittest
import threading

from inject import errors, scopes


class AbstractTestCase(unittest.TestCase):
    
    scope_class = scopes.Abstract
    
    def setUp(self):
        self.scope = self.scope_class()
    
    def testDecorator(self):
        '''Scope decorator should set function's STORE_ATTR.'''
        scope = self.scope
        
        @scope
        def func(): pass
        
        self.assertTrue(getattr(func, scopes.SCOPE_ATTR) is scope)


if sys.version_info[0] == 2 and sys.version_info[1] >= 6:
    from test_scopes26 import testClassDecorator
    AbstractTestCase.testClassDecorator = testClassDecorator


class ApplicationTestCase(AbstractTestCase):
    
    scope_class = scopes.Application
    
    def testScope(self):
        '''App scope should create a cached scoped provider.'''
        scope = self.scope
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        a = scopedprovider()
        self.assertTrue(isinstance(a, A))
        
        a2 = scopedprovider()
        self.assertTrue(a is a2)


class RequestTestCase(AbstractTestCase):
    
    scope_class = scopes.Request
    
    def testRequestScope(self):
        '''Request scope should create a request-local provider.'''
        scope = self.scope
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        
        
        scope.register()
        a = scopedprovider()
        a2 = scopedprovider()
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
        
        
        scope.register()
        a3 = scopedprovider()
        
        self.assertTrue(a is a2)
        self.assertTrue(a3 is not a)
        self.assertTrue(isinstance(a3, A))
    
    def testThreadingScope(self):
        '''Request scope should create a thread-local provider.'''
        scope = self.scope
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        
        scope.register()
        a = scopedprovider()
        
        def run():
            scope.register()
            a2 = scopedprovider()
            self.assertTrue(a is not a2)
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
    
    def testProviderNoRequestRegistered(self):
        '''Request-scoped provider should raise NoRequestRegisteredError.'''
        scope = self.scope
        def provider(): pass
        
        scopedprovider = scope.scope(provider)
        self.assertRaises(errors.NoRequestRegisteredError, scopedprovider)
    
    def testThreadLocalRequestRegister(self):
        '''Request register should affect only one thread.'''
        scope = self.scope
        def provider(): pass
        scopedprovider = scope.scope(provider)
        
        def run():
            self.assertRaises(errors.NoRequestRegisteredError, scopedprovider)
        
        scope.register()
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
    
    def testUnregister(self):
        '''Request unregister should delete the instances cache.'''
        scope = self.scope
        class A(object): pass
        scopedprovider = scope.scope(A)
        
        scope.register()
        a = weakref.ref(scopedprovider())
        
        self.assertTrue(isinstance(a(), A))
        scope.unregister()
        
        self.assertTrue(a() is None)
