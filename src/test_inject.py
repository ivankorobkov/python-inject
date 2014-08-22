from random import random
from unittest import TestCase

import inject
from inject import Binder, InjectorException, Injector


class TestBinder(TestCase):
    def test_bind(self):
        binder = Binder()
        binder.bind(int, 123)

        assert int in binder._bindings

    def test_bind__class_required(self):
        binder = Binder()

        self.assertRaisesRegexp(InjectorException, 'Binding key cannot be None',
                                binder.bind, None, None)

    def test_bind__duplicate_binding(self):
        binder = Binder()
        binder.bind(int, 123)

        self.assertRaisesRegexp(InjectorException, "Duplicate binding", 
                                binder.bind, int, 456)

    def test_bind_provider(self):
        provider = lambda: 123
        binder = Binder()
        binder.bind_to_provider(int, provider)

        assert binder._bindings[int] is provider

    def test_bind_provider__provider_required(self):
        binder = Binder()
        self.assertRaisesRegexp(InjectorException, "Provider cannot be None",
                                binder.bind_to_provider, int, None)

    def test_bind_constructor(self):
        constructor = lambda: 123
        binder = Binder()
        binder.bind_to_constructor(int, constructor)

        assert binder._bindings[int]._constructor is constructor

    def test_bind_constructor__constructor_required(self):
        binder = Binder()
        self.assertRaisesRegexp(InjectorException, "Constructor cannot be None",
                                binder.bind_to_constructor, int, None)


class TestInjector(TestCase):
    def test_instance_binding__should_use_the_same_instance(self):
        injector = Injector(lambda binder: binder.bind(int, 123))
        instance = injector.get_instance(int)
        assert instance == 123

    def test_constructor_binding__should_construct_singleton(self):
        injector = Injector(lambda binder: binder.bind_to_constructor(int, random))
        instance0 = injector.get_instance(int)
        instance1 = injector.get_instance(int)

        assert instance0 == instance1

    def test_provider_binding__should_call_provider_for_each_injection(self):
        injector = Injector(lambda binder: binder.bind_to_provider(int, random))
        instance0 = injector.get_instance(int)
        instance1 = injector.get_instance(int)
        assert instance0 != instance1


    def test_runtime_binding__should_create_runtime_singleton(self):
        class MyClass(object):
            pass

        injector = Injector()
        instance0 = injector.get_instance(MyClass)
        instance1 = injector.get_instance(MyClass)

        assert instance0 is instance1
        assert isinstance(instance0, MyClass)

    def test_runtime_binding__not_callable(self):
        injector = Injector()
        self.assertRaisesRegexp(InjectorException, 
                               'Cannot create a runtime binding, the key is not callable, key=123',
                                injector.get_instance, 123)


