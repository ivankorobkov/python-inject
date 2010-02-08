'''Key combines a type and an annotation into one hashable object. If two keys 
are constructed from the same objects, their hashes are equal.
'''


class Key(object):
    
    '''Key combines binding type and annotation into one object. Two different
    keys, constructed from the same objects always have the same hash.
    
    Example::
    
        >>> class A(object): pass
        >>> key = Key(A, 'annotation')
        >>> key2 = Key(A, 'annotation')
        
        >>> key is key2
        False
        >>> key == key2
        True
        
        >>> d = {}
        >>> d[key] = 'value'
        >>> d[key2]
        'value'
    
    '''
    
    __slots__ = ('type', 'annotation', '_hash')
    
    def __new__(cls, type, annotation=None):
        if annotation is None:
            return type
        return super(Key, cls).__new__(cls)
    
    def __init__(self, type, annotation=None):
        self.type = type
        self.annotation = annotation
        self._hash = None
    
    def __hash__(self):
        _hash = self._hash
        if _hash is None:
            _hash = hash(self.type) ^ hash(self.annotation)
            self._hash = _hash
        return _hash
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __ne__(self, other):
        return hash(self) != hash(other)
    
    def __repr__(self):
        return '<%s for "%s" annotated with "%s" at %s>' % \
            (self.__class__.__name__, self.type, self.annotation,
             hex(id(self)))