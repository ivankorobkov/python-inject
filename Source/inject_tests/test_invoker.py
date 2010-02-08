from inject import scopes
import unittest

from inject.invoker_ import Invoker


class InvokerTestCase(unittest.TestCase):
    
    invoker_class = Invoker
    
    def testNew(self):
        '''Invoker() should return an instance if an unbound method.'''
        class A(object):
            def method(self): pass 
        invoker = self.invoker_class(A.method)
        self.assertTrue(isinstance(invoker, self.invoker_class))
    
    def testNewNotUnboundMethod(self):
        '''Invoker() should return an obj untouched if not an unbound method.
        '''
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
        '''Invoker.__call__() should inject a class and call a method.'''
        class A(object):
            def method(self, arg):
                return 'arg: %s' % arg
        invoker = self.invoker_class(A.method)
        result = invoker('value')
        self.assertEqual(result, 'arg: value')
    
    def testInvokeScope(self):
        '''Invoker.__call__() should inject a class using a provided scope.'''
        class A(object):
            i = 0
            def __init__(self):
                self.__class__.i += 1
            def method(self):
                return self.i
        invoker = self.invoker_class(A.method, scope=scopes.app)
        result1 = invoker()
        result2 = invoker()
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 1)
        scopes.app.clear()
    
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