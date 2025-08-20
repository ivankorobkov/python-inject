import sys
import typing as t

import inject
from tests import BaseTestInject


class A:
    pass


class B:
    pass


class C:
    pass


class TestInjectEmptyAutoparamsWithBraces(BaseTestInject):
    @staticmethod
    def _get_decorator():
        return inject.autoparams()

    def test_autoparams_by_class(self):
        @self._get_decorator()
        def test_func(val: t.Optional[int] = None):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert test_func() == 123
        assert test_func(val=321) == 321

    def test_autoparams_multi(self):
        @self._get_decorator()
        def test_func(a: A, b: B, *, c: C):
            return a, b, c

        def config(binder):
            binder.bind(A, 1)
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, c=30) == (10, 20, 30)
        assert test_func(a="a") == ("a", 2, 3)
        assert test_func(b="b") == (1, "b", 3)
        assert test_func(c="c") == (1, 2, "c")
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_autoparams_strings(self):
        @self._get_decorator()
        def test_func(a: A, b: B, *, c: C):
            return a, b, c

        def config(binder):
            binder.bind(A, 1)
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, c=30) == (10, 20, 30)
        assert test_func(a="a") == ("a", 2, 3)
        assert test_func(b="b") == (1, "b", 3)
        assert test_func(c="c") == (1, 2, "c")
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_autoparams_with_defaults(self):
        @self._get_decorator()
        def test_func(a=1, b: B = None, *, c: C = 300):
            return a, b, c

        def config(binder):
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        assert test_func() == (1, 2, 3)
        assert test_func(10) == (10, 2, 3)
        assert test_func(10, 20) == (10, 20, 3)
        assert test_func(10, 20, c=30) == (10, 20, 30)
        assert test_func(a="a") == ("a", 2, 3)
        assert test_func(b="b") == (1, "b", 3)
        assert test_func(c="c") == (1, 2, "c")
        assert test_func(a=10, c=30) == (10, 2, 30)
        assert test_func(c=30, b=20, a=10) == (10, 20, 30)
        assert test_func(10, b=20) == (10, 20, 3)

    def test_autoparams_on_method(self):
        class Test:
            @self._get_decorator()
            def func(self, a=1, b: B = None, *, c: t.Optional[C] = None):
                return self, a, b, c

        def config(binder):
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)
        test = Test()

        assert test.func() == (test, 1, 2, 3)
        assert test.func(10) == (test, 10, 2, 3)
        assert test.func(10, 20) == (test, 10, 20, 3)
        assert test.func(10, 20, c=30) == (test, 10, 20, 30)
        assert test.func(a="a") == (test, "a", 2, 3)
        assert test.func(b="b") == (test, 1, "b", 3)
        assert test.func(c="c") == (test, 1, 2, "c")
        assert test.func(a=10, c=30) == (test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (test, 10, 20, 30)
        assert test.func(10, b=20) == (test, 10, 20, 3)

    def test_autoparams_on_classmethod(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @self._get_decorator()
            def func(cls, a=1, b: B = None, *, c: t.Optional[C] = None):
                return cls, a, b, c

        def config(binder):
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        assert Test.func() == (Test, 1, 2, 3)
        assert Test.func(10) == (Test, 10, 2, 3)
        assert Test.func(10, 20) == (Test, 10, 20, 3)
        assert Test.func(10, 20, c=30) == (Test, 10, 20, 30)
        assert Test.func(a="a") == (Test, "a", 2, 3)
        assert Test.func(b="b") == (Test, 1, "b", 3)
        assert Test.func(c="c") == (Test, 1, 2, "c")
        assert Test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert Test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert Test.func(10, b=20) == (Test, 10, 20, 3)

    def test_autoparams_on_classmethod_ob_object(self):
        class Test:
            # note inject must be *before* classmethod!
            @classmethod
            @self._get_decorator()
            def func(cls, a=1, b: B = None, *, c: t.Optional[C] = None):
                return cls, a, b, c

        def config(binder):
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)
        test = Test

        assert test.func() == (Test, 1, 2, 3)
        assert test.func(10) == (Test, 10, 2, 3)
        assert test.func(10, 20) == (Test, 10, 20, 3)
        assert test.func(10, 20, c=30) == (Test, 10, 20, 30)
        assert test.func(a="a") == (Test, "a", 2, 3)
        assert test.func(b="b") == (Test, 1, "b", 3)
        assert test.func(c="c") == (Test, 1, 2, "c")
        assert test.func(a=10, c=30) == (Test, 10, 2, 30)
        assert test.func(c=30, b=20, a=10) == (Test, 10, 20, 30)
        assert test.func(10, b=20) == (Test, 10, 20, 3)

    def test_autoparams_omits_return_type(self):
        @self._get_decorator()
        def test_func(a: str) -> int:
            return a

        def config(binder):
            binder.bind(str, "bazinga")

        inject.configure(config)

        assert test_func() == "bazinga"


class TestInjectEmptyAutoparamsNoBraces(TestInjectEmptyAutoparamsWithBraces):
    @staticmethod
    def _get_decorator():
        return inject.autoparams


class TestInjectSelectedAutoparams(BaseTestInject):
    def test_autoparams_only_selected(self):
        @inject.autoparams("a", "c")
        def test_func(a: A, b: B, *, c: C):
            return a, b, c

        def config(binder):
            binder.bind(A, 1)
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        self.assertRaises(TypeError, test_func)
        self.assertRaises(TypeError, test_func, a=1, c=3)

    def test_autoparams_only_selected_with_optional(self):
        @inject.autoparams("a", "c")
        def test_func(a: A, b: B, *, c: t.Optional[C] = None):
            return a, b, c

        def config(binder):
            binder.bind(A, 1)
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        self.assertRaises(TypeError, test_func)
        self.assertRaises(TypeError, test_func, a=1, c=3)

    def test_autoparams_only_selected_with_optional_pep604_union(self):
        if not sys.version_info[:3] >= (3, 10, 0):
            return

        @inject.autoparams("a", "c")
        def test_func(a: A, b: B, *, c: t.Optional[C] = None):
            return a, b, c

        def config(binder):
            binder.bind(A, 1)
            binder.bind(B, 2)
            binder.bind(C, 3)

        inject.configure(config)

        self.assertRaises(TypeError, test_func)
        self.assertRaises(TypeError, test_func, a=1, c=3)
