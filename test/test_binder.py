from unittest import TestCase

from inject import Binder, InjectorException


class TestBinder(TestCase):
    def test_bind(self):
        binder = Binder()
        binder.bind(int, 123)

        assert int in binder._bindings

    def test_bind__class_required(self):
        binder = Binder()

        self.assertRaisesRegex(InjectorException, 'Binding key cannot be None', binder.bind, None, None)

    def test_bind__duplicate_binding(self):
        binder = Binder()
        binder.bind(int, 123)

        self.assertRaisesRegex(InjectorException, "Duplicate binding", binder.bind, int, 456)

    def test_bind__allow_override(self):
        binder = Binder(allow_override=True)
        binder.bind(int, 123)
        binder.bind(int, 456)
        assert int in binder._bindings

    def test_bind_provider(self):
        provider = lambda: 123
        binder = Binder()
        binder.bind_to_provider(int, provider)

        assert binder._bindings[int] is provider

    def test_bind_provider__provider_required(self):
        binder = Binder()
        self.assertRaisesRegex(InjectorException, "Provider cannot be None", binder.bind_to_provider, int, None)

    def test_bind_constructor(self):
        constructor = lambda: 123
        binder = Binder()
        binder.bind_to_constructor(int, constructor)

        assert binder._bindings[int]._constructor is constructor

    def test_bind_constructor__constructor_required(self):
        binder = Binder()
        self.assertRaisesRegex(InjectorException, "Constructor cannot be None", binder.bind_to_constructor, int, None)
