import unittest

from inject.providers import InstanceProvider, ProviderFactory


class InstanceProviderTestCase(unittest.TestCase):
    
    def test(self):
        '''InstanceProvider provider should always return the same value.'''
        obj = object()
        provider = InstanceProvider(obj)
        self.assertTrue(provider() is obj)
        self.assertTrue(provider() is obj)
    
    def testHash(self):
        '''InstanceProvider.__hash__ should be a delegate to instance's hash.'''
        class A(object): pass
        a = A()
        provider = InstanceProvider(a)
        self.assertEqual(hash(a), hash(provider))
        
        d = {}
        d[a] = True
        self.assertTrue(provider in d)
    
    def testEq(self):
        '''InstanceProvider.__eq__ should be a delegate for instance's eq.'''
        provider = InstanceProvider(123)
        self.assertEqual(provider, 123)
    
    def testNe(self):
        '''InstanceProivder.__ne__ should be a delegate for instance's ne.'''
        provider = InstanceProvider(123)
        self.assertNotEqual(provider, 321)


class ProvidersFactoryTestCase(unittest.TestCase):
    
    def testCallable(self):
        '''ProviderFactory should return untouched callables.'''
        def func(): pass
        provider = ProviderFactory(func)
        self.assertTrue(provider is func)
    
    def testUnboundMethod(self):
        '''ProviderFactory should return an invoker for an unbound method.'''
        class A(object):
            def method(self):
                pass
        provider = ProviderFactory(A.method)
        invoker_class = ProviderFactory.invoker_class
        self.assertTrue(isinstance(provider, invoker_class))
    
    def testInstance(self):
        '''ProviderFactory should return an instance provider.'''
        provider = ProviderFactory(123)
        self.assertTrue(isinstance(provider, ProviderFactory.instance_class))
