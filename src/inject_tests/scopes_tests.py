import threading
import unittest
import weakref

from inject.scopes import NoRequestStartedError, ApplicationScope, \
    RequestScope, NoScope, ThreadScope


class NoScopeTestCase(unittest.TestCase):
    
    def testScope(self):
        '''NoScope should return the provider untouched.'''
        class A(object): pass
        scope = NoScope()
        
        A2 = scope.scope(A)
        self.assertTrue(A is A2)


class ApplicationScopeTestCase(unittest.TestCase):
    
    def testScope(self):
        '''Application scope should create a cached scoped provider.'''
        scope = ApplicationScope()
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        a = scopedprovider()
        self.assertTrue(isinstance(a, A))
        
        a2 = scopedprovider()
        self.assertTrue(a is a2)


class ThreadScopeTestCase(unittest.TestCase):
    
    def testThreadingScope(self):
        '''ThreadScope scope should create a thread-local provider.'''
        scope = ThreadScope()
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        a = scopedprovider()
        
        def run():
            a2 = scopedprovider()
            self.assertTrue(a is not a2)
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()


class RequestScopeTestCase(unittest.TestCase):

    def testRequestScope(self):
        '''RequestScope scope should create a request-local provider.'''
        scope = RequestScope()
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        
        scope.start()
        a = scopedprovider()
        a2 = scopedprovider()
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
        
        
        scope.start()
        a3 = scopedprovider()
        
        self.assertTrue(a is a2)
        self.assertTrue(a3 is not a)
        self.assertTrue(isinstance(a3, A))
    
    def testNoRequestStartedError(self):
        '''RequestScope-scoped provider should raise NoRequestStartedError.'''
        scope = RequestScope()
        def provider(): pass
        
        scopedprovider = scope.scope(provider)
        self.assertRaises(NoRequestStartedError, scopedprovider)
    
    def testStart(self):
        '''RequestScope start should affect only one thread.'''
        scope = RequestScope()
        def provider(): pass
        scopedprovider = scope.scope(provider)
        
        def run():
            self.assertRaises(NoRequestStartedError, scopedprovider)
        
        scope.start()
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
    
    def testEnd(self):
        '''RequestScope end should delete the instances cache.'''
        scope = RequestScope()
        class A(object): pass
        scopedprovider = scope.scope(A)
        
        scope.start()
        a = weakref.ref(scopedprovider())
        
        self.assertTrue(isinstance(a(), A))
        scope.end()
        
        self.assertTrue(a() is None)
    
    def testContextManager(self):
        '''RequestScope should support the context manager protocol.'''
        scope = RequestScope()
        class A(object): pass
        A = scope.scope(A)
        
        self.assertRaises(NoRequestStartedError, A)
        
        with scope:
            a = A()
            a2 = A()
        
        self.assertTrue(a is a2)
        self.assertRaises(NoRequestStartedError, A)
    
    def testMultipleRequests(self):
        '''RequestScope multiple requests test.'''
        scope = RequestScope()
        class A(object): pass
        A = scope.scope(A)
        
        self.assertRaises(NoRequestStartedError, A)
        
        with scope:
            a = A()
            a2 = A()
        
        with scope:
            a3 = A()
        
        with scope:
            a4 = A()
        
        self.assertTrue(a is a2)
        self.assertTrue(a3 is not a2)
        self.assertTrue(a4 is not a3)
        self.assertRaises(NoRequestStartedError, A)
