import unittest
from mock import Mock

from inject.invokers import Invoker


class InvokerTestCase(unittest.TestCase):
    
    def setUp(self):
        class DummyInvoker(Invoker):
            injection_class = Mock()
        
        self.invoker_class = DummyInvoker
    
    def testNew(self):
        '''Invoker should return an instance if an unbound method.'''
        class A(object):
            def method(self): pass 
        invoker = self.invoker_class(A.method)
        self.assertTrue(isinstance(invoker, self.invoker_class))
    
    def testNewNotUnboundMethod(self):
        '''Invoker should return an obj untouched if not an unbound method.'''
        def func():
            pass
        invoker = self.invoker_class(func)
        self.assertTrue(invoker is func)
        
        class A(object):
            def method(self): pass
        
        a = A()
        invoker = self.invoker_class(a.method)
        
        self.assertEqual(invoker, a.method)
    
    def testInvoke(self):
        '''Invoker should inject a class and call a method.'''
        class A(object):
            def method(self, arg):
                return 'arg: %s' % arg
        
        a = A()
        invoker = self.invoker_class(A.method)
        invoker.injection.get_instance.return_value = a
        
        result = invoker('value')
        self.assertEqual(result, 'arg: value')
        
    def testHash(self):
        '''Invoker should have the same hash an unbound method.'''
        class A(object):
            def method(self):
                pass
        
        invoker = self.invoker_class(A.method)
        self.assertEqual(hash(invoker), hash(A.method))
        
        d = {}
        d[A.method] = 'value'
        self.assertEqual(d[invoker], 'value')
    
    def testEqNe(self):
        '''Invoker should be equal to an unbound method.'''
        class A(object):
            def method(self):
                pass
            def method2(self):
                pass
        
        invoker = self.invoker_class(A.method)
        self.assertEqual(invoker, A.method)
        self.assertNotEqual(invoker, A.method2)
