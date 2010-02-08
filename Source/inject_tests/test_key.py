import unittest

from inject import key


class KeyTestCase(unittest.TestCase):
    
    key_class = key.Key
    
    def testHash(self):
        '''Keys constructed from the same objs must have equal hashes.'''
        obj = object()
        key = self.key_class(obj, 'annotation')
        key2 = self.key_class(obj, 'annotation')
        
        self.assertTrue(isinstance(key, self.key_class))
        self.assertTrue(key is not key2)
        self.assertEqual(hash(key), hash(key2))
        
        d = {}
        d[key] = 'value'
        self.assertEqual(d[key2], 'value')
    
    def testEqual(self):
        '''Keys constructed from the same objs must be equal.'''
        obj = object()
        key = self.key_class(obj, 'annotation')
        key2 = self.key_class(obj, 'annotation')
        
        self.assertEqual(key, key2)
    
    def testNotEqual(self):
        '''Keys constructed from different objs must be non-equal.'''
        obj = object()
        key = self.key_class(obj, 'annotation')
        key2 = self.key_class(obj, 'annotation2')
        
        self.assertNotEqual(key, key2)