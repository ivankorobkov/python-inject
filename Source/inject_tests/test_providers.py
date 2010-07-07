import unittest

from inject.providers import InstanceProvider, ProvidersFactory, \
    CantCreateProviderError


class InstanceProviderTestCase(unittest.TestCase):
    
    provider_class = InstanceProvider
    
    def test(self):
        '''InstanceProvider provider should always return the same value.'''
        obj = object()
        provider = self.provider_class('notype', obj)
        self.assertTrue(provider() is obj)
        self.assertTrue(provider() is obj)


class ProvidersFactoryTestCase(unittest.TestCase):
    
    factory_class = ProvidersFactory
    
    def testCallable(self):
        '''ProvidersFactory should return untouched callables.'''
        def func(): pass
        provider = self.factory_class(func, to=func)
        self.assertTrue(provider is func)
    
    def testUnboundMethod(self):
        '''ProvidersFactory should return an invoker for an unbound method.'''
        class A(object):
            def method(self):
                pass
        provider = self.factory_class(A.method, to=A.method)
        invoker_class = self.factory_class.invoker_class
        self.assertTrue(isinstance(provider, invoker_class))
    
    def testInstance(self):
        '''ProvidersFactory should return an instance provider.'''
        provider = self.factory_class(123, to=123)
        self.assertTrue(isinstance(provider,
                                   self.factory_class.instance_class))
    
    def testInstanceCantCreateProviderError(self):
        '''ProvidersFactory should raise CantCreateProviderError.'''
        self.assertRaises(CantCreateProviderError, self.factory_class, 123)
