from __future__ import annotations

import inject
from test import BaseTestInject


class TestFutureSupport(BaseTestInject):
    def test_future_support(self):
        @inject.autoparams()
        def func(a: 'A', b: int):
            return a + b

        def configure(binder: inject.Binder):
            binder.bind('A', 321)
            binder.bind(int, 123)

        inject.configure(configure)

        assert func() == 444
