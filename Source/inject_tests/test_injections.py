import unittest
from mock import Mock

from inject.injections import AttributeInjection, ParamInjection, NoParamError, \
    NamedAttributeInjection
from inject.injectors import Injector


class AttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
        self.injection_class = AttributeInjection
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''AttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = self.injection_class(A)
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        self.assertTrue(b.a is a)
    
    def testInheritance(self):
        '''AttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = self.injection_class(A)
        class C(B): pass
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        c = C()
        self.assertTrue(b.a is a)
        self.assertTrue(c.a is a)
    
    def testSettingAttr(self):
        '''AttributeInjection should set an attribute of an object.'''
        class A(object): pass
        class B(object):
            a = self.injection_class(A)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        self.assertTrue(isinstance(b.a, A))
        self.assertTrue(a is a2)
    
    def testReinjecting(self):
        '''AttributeInjection should support reinjecting dependencies.'''
        class A(object):
            i = 0
            def __init__(self):
                self.__class__.i += 1
                self.i = self.__class__.i
        
        class B(object):
            a = self.injection_class(A, reinject=True)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        
        self.assertFalse(a is a2)
        self.assertEqual(a.i, 1)
        self.assertEqual(a2.i, 2)


class NamedAttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
        self.injection_class = NamedAttributeInjection
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''NamedAttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        self.assertTrue(b.a is a)
    
    def testInheritance(self):
        '''NamedAttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        class C(B): pass
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        c = C()
        self.assertTrue(b.a is a)
        self.assertTrue(c.a is a)
    
    def testSettingAttr(self):
        '''NamedAttributeInjection should set an attribute of an object.'''
        class A(object): pass
        class B(object):
            a = self.injection_class('a', A)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        self.assertTrue(isinstance(b.a, A))
        self.assertTrue(a is a2)

    def testReinjecting(self):
        '''NamedAttributeInjection should support reinjecting dependencies.'''
        class A(object):
            i = 0
            def __init__(self):
                self.__class__.i += 1
                self.i = self.__class__.i
        
        class B(object):
            a = self.injection_class('a', A, reinject=True)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        
        self.assertFalse(a is a2)
        self.assertEqual(a.i, 1)
        self.assertEqual(a2.i, 2)


class ParamTestCase(unittest.TestCase):
    
    def setUp(self):
        class DummyParamInjection(ParamInjection):
            point_class = Mock()
        
        self.injection_class = DummyParamInjection
    
    def testInjection(self):
        '''ParamInjection should inject dependencies as kwargs.'''
        class A(object): pass
        a = A()
        
        @self.injection_class('a', A)
        def func(a):
            return a
        
        func.injections['a'].get_instance.return_value = a
        
        self.assertTrue(func() is a)
    
    def testMultipleInjection(self):
        '''Multiple ParamInjection injections should be combined into one.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        
        @self.injection_class('a', A)
        @self.injection_class('b', B)
        def func(b, a):
            return b, a
        
        injections = func.injections
        injections['a'] = Mock()
        injections['b'] = Mock()
        injections['a'].get_instance.return_value = a
        injections['b'].get_instance.return_value = b
        
        b2, a2 = func()
        
        self.assertTrue(b2 is b)
        self.assertTrue(a2 is a)
    
    def testInjectNonGivenParams(self):
        '''ParamInjection should injection only non-given dependencies.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        
        @self.injection_class('a', A)
        @self.injection_class('b', B)
        def func(a, b):
            return a, b
        
        injections = func.injections
        injections['a'] = Mock()
        injections['b'] = Mock()
        injections['a'].get_instance.return_value = a
        injections['b'].get_instance.return_value = b
        
        a2, b2 = func(b='b')
        self.assertTrue(a2 is a)
        self.assertEqual(b2, 'b')
    
    def testCreateWrapper(self):
        '''Create wrapper should return a func with set attrs.'''
        def func(): pass
        wrapper = self.injection_class.create_wrapper(func)
        
        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.injections, {})
        self.assertTrue(wrapper.injection_wrapper)
    
    def testAddInjection(self):
        '''Add injection should add an inj to injections dict.'''
        def func(arg): pass
        wrapper = self.injection_class.create_wrapper(func)
        
        self.injection_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionNoParamError(self):
        '''Add injection should raise NoParamError when no such a param.'''
        def func(): pass
        
        wrapper = self.injection_class.create_wrapper(func)
        self.assertRaises(NoParamError,
                          self.injection_class.add_injection,
                          wrapper, 'arg2', 'inj')
    
    def testAddInjectionArgs(self):
        '''Add injection should not raise NoParamError, when *args given.'''
        def func2(*args): pass
        
        wrapper = self.injection_class.create_wrapper(func2)
        self.injection_class.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionKwargs(self):
        '''Add injection should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass
        
        wrapper = self.injection_class.create_wrapper(func3)
        self.injection_class.add_injection(wrapper, 'kwarg', 'inj')
        self.assertEqual(wrapper.injections['kwarg'], 'inj')
