import unittest
from mock import Mock


from inject.injection import Injection


class InjectionTestCase(unittest.TestCase):
    
    injection_class = Injection
    
    def test(self):
        '''Injection should call injector's get_instance method.'''
        class A(object):
            pass
        
        class DummyInjection(self.injection_class):
            '''DummyInjection allows to override the injector attr.'''
        
        injector = Mock()
        DummyInjection.injector = injector
        injection = DummyInjection(A)
        injection.get_instance()
        
        self.assertTrue(injector.get_instance.called)
