import unittest

from inject import injections, errors


class AttrTestCase(unittest.TestCase):
    
    attr_class = injections.Attr
    
    def test(self):
        '''Attribute injection should create an instance and set an Attr.'''
        class A(object): pass
        class B(object):
            a = self.attr_class('a', A)
        
        b = B()
        a = b.a
        a2 = b.a
        
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
        
        # Test inheritance.
        class C(B): pass
        
        c = C()
        a = c.a
        a2 = c.a
        self.assertTrue(isinstance(a, A))
        self.assertTrue(a is a2)
    
    def testNoType(self):
        '''Attribute injection should use attr as type if type is not given.'''
        class A(object):
            attr = self.attr_class('attr')
        
        a = A()
        self.assertEqual(A.attr.injection.key, 'attr')
        self.assertRaises(errors.NoProviderError, getattr, a, 'attr')


class ParamTestCase(unittest.TestCase):
    
    param_class = injections.Param
    
    def testInjection(self):
        '''Param injection should inject non-existing params into a func.'''
        class A(object): pass
        
        @self.param_class('a', A)
        def func(a, b):
            return a, b
        
        a, b = func(b='b')
        self.assertTrue(isinstance(a, A))
        self.assertEqual(b, 'b')
        
        a, b = func(a='a', b='b')
        self.assertEqual(a, 'a')
        self.assertEqual(b, 'b')
    
    def testMultipleInjection(self):
        '''Multiple Param injections should be combined into one.'''
        class A(object): pass
        class B(object): pass
        
        class C(object):
            @self.param_class('a', A)
            @self.param_class('b', B)
            def __init__(self, a, b):
                self.a = a
                self.b = b
        
        c = C()
        self.assertTrue(isinstance(c.a, A))
        self.assertTrue(isinstance(c.b, B))
    
    def testNoType(self):
        '''Param injection should use name as type if type is not given.'''
        @self.param_class('a')
        def func(a):
            pass
        
        self.assertEqual(func.injections['a'].key, 'a')
        self.assertRaises(errors.NoProviderError, func)
    
    def testCreateWrapper(self):
        '''Create wrapper() should return a func with set attrs.'''
        def func(): pass
        wrapper = self.param_class.create_wrapper(func)
        
        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.injections, {})
        self.assertTrue(wrapper.injection_wrapper)
    
    def testAddInjection(self):
        '''Add injection() should add an inj to injections dict.'''
        def func(arg): pass
        wrapper = self.param_class.create_wrapper(func)
        
        # Noraml injection.
        self.param_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionNoParamError(self):
        '''Add injection() should raise NoParamError when no such a Param.'''
        # NoParamError.
        def func(): pass
        wrapper = self.param_class.create_wrapper(func)
        self.assertRaises(errors.NoParamError, self.param_class.add_injection,
                          wrapper, 'arg2', 'inj')
        
    
    def testAddInjectionArgs(self):
        '''Add injection() should not raise NoParamError, when *args,'''
        def func2(*args): pass
        wrapper = self.param_class.create_wrapper(func2)
        self.param_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
        
    def testAddInjectionKwargs(self):
        '''Add injection() should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass
        wrapper = self.param_class.create_wrapper(func3)
        self.param_class.add_injection(wrapper, 'kwarg', 'inj')
        self.assertEqual(wrapper.injections['kwarg'], 'inj')