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
