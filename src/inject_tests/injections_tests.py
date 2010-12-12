import unittest

from inject.injections import InjectionPoint, NoInjectorRegistered, \
    AttributeInjection, ParamInjection, NoParamError, NamedAttributeInjection, \
    ClassAttributeInjection
from inject.injectors import Injector


class InjectionTestCase(unittest.TestCase):
    
    def testGetInstance(self):
        '''InjectionPoint should call injector's get_instance method.'''
        class A(object): pass
        class B(object): pass
        
        my_injector = Injector()
        my_injector.bind(A, to=B)
        
        class MyPoint(InjectionPoint):
            injector = my_injector
        
        injection_point = MyPoint(A)
        a = injection_point.get_instance()
        
        self.assertTrue(isinstance(a, B))
    
    def testNoInjectorRegistered(self):
        '''InjectionPoint should raise NoInjectorRegistered.'''
        class A(object): pass
        
        injection_point = InjectionPoint(A)
        
        self.assertRaises(NoInjectorRegistered, injection_point.get_instance)


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
            a = AttributeInjection(A, reinject=True)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        
        self.assertFalse(a is a2)
        self.assertEqual(a.i, 1)
        self.assertEqual(a2.i, 2)
    
    def testReinjectingTypeError(self):
        '''AttributeInjection should raise TypeError for wrong reinject type.'''
        class A(object): pass
        
        self.assertRaises(TypeError, AttributeInjection, A, reinject=A)
        self.assertRaises(TypeError, AttributeInjection, A, reinject=None)
        
        attr = AttributeInjection(A, True) #@UnusedVariable
        attr2 = AttributeInjection(A, False) #@UnusedVariable
    
    def testLazyImport(self):
        '''AttributeInjection lazy imports.'''
        from inject_tests.fixtures.cyclic1 import A, A2
        from inject_tests.fixtures.cyclic2 import B
        
        a = A()
        a2 = A2()
        b = B()
        
        self.assertTrue(isinstance(a.b, B))
        self.assertTrue(isinstance(a2.b, B))
        self.assertTrue(isinstance(b.a, A))
    
    def testLazyReference(self):
        '''AttributeInjection lazy references.'''
        from inject_tests.fixtures.lazyref import A, B
        
        a = A()
        self.assertTrue(isinstance(a.b, B))


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
            a = NamedAttributeInjection('a', A, reinject=True)
        
        self.injector.bind(A, to=A)
        
        b = B()
        a = b.a
        a2 = b.a
        
        self.assertFalse(a is a2)
        self.assertEqual(a.i, 1)
        self.assertEqual(a2.i, 2)
    
    def testLazyImports(self):
        '''NamedAttributeInjection lazy imports.'''
        from inject_tests.fixtures.cyclic1 import P
        from inject_tests.fixtures.cyclic2 import Q
        
        p = P()
        q = Q()
        
        self.assertTrue(isinstance(p.q, Q))
        self.assertTrue(isinstance(q.p, P))
    
    def testLazyRef(self):
        '''NamedAttributeInjection lazy references.'''
        from inject_tests.fixtures.lazyref import P, Q
        
        p = P()
        q = Q()
        
        self.assertTrue(isinstance(p.q, Q))
        self.assertTrue(isinstance(q.p, P))


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
        
        a = B.a
        a2 = B.a
        self.assertTrue(isinstance(a, A))
        self.assertTrue(isinstance(a2, A))
        self.assertFalse(a is a2)


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


class ParamLazyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testLazyRef(self):
        '''ParamInjection lazy references.'''
        from inject_tests.fixtures.lazyref import func, Z
        
        z = func()
        self.assertTrue(isinstance(z, Z))
    
    def testLazyImport(self):
        '''ParamInjection lazy imports.'''
        from inject_tests.fixtures.cyclic1 import func
        from inject_tests.fixtures.cyclic2 import Z
        
        z = func()
        self.assertTrue(isinstance(z, Z))
        
        z2 = z.get_z()
        self.assertTrue(isinstance(z2, Z))
