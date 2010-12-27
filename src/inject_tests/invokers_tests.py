import unittest

from inject.invokers import Invoker
from inject.injectors import Injector


class InvokerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testNew(self):
        '''Invoker should return an instance if an unbound method.'''
        class A(object):
            def method(self): pass 
        invoker = Invoker(A.method)
        self.assertTrue(isinstance(invoker, Invoker))
    
    def testNewNotUnboundMethod(self):
        '''Invoker should return an obj untouched if not an unbound method.'''
        def func():
            pass
        invoker = Invoker(func)
        self.assertTrue(invoker is func)
        
        class A(object):
            def method(self): pass
        
        a = A()
        invoker = Invoker(a.method)
        
        self.assertEqual(invoker, a.method)
    
    def testInvoke(self):
        '''Invoker should inject a class and call a method.'''
        class A(object):
            def method(self, arg):
                return 'arg: %s' % arg
        
        self.injector.bind(A, to=A)
        invoker = Invoker(A.method)
        
        result = invoker('value')
        self.assertEqual(result, 'arg: value')
    
    def testHash(self):
        '''Invoker should have the same hash an unbound method.'''
        class A(object):
            def method(self):
                pass
        
        invoker = Invoker(A.method)
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
        
        invoker = Invoker(A.method)
        self.assertEqual(invoker, A.method)
        self.assertNotEqual(invoker, A.method2)
