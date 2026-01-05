import asyncio
import typing as t
from unittest import TestCase

import inject


class BaseTestInject(TestCase):
    def tearDown(self) -> None:
        inject.clear()

    def run_async(self, awaitable: t.Awaitable):  # noqa: ANN201
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ret = loop.run_until_complete(awaitable)
        finally:
            loop.close()
        return ret
