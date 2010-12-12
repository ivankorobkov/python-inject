import unittest

import inject
from inject import Injector
from inject.imports import LazyImport, lazy_import


class LazyImportTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def testObjProperty(self):
        '''LazyImport should lazily reference an object.'''
        self.assertTrue(LazyRef.obj is Ref)
    
    def testHashEq(self):
        '''LazyImport should be equal to the ref object, and has the same hash.'''
        self.assertEqual(hash(LazyRef), hash(Ref))
        self.assertEqual(LazyRef, Ref)
    
    def testInjection(self):
        '''LazyImport in injections.'''
        class B(object):
            a = inject.attr(inject.lazy('inject_tests.fixtures.lazy.A'))
        b = B()
        
        from inject_tests.fixtures.lazy import A
        a = A()
        self.injector.bind(A, a)
        
        self.assertTrue(b.a is a) 


class LazyImportFuncTestCase(unittest.TestCase):
    
    def testReference(self):
        r = lazy_import('Ref', globals())
        self.assertTrue(r() is Ref)
    
    def testReferenceImportError(self):
        r = lazy_import('WrongRef', globals())
        self.assertRaises(ImportError, r) 
    
    def testImport(self):
        a = lazy_import('inject_tests.fixtures.lazy.A', None)
        
        from inject_tests.fixtures.lazy import A
        self.assertTrue(a() is A)
    
    def testImportError(self):
        wrong = lazy_import('inject_tests.fixtures.lazy.WrongClass', None)
        self.assertRaises(ImportError, wrong)


LazyRef = LazyImport('Ref')


class Ref(object):
    
    pass
