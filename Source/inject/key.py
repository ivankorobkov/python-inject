'''Key combines a type and an annotation into one hashable object. If two keys 
are constructed from the same objects, their hashes are equal.
'''


class Key(object):
    
    '''Key is a factory which returns an object or a tuple depending on
    whether the annotation has been given. When the annotation is not given,
    it returns C{type} untouched.
    '''
    
    def __new__(cls, type, annotation=None):
        if annotation is None:
            return type
        return type, annotation