'''
Created on Aug 2, 2010

@author: ivan
'''
import unittest

from inject.injectors import Injector
from inject.points import InjectionPoint, NoInjectorRegistered


class InjectionTestCase(unittest.TestCase):
    
    point_class = InjectionPoint
    injector_class = Injector
    
    def testGetInstance(self):
        '''InjectionPoint should call injector's get_instance method.'''
        class A(object): pass
        class B(object): pass
        
        my_injector = self.injector_class()
        my_injector.bind(A, to=B)
        
        class MyPoint(self.point_class):
            injector = my_injector
        
        injection_point = MyPoint(A)
        a = injection_point.get_instance()
        
        self.assertTrue(isinstance(a, B))
    
    def testNoInjectorRegistered(self):
        '''InjectionPoint should raise NoInjectorRegistered.'''
        class A(object): pass
        
        injection_point = self.point_class(A)
        
        self.assertRaises(NoInjectorRegistered, injection_point.get_instance)
