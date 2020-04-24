from __future__ import annotations

import inject
from test import BaseTestInject


class Something:
    def return_self(self) -> Something:
        return self

    @inject.autoparams()
    def test_func(self, val: int):
        return val


class AnotherThing:
    @inject.autoparams()
    def test_func(self, val: int):
        return val


class TestFutureSupport(BaseTestInject):
    def test_future_support(self):
        inject.configure(lambda binder: binder.bind(int, 123), bind_in_runtime=False)

        self.assertRaises(inject.InjectorException, Something().test_func())
        self.assertRaises(inject.InjectorException, AnotherThing().test_func())
