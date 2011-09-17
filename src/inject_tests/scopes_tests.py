import threading
import unittest

from inject.scopes import NoRequestError, ApplicationScope, \
    NoScope, RequestScope, ThreadScope
from inject.exc import FactoryNotCallable


class A(object):
    
    pass


class ApplicationScopeTestCase(unittest.TestCase):
    
    def new_scope(self):
        return ApplicationScope()
    
    def testBinding(self):
        s = self.new_scope()
        
        a = A()
        s.bind(A, a)
        
        self.assertTrue(s.is_bound(A))
        self.assertTrue(s.get(A) is a)
    
    def testRebind(self):
        s = self.new_scope()
        
        a = A()
        s.bind(A, a)
        self.assertTrue(s.get(A) is a)
        
        a2 = A()
        s.bind(A, a2)
        self.assertTrue(s.get(A) is a2)
    
    def testNoBinding(self):
        s = self.new_scope()
        
        self.assertFalse(s.is_bound(A))
        self.assertTrue(s.get(A) is None)
    
    def testUnbind(self):
        s = self.new_scope()
        
        a = A()
        s.bind(A, a)
        self.assertTrue(s.get(A) is a)
        
        s.unbind(A)
        self.assertFalse(s.is_bound(A))
        self.assertTrue(s.get(A) is None)
    
    def testContains(self):
        s = self.new_scope()
        
        self.assertFalse(A in s)
        
        a = A()
        s.bind(A, a)
        self.assertTrue(A in s)
    
    def testBindFactory(self):
        s = self.new_scope()
        
        s.bind_factory(A, A)
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        a = s.get(A)
        self.assertTrue(isinstance(a, A))
        self.assertTrue(s.is_bound(A))
        
        a2 = s.get(A)
        self.assertTrue(a2 is a)
    
    def testBindFactoryNotCallable(self):
        s = self.new_scope()
        self.assertRaises(FactoryNotCallable, s.bind_factory, 'some_key',
                          'not_callable')
    
    def testUnbindFactory(self):
        s = self.new_scope()
        
        s.bind_factory(A, A)
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        s.get(A)
        self.assertTrue(s.is_bound(A))
        
        s.unbind_factory(A)
        self.assertFalse(s.is_factory_bound(A))
        self.assertTrue(s.is_bound(A))


class NoScopeTestCase(ApplicationScopeTestCase):
    
    def new_scope(self):
        return NoScope()
    
    def testBindFactory(self):
        s = self.new_scope()
        
        s.bind_factory(A, A)
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        a = s.get(A)
        self.assertTrue(isinstance(a, A))
        self.assertFalse(s.is_bound(A))
        
        a2 = s.get(A)
        self.assertTrue(a2 is not a)
    
    def testUnbindFactory(self):
        s = self.new_scope()
        
        s.bind_factory(A, A)
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        s.get(A)
        self.assertFalse(s.is_bound(A))
        
        s.unbind_factory(A)
        self.assertFalse(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))


class ThreadScopeTestCase(ApplicationScopeTestCase):
    
    def new_scope(self):
        return ThreadScope()
    
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
    
    def new_scope(self):
        s = RequestScope()
        s.start();
        return s

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
    
    def testRequestLocalAndFactories(self):
        s = RequestScope()
        s.start()
        
        s.bind_factory(A, A)
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        a = s.get(A)
        self.assertTrue(s.is_bound(A))
        
        s.end()
        self.assertTrue(s.is_factory_bound(A))
        self.assertFalse(s.is_bound(A))
        
        s.start()
        a2 = s.get(A)
        self.assertFalse(a2 is a)
        s.end()
    
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
