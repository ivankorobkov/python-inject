from unittest import TestCase
import asyncio
import inject


class BaseTestInject(TestCase):
    def tearDown(self):
        inject.clear()
    
    def run_async(self, awaitable):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(awaitable)