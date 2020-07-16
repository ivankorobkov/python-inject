import inject
from test import BaseTestInject
import inspect
import asyncio

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
    
    def test_async_param(self):
        @inject.param('val')
        async def test_func(val):
            return val
        
        inject.configure(lambda binder: binder.bind('val', 123))

        assert inspect.iscoroutinefunction(test_func)
        assert self.run_async(test_func()) == 123
