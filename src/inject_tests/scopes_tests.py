import threading
import unittest
import weakref

from inject.scopes import NoRequestStartedError, AbstractScopeDecorator, \
    ApplicationScope, RequestScope, get_default_scope, set_default_scope, \
    clear_default_scope, appscope, reqscope, NoScope, noscope, threadscope, \
    ThreadScope


class DefaultScopeTestCase(unittest.TestCase):
    
    def test_default_scope(self):
        '''Test setting/getting the default scopes.'''
        class A(object): pass
        class Scope(object): pass
        
        self.assertTrue(get_default_scope(A) is None)
        
        set_default_scope(A, Scope)
        self.assertTrue(get_default_scope(A) is Scope)
    
    def test_cant_set_attr(self):
        '''Test getting/setting default scopes for objects which cannot have attrs.'''
        s = [1, 2, 3]
        
        # No error
        get_default_scope(s)
        
        self.assertRaises(AttributeError, set_default_scope, s, None)
    
    def test_clear_default_scope(self):
        '''Test clearing the default scopes.'''
        class A(object): pass
        class Scope(object): pass
        
        self.assertTrue(get_default_scope(A) is None)
        
        clear_default_scope(A)
        self.assertTrue(get_default_scope(A) is None)
        
        set_default_scope(A, Scope)
        self.assertTrue(get_default_scope(A) is Scope)
        
        clear_default_scope(A)
        self.assertTrue(get_default_scope(A) is None)
    
    def test_inheritance(self):
        '''Test default scope inheritance.'''
        class A(object): pass
        class A2(A): pass
        class Scope(object): pass
        class Scope2(object): pass
        
        self.assertTrue(get_default_scope(A) is None)
        
        set_default_scope(A, Scope)
        self.assertTrue(get_default_scope(A) is Scope)
        self.assertTrue(get_default_scope(A2) is Scope)
        
        set_default_scope(A2, Scope2)
        self.assertTrue(get_default_scope(A) is Scope)
        self.assertTrue(get_default_scope(A2) is Scope2)


class AbstractDecoratorTestCase(unittest.TestCase):
    
    def test(self):
        '''AbstractScopeDecorator should call set_default_scope.'''
        class Scope(object): pass
        class MyDecorator(AbstractScopeDecorator):
            scope_class = Scope
        
        class A(object): pass
        A2 = MyDecorator(A)
        
        self.assertTrue(A2 is A)
        self.assertTrue(get_default_scope(A) is Scope)


class NoScopeTestCase(unittest.TestCase):
    
    def testScope(self):
        '''NoScope should return the provider untouched.'''
        class A(object): pass
        scope = NoScope()
        
        A2 = scope.scope(A)
        self.assertTrue(A is A2)
    
    def testDecorator(self):
        '''noscope decorator should set the default scope.'''
        class A(object): pass
        A = noscope(A)
        
        self.assertTrue(get_default_scope(A) is NoScope)


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
    
    def testDecorator(self):
        '''appscope decorator should set the default scope.'''
        class A(object): pass
        A = appscope(A)
        
        self.assertTrue(get_default_scope(A) is ApplicationScope)


class ThreadScopeTestCase(unittest.TestCase):
    
    def testDecorator(self):
        '''threadscope decorator should set the default scope.'''
        class A(object): pass
        A = threadscope(A)
        
        self.assertTrue(get_default_scope(A) is ThreadScope)
    
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

    def testDecorator(self):
        '''reqscope decorator should set the default scope.'''
        class A(object): pass
        A = reqscope(A)
        
        self.assertTrue(get_default_scope(A) is RequestScope)
    
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
        scope = RequestScope()
        def provider(): pass
        
        raise NotImplementedError()
