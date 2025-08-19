from dataclasses import dataclass
import inject
from test import BaseTestInject


class TestInjectAttr(BaseTestInject):
    def test_attr(self):
        @dataclass
        class MyDataClass:
            field = inject.attr(int)

        class MyClass:
            field = inject.attr(int)
            field2: int = inject.attr(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        my = MyClass()
        my_dc = MyDataClass()
        value0 = my.field
        value1 = my.field
        value2 = my_dc.field
        value3 = my_dc.field

        assert value0 == 123
        assert value1 == 123
        assert value2 == 123
        assert value3 == 123

    def test_invalid_attachment_to_dataclass(self):
        @dataclass
        class MyDataClass:
            # dataclasses treat this definition as regular descriptor
            field: int = inject.attr(int)

        self.assertRaises(AttributeError, MyDataClass)

    def test_class_attr(self):
        descriptor = inject.attr(int)

        @dataclass
        class MyDataClass:
            field = descriptor

        class MyClass(object):
            field = descriptor

        inject.configure(lambda binder: binder.bind(int, 123))
        value0 = MyClass.field
        value1 = MyClass.field
        value2 = MyDataClass.field
        value3 = MyDataClass.field

        assert value0 is descriptor
        assert value1 is descriptor
        assert value2 is descriptor
        assert value3 is descriptor
