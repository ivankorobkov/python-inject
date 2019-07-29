import inject
from test import BaseTestInject


class TestInjectInstance(BaseTestInject):
    def test_instance(self):
        inject.configure(lambda binder: binder.bind(int, 123))
        instance = inject.instance(int)
        assert instance == 123
