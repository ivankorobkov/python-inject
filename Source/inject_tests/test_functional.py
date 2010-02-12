import unittest

from inject.functional import update_wrapper


class UpdateWrapperTestCase(unittest.TestCase):
    
    update_wrapper = staticmethod(update_wrapper)
    
    def testFunc(self):
        '''Update_wrapper() should set func's name, doc, module and dict.'''
        def func():
            '''Docstring.'''
            pass
        func.attr = 'value'
        
        def wrapper():
            pass
        
        self.update_wrapper(wrapper, func)
        
        self.assertEqual(wrapper.__name__, 'func')
        self.assertEqual(wrapper.__doc__, 'Docstring.')
        self.assertTrue(wrapper.__module__ is func.__module__)
        self.assertEqual(wrapper.attr, 'value')
    
    def testMethod(self):
        '''Update_wrapper() should set object's name, doc, module and dict.'''
        class A(object):
            def method(self):
                '''Method's docstring.'''
                pass
        
        A.method.__dict__['key'] = 'value'
        self.assertEqual(A.method.key, 'value')
        
        a = A()
        self.assertEqual(a.method.key, 'value')
        
        class Wrapper(object):
            pass
        
        # Test using an unbound method.
        wrapper = Wrapper()
        self.update_wrapper(wrapper, A.method)
        
        self.assertEqual(wrapper.__name__, 'method')
        self.assertEqual(wrapper.__doc__, 'Method\'s docstring.')
        self.assertTrue(wrapper.__module__ is A.method.__module__)
        self.assertEqual(wrapper.key, 'value')
        
        
        # Test using a bound method.
        wrapper = Wrapper()
        self.update_wrapper(wrapper, a.method)
        
        self.assertEqual(wrapper.__name__, 'method')
        self.assertEqual(wrapper.__doc__, 'Method\'s docstring.')
        self.assertTrue(wrapper.__module__ is a.method.__module__)
        self.assertEqual(wrapper.key, 'value')