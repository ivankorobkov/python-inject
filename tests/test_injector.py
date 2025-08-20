from random import random
from unittest import TestCase

from inject import Injector, InjectorException


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
        self.assertRaisesRegex(InjectorException,
                               'Cannot create a runtime binding, the key is not callable, key=123',
                               injector.get_instance, 123)

    def test_runtime_binding__disabled(self):
        injector = Injector(bind_in_runtime=False)
        self.assertRaisesRegex(InjectorException,
                               "No binding was found for key=<.* 'int'>",
                               injector.get_instance, int)
