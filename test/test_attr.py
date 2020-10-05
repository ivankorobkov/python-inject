import inject
from test import BaseTestInject


class TestInjectAttr(BaseTestInject):
    def test_attr(self):
        class MyClass(object):
            field = inject.attr(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        my = MyClass()
        value0 = my.field
        value1 = my.field

        assert value0 == 123
        assert value1 == 123

    def test_class_attr(self):
        class MyClass(object):
            field = inject.attr(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        value0 = MyClass.field
        value1 = MyClass.field

        assert value0 == 123
        assert value1 == 123


class TestInjectAttrDataclass(BaseTestInject):
    def test_class_attr_dc(self):
        class MyClass(object):
            field = inject.attr_dc(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        value0 = MyClass.field
        value1 = MyClass.field

        assert value0 == 123
        assert value1 == 123

