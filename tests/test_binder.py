from unittest import TestCase

import inject


class TestBinder(TestCase):
    def test_bind(self):
        binder = inject.Binder()
        binder.bind(int, 123)

        assert int in binder._bindings

    def test_bind__class_required(self):
        binder = inject.Binder()

        self.assertRaisesRegex(
            inject.InjectorException,
            "Binding key cannot be None",
            binder.bind,
            None,
            None,
        )

    def test_bind__duplicate_binding(self):
        binder = inject.Binder()
        binder.bind(int, 123)

        self.assertRaisesRegex(
            inject.InjectorException,
            "Duplicate binding",
            binder.bind,
            int,
            456,
        )

    def test_bind__allow_override(self):
        binder = inject.Binder(allow_override=True)
        binder.bind(int, 123)
        binder.bind(int, 456)
        assert int in binder._bindings

    def test_bind_provider(self):
        provider = lambda: 123
        binder = inject.Binder()
        binder.bind_to_provider(int, provider)

        assert binder._bindings[int] is provider

    def test_bind_provider__provider_required(self):
        binder = inject.Binder()
        self.assertRaisesRegex(
            inject.InjectorException,
            "Provider cannot be None",
            binder.bind_to_provider,
            int,
            None,
        )

    def test_bind_constructor(self):
        constructor = lambda: 123
        binder = inject.Binder()
        binder.bind_to_constructor(int, constructor)

        assert binder._bindings[int]._constructor is constructor

    def test_bind_constructor__constructor_required(self):
        binder = inject.Binder()
        self.assertRaisesRegex(
            inject.InjectorException,
            "Constructor cannot be None",
            binder.bind_to_constructor,
            int,
            None,
        )
