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
            auto_typed_field: int = inject.attr()

        inject.configure(lambda binder: binder.bind(int, 123))
        my = MyClass()
        my_dc = MyDataClass()

        assert my.field == 123
        assert my.field == 123
        assert my.field2 == 123
        assert my.field2 == 123
        assert my.auto_typed_field == 123
        assert my.auto_typed_field == 123
        assert my_dc.field == 123
        assert my_dc.field == 123

    def test_invalid_attachment_to_dataclass(self):
        @dataclass
        class MyDataClass:
            # dataclasses treat this definition as regular descriptor
            field: int = inject.attr(int)

        self.assertRaises(AttributeError, MyDataClass)

    def test_class_attr(self):
        descriptor = inject.attr(int)
        auto_descriptor = inject.attr()

        @dataclass
        class MyDataClass:
            field = descriptor

        class MyClass(object):
            field = descriptor
            field2: int = descriptor
            auto_typed_field: int = auto_descriptor

        inject.configure(lambda binder: binder.bind(int, 123))

        assert MyClass.field is descriptor
        assert MyClass.field is descriptor
        assert MyClass.field2 is descriptor
        assert MyClass.field2 is descriptor
        assert MyClass.auto_typed_field is auto_descriptor
        assert MyClass.auto_typed_field is auto_descriptor
        assert MyDataClass.field is descriptor
        assert MyDataClass.field is descriptor
