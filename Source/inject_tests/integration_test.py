import unittest

import inject
from inject import errors, appscope, noscope


class A(object): pass
class B(object): pass
class C(object): pass
class D(object): pass
class E(object): pass

class A2(object): pass
class B2(object): pass
class C2(object): pass
class D2(object): pass
class E2(object): pass
E2 = appscope(E2)


class MyAttr(object):
    a = inject.attr('a', A)
    b = inject.attr('b', B, annotation='my')
    c = appscope.inject_attr('c', C, annotation='my', bindto=C2)
    d = inject.attr('d', D, scope=appscope)
    e = inject.attr('e')


class MyParam(object):
    
    @inject.param('a', A)
    @inject.param('b', B, annotation='my')
    @appscope.inject_param('c', C, annotation='my', bindto=C2)
    @inject.param('d', D, scope=appscope)
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d


class MyParam2(MyParam):
    
    @inject.param('e')
    def __init__(self, e, a=inject.super, b=inject.super, c=inject.super,
                 d=inject.super):
        super(MyParam2, self).__init__(a=a, b=b, c=c, d=d)
        self.e = e


class InjectionsTestCase(unittest.TestCase):
    
    def testAttr(self):
        '''Attribute injection integration test.'''
        my = MyAttr()
        a = my.a
        b = my.b
        c = my.c
        d = my.d
        # e = my.e
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(isinstance(b, B))
        self.assertTrue(isinstance(c, C2))
        self.assertTrue(isinstance(d, D))
        self.assertRaises(errors.NoProviderError, getattr, my, 'e')
        
        my2 = MyAttr()
        a2 = my2.a
        b2 = my2.b
        c2 = my2.c
        d2 = my2.d
        
        self.assertTrue(isinstance(a2, A) and a2 is not a)
        self.assertTrue(isinstance(b2, B) and b2 is not b)
        self.assertTrue(isinstance(c2, C2) and c2 is c)
        self.assertTrue(isinstance(d2, D) and d2 is d)
    
    def testParam(self):
        '''Param injection integration test.'''
        my = MyParam()
        a = my.a
        b = my.b
        c = my.c
        d = my.d
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(isinstance(b, B))
        self.assertTrue(isinstance(c, C2))
        
        self.assertRaises(errors.NoProviderError, MyParam2)
        
        my2 = MyParam2(e='my e')
        a2 = my2.a
        b2 = my2.b
        c2 = my2.c
        d2 = my2.d
        e2 = my2.e
        
        self.assertTrue(isinstance(a2, A) and a2 is not a)
        self.assertTrue(isinstance(b2, B) and b2 is not b)
        self.assertTrue(isinstance(c2, C2) and c2 is c)
        self.assertTrue(isinstance(d2, D) and d2 is d)
        self.assertEqual(e2, 'my e')


class InjectorTestCase(unittest.TestCase):
    
    def setUp(self):
        injector = inject.Injector()
        injector.bind(A, to=A2, scope=appscope)
        injector.bind(B, 'my', to=B2, scope=appscope)
        injector.bind(C, to=C2, scope=noscope)
        injector.bind(D, 'my', to=D2) # The default must be used.
        injector.bind('e', to=E2)
        inject.register(injector)
        
        self.injector = injector
    
    def tearDown(self):
        inject.unregister()
    
    def testAttrs(self):
        '''Injector integration test with attributes.'''
        my = MyAttr()
        a = my.a
        b = my.b
        c = my.c
        d = my.d
        e = my.e
        
        self.assertTrue(isinstance(a, A2))
        self.assertTrue(isinstance(b, B2))
        self.assertTrue(isinstance(c, C2))
        self.assertTrue(isinstance(d, D))  # The default must be used.
        self.assertTrue(isinstance(e, E2))
        
        my2 = MyAttr()
        a2 = my2.a
        b2 = my2.b
        c2 = my2.c
        d2 = my2.d
        e2 = my2.e
        
        self.assertTrue(isinstance(a2, A2) and a2 is a)
        self.assertTrue(isinstance(b2, B2) and b2 is b)
        self.assertTrue(isinstance(c2, C2) and c2 is not c)
        self.assertTrue(isinstance(d2, D) and d2 is d)
        self.assertTrue(isinstance(e2, E2) and e2 is e)