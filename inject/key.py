

class Key(object):
    
    __slots__ = ('type', 'annotation', '_hash')
    
    def __init__(self, type, annotation):
        self.type = type
        self.annotation = annotation
        self._hash = None
    
    def __hash__(self):
        _hash = self._hash
        if _hash is None:
            _hash = hash(self.type) ^ hash(self.annotation)
            self._hash = _hash
        return _hash
    
    def __repr__(self):
        return '<%s for "%s" annotated with "%s" at %s>' % \
            (self.__class__.__name__, self.type, self.annotation,
             hex(id(self)))