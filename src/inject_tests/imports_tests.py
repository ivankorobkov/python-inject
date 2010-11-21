import unittest
from inject.imports import lazy_import


class LazyImportTestCase(unittest.TestCase):
    
    def test_lazy_reference(self):
        self.assertTrue(lazy_reference() is DummyObject)
    
    def test_lazy_reference_error(self):
        dummy_object = lazy_import('.WrongObject', globals())
        self.assertRaises(ImportError, dummy_object)
    
    def test_lazy_import(self):
        lazy = lazy_import('inject.Injector')
        from inject import Injector
        inj = lazy()
        self.assertTrue(lazy() is Injector)
    
    def test_lazy_import_error(self):
        lazy = lazy_import('wrong.module.Class')
        self.assertRaises(ImportError, lazy)


lazy_reference = lazy_import('.DummyObject', globals())


class DummyObject(object):
    
    pass
