import inject
from test import BaseTestInject
import inspect
import asyncio

class TestInjectParams(BaseTestInject):
    def test_params(self):
        @inject.params(val=int)
        def test_func(val):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert test_func() == 123
        assert test_func(321) == 321
        assert test_func(val=42) == 42

    def test_params_multi(self):
        @inject.params(a='A', b='B', c='C')
        def test_func(a, b, c):
            return a, b, c

        def config(binder):
            binder.bind('A', 1)
            binder.bind('B', 2)
            binder.bind('C', 3)

        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, 30) == (10, 20, 30)
        assert test_func(a='a') == ('a', 2, 3)
        assert test_func(b='b') == (1, 'b', 3)
        assert test_func(c='c') == (1, 2, 'c')
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_params_with_defaults(self):
        # note the inject overrides default parameters
        @inject.params(b='B', c='C')
        def test_func(a=1, b=None, c=300):
            return a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)

        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, 30) == (10, 20, 30)
        assert test_func(a='a') == ('a', 2, 3)
        assert test_func(b='b') == (1, 'b', 3)
        assert test_func(c='c') == (1, 2, 'c')
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_params_on_method(self):
        class Test:
            @inject.params(b='B', c='C')
            def func(self, a=1, b=None, c=None):
                return self, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)

        inject.configure(config)
        test = Test()

        assert test.func() == (test, 1, 2, 3)
        assert test.func(10) == (test, 10, 2, 3)
        assert test.func(10, 20) == (test, 10, 20, 3)
        assert test.func(10, 20, 30) == (test, 10, 20, 30)
        assert test.func(a='a') == (test, 'a', 2, 3)
        assert test.func(b='b') == (test, 1, 'b', 3)
        assert test.func(c='c') == (test, 1, 2, 'c')
        assert test.func(a=10, c=30) == (test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (test, 10, 20, 30)
        assert test.func(10, b=20) == (test, 10, 20, 3)

    def test_params_on_classmethod(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @inject.params(b='B', c='C')
            def func(cls, a=1, b=None, c=None):
                return cls, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)

        inject.configure(config)

        assert Test.func() == (Test, 1, 2, 3)
        assert Test.func(10) == (Test, 10, 2, 3)
        assert Test.func(10, 20) == (Test, 10, 20, 3)
        assert Test.func(10, 20, 30) == (Test, 10, 20, 30)
        assert Test.func(a='a') == (Test, 'a', 2, 3)
        assert Test.func(b='b') == (Test, 1, 'b', 3)
        assert Test.func(c='c') == (Test, 1, 2, 'c')
        assert Test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert Test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert Test.func(10, b=20) == (Test, 10, 20, 3)

    def test_params_on_classmethod_ob_object(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @inject.params(b='B', c='C')
            def func(cls, a=1, b=None, c=None):
                return cls, a, b, c

        def config(binder):
            binder.bind('B', 2)
            binder.bind('C', 3)

        inject.configure(config)
        test = Test

        assert test.func() == (Test, 1, 2, 3)
        assert test.func(10) == (Test, 10, 2, 3)
        assert test.func(10, 20) == (Test, 10, 20, 3)
        assert test.func(10, 20, 30) == (Test, 10, 20, 30)
        assert test.func(a='a') == (Test, 'a', 2, 3)
        assert test.func(b='b') == (Test, 1, 'b', 3)
        assert test.func(c='c') == (Test, 1, 2, 'c')
        assert test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert test.func(10, b=20) == (Test, 10, 20, 3)

    def test_async_params(self):
        @inject.params(val=int)
        async def test_func(val):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert inspect.iscoroutinefunction(test_func)
        assert self.run_async(test_func()) == 123
        assert self.run_async(test_func(321)) == 321
        assert self.run_async(test_func(val=42)) == 42
