import unittest

from inject.injections import InjectionPoint, AttributeInjection, \
    ParamInjection, NoParamError, NamedAttributeInjection, \
    ClassAttributeInjection
from inject.injectors import Injector


class InjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testGetInstance(self):
        '''InjectionPoint should call injector's get_instance method.'''
        class A(object): pass
        
        a = A()
        self.injector.bind(A, to=a)
        
        injection_point = InjectionPoint(A)
        a2 = injection_point.get_instance()
        
        self.assertTrue(a2 is a)


class AttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''AttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A)
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        self.assertTrue(b.a is a)
    
    def testInheritance(self):
        '''AttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A)
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
            a = AttributeInjection(A)
        
        a = A()
        self.injector.bind(A, a)
        
        b = B()
        self.assertTrue(b.a is a)
        
        a2 = A()
        self.injector.bind(A, a2)
        
        # It is still a, not a2.
        self.assertTrue(b.a is a)
    
    def testReinjecting(self):
        '''AttributeInjection should support reinjecting dependencies.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A, reinject=True)
        
        a = A()
        self.injector.bind(A, a)
        
        b = B()
        self.assertTrue(b.a is a)
        self.assertTrue(b.a is a) # Multiple accesses.
        
        a2 = A()
        self.injector.bind(A, a2)
        self.assertTrue(b.a is a2)


class NamedAttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''NamedAttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A)
        
        a = A()
        self.injector.bind(A, to=a)
        
        b = B()
        self.assertTrue(b.a is a)
    
    def testInheritance(self):
        '''NamedAttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A)
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
            a = NamedAttributeInjection('a', A)
        
        a = A()
        self.injector.bind(A, a)
        
        b = B()
        self.assertTrue(b.a is a)
        
        a2 = A()
        self.injector.bind(A, a2)
        
        # It is still a, not a2.
        self.assertTrue(b.a is a)

    def testReinjecting(self):
        '''NamedAttributeInjection should support reinjecting dependencies.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A, reinject=True)
        
        a = A()
        self.injector.bind(A, a)
        
        b = B()
        self.assertTrue(b.a is a)
        self.assertTrue(b.a is a) # Multiple accesses.
        
        a2 = A()
        self.injector.bind(A, a2)
        self.assertTrue(b.a is a2)


class ClassAttributeInjectionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''ClassAttributeInjection should resolve a dependency on every access.'''
        class A(object): pass
        class B(object):
            a = ClassAttributeInjection(A)
        
        a = A()
        self.injector.bind(A, a)
        self.assertTrue(B.a is a)
        
        a2 = A()
        self.injector.bind(A, a2)
        self.assertTrue(B.a is a2)


class ParamTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testInjection(self):
        '''ParamInjection should inject dependencies as kwargs.'''
        class A(object): pass
        a = A()
        self.injector.bind(A, a)
        
        @ParamInjection('a', A)
        def func(a):
            return a
        
        self.assertTrue(func() is a)
    
    def testInjectionNoType(self):
        '''ParamInjection should use name as type when type is not given.'''
        class A(object): pass
        a = A()
        self.injector.bind('a', a)
        
        @ParamInjection('a')
        def func(a):
            return a
        
        a2 = func()
        self.assertTrue(a2 is a)
    
    def testMultipleInjection(self):
        '''Multiple ParamInjection injections should be combined into one.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        self.injector.bind(A, a)
        self.injector.bind(B, b)
        
        @ParamInjection('a', A)
        @ParamInjection('b', B)
        def func(b, a):
            return b, a
        
        b2, a2 = func()
        
        self.assertTrue(b2 is b)
        self.assertTrue(a2 is a)
    
    def testInjectNonGivenParams(self):
        '''ParamInjection should injection only non-given dependencies.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        self.injector.bind(A, a)
        self.injector.bind(B, b)
        
        @ParamInjection('a', A)
        @ParamInjection('b', B)
        def func(a, b):
            return a, b
        
        a2, b2 = func(b='b')
        self.assertTrue(a2 is a)
        self.assertEqual(b2, 'b')
    
    def testCreateWrapper(self):
        '''Create wrapper should return a func with set attributes.'''
        def func(): pass
        wrapper = ParamInjection.create_wrapper(func)
        
        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.injections, {})
        self.assertTrue(wrapper.injection_wrapper)
    
    def testAddInjection(self):
        '''Add injection should add an injection to the injections dict.'''
        def func(arg): pass
        wrapper = ParamInjection.create_wrapper(func)
        
        ParamInjection.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionNoParamError(self):
        '''Should raise NoParamError when the func does not take an injected param.'''
        def func(): pass
        
        wrapper = ParamInjection.create_wrapper(func)
        self.assertRaises(NoParamError,
                          ParamInjection.add_injection,
                          wrapper, 'arg2', 'inj')
    
    def testAddInjectionArgs(self):
        '''Add injection should not raise NoParamError, when *args given.'''
        def func2(*args): pass
        
        wrapper = ParamInjection.create_wrapper(func2)
        ParamInjection.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionKwargs(self):
        '''Add injection should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass
        
        wrapper = ParamInjection.create_wrapper(func3)
        ParamInjection.add_injection(wrapper, 'kwarg', 'inj')
        self.assertEqual(wrapper.injections['kwarg'], 'inj')
