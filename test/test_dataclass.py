from dataclasses import dataclass

import inject
from test import BaseTestInject
from typing import ClassVar


class TestInjectAttr(BaseTestInject):
    def test_attr_on_dataclass_class_var_raises_error(self):
        with self.assertRaises(inject.InjectorException):
            @dataclass
            class MyClass:
                field: ClassVar[int] = inject.attr(int)


class TestInjectAttrDataclass(BaseTestInject):
    def test_attr_dc(self):
        @dataclass
        class MyClass(object):
            field = inject.attr_dc(int)

        inject.configure(lambda binder: binder.bind(int, 123))
        my = MyClass()
        value0 = my.field
        value1 = my.field

        assert value0 == 123
        assert value1 == 123

    def test_attr_on_dataclass_class_var_works(self):
        @dataclass
        class MyClass:
            field: ClassVar[int] = inject.attr_dc(int)

        inject.configure(lambda binder: binder.bind(int, 123))

        assert MyClass().field == 123
        assert MyClass.field == 123
