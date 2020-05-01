from __future__ import annotations

import inject
from test import BaseTestInject


class TestFutureSupport(BaseTestInject):
    def test_future_support(self):
        @inject.autoparams()
        def func(a: 'A', b: int):
            return a + b

        @inject.autoparams()
        def func2(val: int):
            return val + 321

        @inject.autoparams()
        def func3(a: 'A', b: 'int'):
            return a + b

        def configure(binder: inject.Binder):
            binder.bind('A', 321)
            binder.bind(int, 123)
            binder.bind('int', 123)

        inject.configure(configure)

        assert func() == 444
        assert func2() == 444
        assert func3() == 444
