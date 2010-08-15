'''Utility function tests.'''
import unittest
from inject.utils import get_attrname_by_value, MultipleAttrsFound, NoAttrFound


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
    
    def test_inheritance(self):
        '''Get attribute name when attr is defined in a super class.'''
        class A(object): pass
        a = A()
        
        class B(object):
            mya = a
        
        class C(B): pass
        c = C()
        
        name = get_attrname_by_value(c, a)
        self.assertEqual(name, 'mya')
    
    def test_multiple_attrs(self):
        '''Raise MultipleAttrsFound when multiple attrs with for a value.'''
        class A(object): pass
        a = A()
        
        class B(object):
            a1 = a
            a2 = a
        
        self.assertRaises(MultipleAttrsFound, get_attrname_by_value, B, a)
    
    def test_value_error(self):
        '''Raise NoAttrFound when can't find an attribute by its value.'''
        class A(object): pass
        class B(object): pass
        
        self.assertRaises(NoAttrFound, get_attrname_by_value, B, A)
