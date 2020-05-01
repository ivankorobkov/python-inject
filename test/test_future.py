# from __future__ import annotations

import inject
from test import BaseTestInject

class TestFutureSupport(BaseTestInject):
    def test_future_support(self):
        # @inject.autoparams()
        # def func1(val: int):
        #     return val

        @inject.autoparams()
        def func2(val: 'A'):
            return val

        def configure(binder: inject.Binder):
            binder.bind('A', 321)

        inject.configure(configure)

        # assert func1() == 123
        assert func2() == 321