class TestInject(TestCase):
    def tearDown(self):
        inject.clear()

    def test_configure__should_create_injector(self):
        injector0 = inject.configure()
        injector1 = inject.get_injector()
        assert injector0
        assert injector0 is injector1

    def test_configure__should_add_bindings(self):
        injector = inject.configure(lambda binder: binder.bind(int, 123))
        instance = injector.get_instance(int)
        assert instance == 123

    def test_configure__already_configured(self):
        inject.configure()

        self.assertRaisesRegexp(InjectorException, 'Injector is already configured',
                                inject.configure)
    
    def test_configure_once__should_create_injector(self):
        injector = inject.configure_once()
        assert inject.get_injector() is injector
    
    def test_configure_once__should_return_existing_injector_when_present(self):
        injector0 = inject.configure()
        injector1 = inject.configure_once()
        assert injector0 is injector1
    
    def test_is_configured__should_return_true_when_injector_present(self):
        assert inject.is_configured() is False
        
        inject.configure()
        assert inject.is_configured() is True
        
        inject.clear()
        assert inject.is_configured() is False

    def test_clear_and_configure(self):
        injector0 = inject.configure()
        injector1 = inject.clear_and_configure()    # No exception.
        assert injector0
        assert injector1
        assert injector1 is not injector0

    def test_get_injector_or_die(self):
        self.assertRaisesRegexp(InjectorException, 'No injector is configured',
                                inject.get_injector_or_die)

    def test_instance(self):
        inject.configure(lambda binder: binder.bind(int, 123))
        instance = inject.instance(int)
        assert instance == 123

    def test_attr(self):
        class MyClass(object):
            field = inject.attr(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        my = MyClass()
        value0 = my.field
        value1 = my.field

        assert value0 == 123
        assert value1 == 123

    def test_class_attr(self):
        class MyClass(object):
            field = inject.attr(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        value0 = MyClass.field
        value1 = MyClass.field

        assert value0 == 123
        assert value1 == 123

    def test_param_by_name(self):
        @inject.param('val')
        def test_func(val=None):
            return val

        inject.configure(lambda binder: binder.bind('val', 123))

        assert test_func() == 123
        assert test_func(val=321) == 321

    def test_param_by_class(self):
        @inject.param('val', int)
        def test_func(val):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert test_func() == 123

    def test_params(self):
        @inject.params(val=int)
        def test_func(val):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert test_func() == 123
        assert test_func(321) == 321
        assert test_func(val=42) == 42

    def test_params_multi(self):
        @inject.params(a='A', b='B', c='C')
        def test_func(a, b, c):
            return a, b, c

        def config(binder):
            binder.bind('A', 1)
            binder.bind('B', 2)
            binder.bind('C', 3)
        
        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, 30) == (10, 20, 30)
        assert test_func(a='a') == ('a', 2, 3)
        assert test_func(b='b') == (1, 'b', 3)
        assert test_func(c='c') == (1, 2, 'c')
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_params_with_defaults(self):
        # note the inject overrides default parameters
        @inject.params(b='B', c='C')
        def test_func(a=1, b=None, c=300):
            return a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)
        
        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, 30) == (10, 20, 30)
        assert test_func(a='a') == ('a', 2, 3)
        assert test_func(b='b') == (1, 'b', 3)
        assert test_func(c='c') == (1, 2, 'c')
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)
        
    def test_params_on_method(self):
        class Test:
            @inject.params(b='B', c='C')
            def func(self, a=1, b=None, c=None):
                return self, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)
        
        inject.configure(config)
        test = Test()
        
        assert test.func() == (test, 1, 2, 3)
        assert test.func(10) == (test, 10, 2, 3)
        assert test.func(10, 20) == (test, 10, 20, 3)
        assert test.func(10, 20, 30) == (test, 10, 20, 30)
        assert test.func(a='a') == (test, 'a', 2, 3)
        assert test.func(b='b') == (test, 1, 'b', 3)
        assert test.func(c='c') == (test, 1, 2, 'c')
        assert test.func(a=10, c=30) == (test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (test, 10, 20, 30)
        assert test.func(10, b=20) == (test, 10, 20, 3)

    def test_params_on_classmethod(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @inject.params(b='B', c='C')
            def func(cls, a=1, b=None, c=None):
                return cls, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)
        
        inject.configure(config)
        
        assert Test.func() == (Test, 1, 2, 3)
        assert Test.func(10) == (Test, 10, 2, 3)
        assert Test.func(10, 20) == (Test, 10, 20, 3)
        assert Test.func(10, 20, 30) == (Test, 10, 20, 30)
        assert Test.func(a='a') == (Test, 'a', 2, 3)
        assert Test.func(b='b') == (Test, 1, 'b', 3)
        assert Test.func(c='c') == (Test, 1, 2, 'c')
        assert Test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert Test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert Test.func(10, b=20) == (Test, 10, 20, 3)

    def test_params_on_classmethod_ob_object(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @inject.params(b='B', c='C')
            def func(cls, a=1, b=None, c=None):
                return cls, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)
        
        inject.configure(config)
        test = Test
        
        assert test.func() == (Test, 1, 2, 3)
        assert test.func(10) == (Test, 10, 2, 3)
        assert test.func(10, 20) == (Test, 10, 20, 3)
        assert test.func(10, 20, 30) == (Test, 10, 20, 30)
        assert test.func(a='a') == (Test, 'a', 2, 3)
        assert test.func(b='b') == (Test, 1, 'b', 3)
        assert test.func(c='c') == (Test, 1, 2, 'c')
        assert test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert test.func(10, b=20) == (Test, 10, 20, 3)

      
class TestFunctional(TestCase):
    def tearDown(self):
        inject.clear()
    
    def test(self):
        class Config(object):
            def __init__(self, greeting):
                self.greeting = greeting
        
        class Cache(object):
            config = inject.attr(Config)
            
            def load_greeting(self):
                return self.config.greeting
        
        class User(object):
            cache = inject.attr(Cache)
            
            def __init__(self, name):
                self.name = name
                
            def greet(self):
                return '%s, %s' % (self.cache.load_greeting(), self.name)
        
        def config(binder):
            binder.bind(Config, Config('Hello'))
        
        inject.configure(config)
        
        user = User('John Doe')
        greeting = user.greet()
        assert greeting == 'Hello, John Doe'
