import unittest
from inject.imports import lazy_import


class LazyImportTestCase(unittest.TestCase):
    
    def testLazyReference(self):
        self.assertTrue(lazy_reference() is DummyObject)
    
    def testLazyReferenceError(self):
        dummy_object = lazy_import('.WrongObject', globals())
        self.assertRaises(ImportError, dummy_object)
    
    def testLazyImport(self):
        lazy = lazy_import('inject.Injector')
        from inject import Injector
        self.assertTrue(lazy() is Injector)
    
    def testLazyImportError(self):
        lazy = lazy_import('wrong.module.Class')
        self.assertRaises(ImportError, lazy)
    
    def testString(self):
        lazy = lazy_import('string')
        self.assertEqual(lazy(), 'string')


lazy_reference = lazy_import('.DummyObject', globals())


class DummyObject(object):
    
    pass
