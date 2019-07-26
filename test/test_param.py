import inject
from test import BaseTestInject


class TestInjectParams(BaseTestInject):
    def test_param_by_name(self):
        @inject.param('val')
        def test_func(val=None):
            return val

        inject.configure(lambda binder: binder.bind('val', 123))

        assert test_func() == 123
        assert test_func(val=321) == 321

    def test_param_by_class(self):
        @inject.param('val', int)
        def test_func(val):
            return val

        inject.configure(lambda binder: binder.bind(int, 123))

        assert test_func() == 123
