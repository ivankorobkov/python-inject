from __future__ import annotations

from test import BaseTestInject

import inject


class TestFutureSupport(BaseTestInject):
    def test_future_support(self):
        @inject.autoparams()
        def func(a: 'A', b: int):
            return a + b

        @inject.autoparams()
        def func2(val: int):
            return val

        @inject.autoparams()
        def func3(a: 'A', b: 'int'):
            return a + b

        def configure(binder: inject.Binder):
            binder.bind('A', 1)
            binder.bind(int, 2)
            binder.bind('int', 3)

        inject.configure(configure)

        assert func() == 3
        assert func2() == 2
        assert func3() == 4
