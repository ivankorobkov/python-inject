from unittest import TestCase

import inject
from inject import autoparams, ConstructorTypeError


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

    def test_class_with_restricted_bool_casting(self):
        class DataFrame(object):
            def __nonzero__(self):
                """Python 2"""
                raise NotImplementedError('Casting to boolean is not allowed')

            def __bool__(self):
                """Python 3"""
                raise NotImplementedError('Casting to boolean is not allowed')

        def create_data_frame():
            return DataFrame()

        def config(binder):
            binder.bind_to_constructor(DataFrame, create_data_frame)

        inject.configure(config)

        assert type(inject.instance(DataFrame)) is DataFrame
        # There should not be an error when we fetch created instance
        assert type(inject.instance(DataFrame)) is DataFrame

    def test_class_support_in_autoparams_programmaticaly(self):
        class AnotherClass:
            pass

        class SomeClass:
            def __init__(self, another_object: AnotherClass):
                self.another_object = another_object

        def config(binder):
            binder.bind_to_constructor(SomeClass, autoparams()(SomeClass))
            binder.bind_to_constructor(AnotherClass, autoparams()(AnotherClass))

        inject.configure(config)

        some_object = inject.instance(SomeClass)
        assert type(some_object) is SomeClass
        assert type(some_object.another_object) is AnotherClass

    def test_error_message(self):
        class SomeClass:
            def __init__(self, missing_arg):
                self._missing_arg = missing_arg

        class AnotherClass(SomeClass):
            pass

        def create_some_class(missing_arg):
            return AnotherClass(missing_arg)

        def config(binder):
            binder.bind_to_constructor(SomeClass, autoparams()(SomeClass))
            binder.bind_to_constructor(AnotherClass, create_some_class)

        inject.configure()

        # covers case when no constructor provided
        try:
            inject.instance(SomeClass)
        except ConstructorTypeError as err:
            assert 'SomeClass' in str(err)
            assert 'missing_arg' in str(err)

        inject.clear_and_configure(config)

        # covers case with provided constructor
        try:
            inject.instance(SomeClass)
        except ConstructorTypeError as err:
            assert 'SomeClass' in str(err)
            assert 'missing_arg' in str(err)

        try:
            inject.instance(AnotherClass)
        except TypeError as err:
            assert not isinstance(err, ConstructorTypeError)
            assert 'create_some_class' in str(err)
            assert 'missing_arg' in str(err)