import asyncio
import typing as t
from unittest import TestCase

import inject


class BaseTestInject(TestCase):
    def tearDown(self) -> None:
        inject.clear()

    def run_async(self, awaitable: t.Awaitable):  # noqa: ANN201
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(awaitable)
