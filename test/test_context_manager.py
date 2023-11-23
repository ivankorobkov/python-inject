import contextlib

import inject
from test import BaseTestInject


class Destroyable:
    def __init__(self):
        self.started = True

    def destroy(self):
        self.started = False


class MockFile(Destroyable):
    ...


class MockConnection(Destroyable):
    ...


class MockFoo(Destroyable):
    ...


@contextlib.contextmanager
def get_file_sync():
    obj = MockFile()
    yield obj
    obj.destroy()


@contextlib.contextmanager
def get_conn_sync():
    obj = MockConnection()
    yield obj
    obj.destroy()


@contextlib.contextmanager
def get_foo_sync():
    obj = MockFoo()
    yield obj
    obj.destroy()


@contextlib.asynccontextmanager
async def get_file_async():
    obj = MockFile()
    yield obj
    obj.destroy()


@contextlib.asynccontextmanager
async def get_conn_async():
    obj = MockConnection()
    yield obj
    obj.destroy()


class TestContextManagerFunctional(BaseTestInject):

    def test_provider_as_context_manager_sync(self):
        def config(binder):
            binder.bind_to_provider(MockFile, get_file_sync)
            binder.bind(int, 100)
            binder.bind_to_provider(str, lambda: "Hello")
            binder.bind_to_provider(MockConnection, get_conn_sync)

        inject.configure(config)

        @inject.autoparams()
        def mock_func(conn: MockConnection, name: str, f: MockFile, number: int):
            assert f.started
            assert conn.started
            assert name == "Hello"
            assert number == 100
            return f, conn

        f_, conn_ = mock_func()
        assert not f_.started
        assert not conn_.started

    def test_provider_as_context_manager_async(self):
        def config(binder):
            binder.bind_to_provider(MockFile, get_file_async)
            binder.bind(int, 100)
            binder.bind_to_provider(str, lambda: "Hello")
            binder.bind_to_provider(MockConnection, get_conn_async)
            binder.bind_to_provider(MockFoo, get_foo_sync)

        inject.configure(config)

        @inject.autoparams()
        async def mock_func(conn: MockConnection, name: str, f: MockFile, number: int, foo: MockFoo):
            assert f.started
            assert conn.started
            assert foo.started
            assert name == "Hello"
            assert number == 100
            return f, conn, foo

        f_, conn_, foo_ = self.run_async(mock_func())
        assert not f_.started
        assert not conn_.started
        assert not foo_.started