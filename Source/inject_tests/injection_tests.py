import unittest

from inject.injectors import Injector
from inject.injection import Injection


class InjectionTestCase(unittest.TestCase):
    
    injector_class = Injector
    injection_class = Injection
    
    def test(self):
        pass
