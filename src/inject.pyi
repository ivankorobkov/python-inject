from typing import Type, TypeVar, Callable, Optional, Union, Hashable

T = TypeVar('T')
Binding = Union[Type[T], Hashable]
Constructor = Provider = Callable[[], T]
BinderCallable = Callable[['Binder'], None]


class Binder(object):

    def __init__(self) -> None: ...

    def install(
        self,
        config: BinderCallable
    ) -> Binder: ...

    def bind(
        self,
        cls: Binding,
        instance: T
    ) -> Binder: ...

    def bind_to_constructor(
        self,
        cls: Binding,
        constructor: Constructor
    ) -> Binder: ...

    def bind_to_provider(
        self,
        cls: Binding,
        provider: Provider
    ) -> Binder: ...

    def _check_class(self, cls: Binding) -> None: ...


class Injector(object):

    def __init__(
        self,
        config: Optional[BinderCallable] = None,
        bind_in_runtime: bool = True
    ) -> None: ...

    def get_instance(self, cls: Binding) -> T: ...


def configure(
    config: Optional[BinderCallable], bind_in_runtime: bool = True
) -> Injector: ...


def configure_once(
    config: Optional[BinderCallable], bind_in_runtime: bool = True
) -> Injector: ...


def clear_and_configure(
    config: Optional[BinderCallable], bind_in_runtime: bool = True
) -> Injector: ...


def is_configured() -> bool: ...


def clear() -> None: ...


def params(**args_to_classes: Binding) -> Callable: ...


def autoparams(*selected_args: str) -> Callable: ...


def instance(cls: Binding) -> T: ...


def attr(cls: Binding) -> T: ...


def get_injector() -> Optional[Injector]: ...


def get_injector_or_die() -> Injector: ...

