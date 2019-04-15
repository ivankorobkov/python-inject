from typing import Type, TypeVar, Callable, Optional


T = TypeVar('T')


class Binder(object):

    def __init__(self) -> None: ...

    def install(
        self,
        config: Callable[[Binder], None]
    ) -> Binder: ...

    def bind(
        self,
        cls: Type[T],
        instance: T
    ) -> Binder: ...

    def bind_to_constructor(
        self,
        cls: Type[T],
        constructor: Callable
    ) -> Binder: ...

    def bind_to_provider(
        self,
        cls: Type[T],
        provider: Callable
    ) -> Binder: ...

    def _check_class(self, cls: Type[T]) -> None: ...


class Injector(object):

    def __init__(
        self,
        config: Optional[Callable[[Binder], None]] = None,
        bind_in_runtime: bool = True
    ) -> None: ...

    def get_instance(self, cls: Type[T]) -> T: ...


def configure(
    config: Optional[Callable], bind_in_runtime: bool = True
) -> None: ...


def configure_once(
    config: Optional[Callable], bind_in_runtime: bool = True
) -> None: ...


def clear_and_configure(
    config: Optional[Callable], bind_in_runtime: bool = True
) -> None: ...


def is_configured() -> bool: ...


def clear() -> None: ...


def params(**args_to_classes: Type[T]) -> Callable: ...


def autoparams(*selected_args: str) -> Callable: ...


def instance(cls: Type[T]) -> T: ...


def attr(cls: Type[T]) -> T: ...


def get_injector() -> Optional[Injector]: ...


def get_injector_or_die() -> Injector: ...

