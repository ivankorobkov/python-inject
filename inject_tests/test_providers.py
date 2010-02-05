import unittest

from inject import providers, errors, scopes


class InstanceTestCase(unittest.TestCase):
    
    provider_class = providers.Instance
    
    def test(self):
        '''Instance provider should always return the same value.'''
        obj = object()
        provider = self.provider_class(obj)
        self.assertTrue(provider() is obj)
        self.assertTrue(provider() is obj)


class FactoryTestCase(unittest.TestCase):
    
    factory_class = providers.Factory
    
    def testCallable(self):
        '''Factory should return untouched callables if not an unbound methods.
        '''
        def func(): pass
        provider = self.factory_class(func)
        self.assertTrue(provider is func)
    
    def testUnboundMethod(self):
        '''Factory should return an invoker for an unbound method.'''
        class A(object):
            def method(self):
                pass
        
        provider = self.factory_class(A.method)
        self.assertTrue(isinstance(provider, 
                                   self.factory_class.invoker_class))
    
    def testScopeCallable(self):
        '''Factory should scope any callable if scope is given.'''
        class A(object): pass
        provider = self.factory_class(A, scope=scopes.app)
        self.assertTrue(provider is not A)
        self.assertTrue(isinstance(provider(), A))
        
        scopes.app.clear()
    
    def testScopeFromSCOPE_ATTR(self):
        '''Factory should use SCOPE_ATTR if it exists and scope=None.'''
        class A(object): pass
        @scopes.app
        def func(): return A()
        
        provider = self.factory_class(func)
        self.assertTrue(provider is not func)
        
        a = provider()
        a2 = provider()
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
    
    def testScopeDontUseSCOPE_ATTR(self):
        '''Factory should not use SCOPE_ATTR if scope is given.'''
        class A(object): pass
        @scopes.app
        def func(): return A()
        
        provider = self.factory_class(func, scope=scopes.no)
        self.assertTrue(provider is func)
        
        a = provider()
        a2 = provider()
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is not a2)
    
    def testDonotScopeWhenNoScope(self):
        '''Factory should not scope a callable if scope is noscope.'''
        class A(object): pass
        provider = self.factory_class(A, scope=scopes.no)
        self.assertTrue(provider is A)
    
    def testInstance(self):
        '''Factory should return an instance provider.'''
        provider = self.factory_class(123)
        self.assertTrue(isinstance(provider, 
                                   self.factory_class.instance_class))
    
    def testInstanceCantBeScopedError(self):
        '''Factory should raise CantBeScopedError for an instance provider.'''
        self.assertRaises(errors.CantBeScopedError, self.factory_class,
                          123, scope=scopes.app)
    
    def testInstanceNoScope(self):
        '''Factory should not raise CantBeScopedError for an inst with noscope.
        '''
        provider = self.factory_class(123, scope=scopes.no)
        self.assertTrue(isinstance(provider, 
                                   self.factory_class.instance_class))