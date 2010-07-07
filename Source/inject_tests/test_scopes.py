import weakref
import unittest
import threading

from inject.scopes import NoRequestStartedError, AbstractScopeDecorator, \
    ApplicationScope, RequestScope, get_default_scope, set_default_scope, \
    clear_default_scopes, appscope, reqscope, NoScope, noscope


class DefaultScopesTestCase(unittest.TestCase):
    
    def tearDown(self):
        clear_default_scopes()
    
    def test_default_scopes(self):
        '''Test setting, getting and clearing the default scopes.'''
        class A(object): pass
        class Scope(object): pass
        
        self.assertTrue(get_default_scope(A) is None)
        
        set_default_scope(A, Scope)
        self.assertTrue(get_default_scope(A) is Scope)
        
        clear_default_scopes()
        self.assertTrue(get_default_scope(A) is None)


class AbstractDecoratorTestCase(unittest.TestCase):
    
    decorator_class = AbstractScopeDecorator
    
    def tearDown(self):
        clear_default_scopes()
    
    def test(self):
        '''AbstractScopeDecorator should call set_default_scope.'''
        class Scope(object): pass
        class MyDecorator(self.decorator_class):
            scope_class = Scope
        
        class A(object): pass
        A2 = MyDecorator(A)
        
        self.assertTrue(A2 is A)
        self.assertTrue(get_default_scope(A) is Scope)


class NoScopeTestCase(unittest.TestCase):
    
    scope_class = NoScope
    decorator_class = noscope
    
    def testDecorator(self):
        '''Noscope scope decorator should set the default scope.'''
        class A(object): pass
        A = self.decorator_class(A)
        
        self.assertTrue(get_default_scope(A) is self.scope_class)


class ApplicationScopeTestCase(unittest.TestCase):
    
    scope_class = ApplicationScope
    decorator_class = appscope
    
    def setUp(self):
        self.scope = self.scope_class()
    
    def tearDown(self):
        clear_default_scopes()
    
    def testScope(self):
        '''Application scope should create a cached scoped provider.'''
        scope = self.scope
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        a = scopedprovider()
        self.assertTrue(isinstance(a, A))
        
        a2 = scopedprovider()
        self.assertTrue(a is a2)
    
    def testDecorator(self):
        '''Application scope decorator should set the default scope.'''
        class A(object): pass
        A = self.decorator_class(A)
        
        self.assertTrue(get_default_scope(A) is self.scope_class)


class RequestScopTestCase(unittest.TestCase):
    
    scope_class = RequestScope
    decorator_class = reqscope
    
    def setUp(self):
        self.scope = self.scope_class()
    
    def tearDown(self):
        clear_default_scopes()

    def testDecorator(self):
        '''Request scope decorator should set the default scope.'''
        class A(object): pass
        A = self.decorator_class(A)
        
        self.assertTrue(get_default_scope(A) is self.scope_class)
    
    def testRequestScope(self):
        '''RequestScope scope should create a request-local provider.'''
        scope = self.scope
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
    
    def testThreadingScope(self):
        '''RequestScope scope should create a thread-local provider.'''
        scope = self.scope
        class A(object): pass
        
        scopedprovider = scope.scope(A)
        
        scope.start()
        a = scopedprovider()
        
        def run():
            scope.start()
            a2 = scopedprovider()
            self.assertTrue(a is not a2)
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
    
    def testProviderNoRequestRegistered(self):
        '''RequestScope-scoped provider should raise NoRequestStartedError.'''
        scope = self.scope
        def provider(): pass
        
        scopedprovider = scope.scope(provider)
        self.assertRaises(NoRequestStartedError, scopedprovider)
    
    def testThreadLocalRequestRegister(self):
        '''RequestScope start should affect only one thread.'''
        scope = self.scope
        def provider(): pass
        scopedprovider = scope.scope(provider)
        
        def run():
            self.assertRaises(NoRequestStartedError, scopedprovider)
        
        scope.start()
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()
    
    def testUnregister(self):
        '''RequestScope end should delete the instances cache.'''
        scope = self.scope
        class A(object): pass
        scopedprovider = scope.scope(A)
        
        scope.start()
        a = weakref.ref(scopedprovider())
        
        self.assertTrue(isinstance(a(), A))
        scope.end()
        
        self.assertTrue(a() is None)
