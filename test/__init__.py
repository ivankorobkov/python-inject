from unittest import TestCase

import inject


class BaseTestInject(TestCase):
    def tearDown(self):
        inject.clear()