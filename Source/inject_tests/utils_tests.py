'''Utility function tests.'''
import unittest
from inject.utils import get_attrname_by_value


class GetAttrnameByValueTestCase(unittest.TestCase):
    
    def test_instance(self):
        '''Get attribute name when the owner is an instance.'''
        class A(object): pass
        class B(object):
            def __init__(self):
                self.a = A()
        
        b = B()
        name = get_attrname_by_value(b, b.a)
        self.assertEqual(name, 'a')
    
    def test_class(self):
        '''Get attribute name when the owner is a class.'''
        class A(object): pass
        class B(object):
            a = A()
        
        name = get_attrname_by_value(B, B.a)
        self.assertEqual(name, 'a')
    
    def test_value_error(self):
        '''Raise ValueError when can't find an attribute by its value.'''
        class A(object): pass
        class B(object): pass
        
        self.assertRaises(ValueError, get_attrname_by_value, B, A)
