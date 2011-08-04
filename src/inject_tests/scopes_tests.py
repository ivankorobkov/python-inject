import threading
import unittest

from inject.scopes import NoRequestError, ApplicationScope, \
    RequestScope, ThreadScope


class A(object):
    
    pass


class ApplicationScopeTestCase(unittest.TestCase):
    
    def testBinding(self):
        s = ApplicationScope()
        
        a = A()
        s.bind(A, a)
        
        self.assertTrue(s.is_bound(A))
        self.assertTrue(s.get(A) is a)
    
    def testRebind(self):
        s = ApplicationScope()
        
        a = A()
        s.bind(A, a)
        self.assertTrue(s.get(A) is a)
        
        a2 = A()
        s.bind(A, a2)
        self.assertTrue(s.get(A) is a2)
    
    def testNoBinding(self):
        s = ApplicationScope()
        
        self.assertFalse(s.is_bound(A))
        self.assertTrue(s.get(A) is None)
    
    def testUnbind(self):
        s = ApplicationScope()
        
        a = A()
        s.bind(A, a)
        self.assertTrue(s.get(A) is a)
        
        s.unbind(A)
        self.assertFalse(s.is_bound(A))
        self.assertTrue(s.get(A) is None)
    
    def testContains(self):
        s = ApplicationScope()
        
        self.assertFalse(A in s)
        
        a = A()
        s.bind(A, a)
        self.assertTrue(A in s)


class ThreadScopeTestCase(ApplicationScopeTestCase):
    
    def testThreadLocal(self):
        s = ThreadScope()
        
        a = A()
        s.bind(A, a)
        
        def run():
            a2 = A()
            s.bind(A, a2)
            
            self.assertTrue(s.get(A) is a2)
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
        
        self.assertTrue(s.get(A) is a)


class RequestScopeTestCase(ApplicationScopeTestCase):

    def testRequestLocal(self):
        s = RequestScope()
        s.start()
        
        self.assertFalse(s.is_bound(A))
        a = A()
        s.bind(A, a)
        self.assertTrue(s.get(A) is a)
        
        def run():
            a2 = A()
            s.start()
            self.assertFalse(s.is_bound(A))
            s.bind(A, a2)
            self.assertTrue(s.get(A) is a2)
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
        
        self.assertTrue(s.is_bound(A))
        self.assertTrue(s.get(A) is a)
    
    def testRequestRequired(self):
        s = RequestScope()
        
        a = A()
        self.assertRaises(NoRequestError, s.bind, A, a)
        self.assertRaises(NoRequestError, s.unbind, A)
        self.assertRaises(NoRequestError, s.get, A)
        
        self.assertFalse(s.is_bound(A))
    
    def testContextManager(self):
        '''RequestScope should support the context manager protocol.'''
        s = RequestScope()
        self.assertRaises(NoRequestError, s.get, A)
        
        with s:
            a = A()
            s.bind(A, a)
            self.assertTrue(s.get(A) is a)
        
        self.assertRaises(NoRequestError, s.get, A)
        
        with s:
            self.assertTrue(s.get(A) is None)
