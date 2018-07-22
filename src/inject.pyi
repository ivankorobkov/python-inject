import typing


T = typing.TypeVar('T')
Injector = typing.TypeVar('Injector')


def configure(config: typing.Optional[typing.Callable]) -> typing.NoReturn: ...


def configure_once(config: typing.Optional[typing.Callable]) -> typing.NoReturn: ...


def clear_and_configure(config: typing.Optional[typing.Callable]) -> typing.NoReturn: ...


def is_configured() -> bool: ...


def clear() -> typing.NoReturn: ...


def instance(cls: typing.Type[T]) -> T: ...


def attr(cls: typing.Type[T]) -> T: ...


def get_injector() -> typing.Optional[Injector]: ...


def get_injector_or_die() -> Injector: ...

