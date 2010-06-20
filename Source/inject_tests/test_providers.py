import unittest

from inject.scopes import app as appscope, no as noscope
from inject.errors import CantBeScopedError, CantCreateProviderError
from inject.providers import Instance, Factory


class InstanceTestCase(unittest.TestCase):
    
    provider_class = Instance
    
    def test(self):
        '''Instance provider should always return the same value.'''
        obj = object()
        provider = self.provider_class(obj)
        self.assertTrue(provider() is obj)
        self.assertTrue(provider() is obj)


class FactoryTestCase(unittest.TestCase):
    
    factory_class = Factory
    
    def testCallable(self):
        '''Factory should return untouched callables if not an unbound methods.
        '''
        def func(): pass
        provider = self.factory_class(func, to=func)
        self.assertTrue(provider is func)
    
    def testUnboundMethod(self):
        '''Factory should return an invoker for an unbound method.'''
        class A(object):
            def method(self):
                pass
        
        provider = self.factory_class(A.method, to=A.method)
        self.assertTrue(isinstance(provider,
                                   self.factory_class.invoker_class))
    
    def testScopeCallable(self):
        '''Factory should scope any callable if scope is given.'''
        class Scope(object):
            def __init__(self, provider):
                self.provider = provider
            
            @classmethod
            def scope(cls, provider):
                return cls(provider)
        
        class A(object): pass
        scoped_provider = self.factory_class(A, to=A, scope=Scope)
        self.assertTrue(scoped_provider is not A)
        self.assertTrue(scoped_provider.provider is A)
    
    def testScopeFromSCOPE_ATTR(self):
        '''Factory should use SCOPE_ATTR if it exists and scope=None.'''
        class A(object): pass
        @appscope
        def func(): return A()
        
        provider = self.factory_class(func, to=func)
        self.assertTrue(provider is not func)
        
        a = provider()
        a2 = provider()
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
    
    def testScopeDontUseSCOPE_ATTR(self):
        '''Factory should not use SCOPE_ATTR if scope is given.'''
        class A(object): pass
        @appscope
        def func(): return A()
        
        provider = self.factory_class(func, to=func, scope=noscope)
        self.assertTrue(provider is func)
        
        a = provider()
        a2 = provider()
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is not a2)
    
    def testDonotScopeWhenNoScope(self):
        '''Factory should not scope a callable if scope is noscope.'''
        class A(object): pass
        provider = self.factory_class(A, to=A, scope=noscope)
        self.assertTrue(provider is A)
    
    def testInstance(self):
        '''Factory should return an instance provider.'''
        provider = self.factory_class(123, to=123)
        self.assertTrue(isinstance(provider,
                                   self.factory_class.instance_class))
    
    def testInstanceCantCreateProviderError(self):
        '''Factory should raise an error when no to, type is not callable.'''
        self.assertRaises(CantCreateProviderError, self.factory_class,
                          123)
    
    def testInstanceCantBeScopedError(self):
        '''Factory should raise CantBeScopedError for an instance provider.'''
        self.assertRaises(CantBeScopedError, self.factory_class, 123, to=123,
                          scope=appscope)
    
    def testInstanceNoScope(self):
        '''Factory should not raise CantBeScopedError for an inst with noscope.
        '''
        provider = self.factory_class(123, to=123, scope=noscope)
        self.assertTrue(isinstance(provider,
                                   self.factory_class.instance_class))
