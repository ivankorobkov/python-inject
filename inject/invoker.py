

class Invoker(object):
    
    __slots__ = ('method', 'injection', '_hash')
    
    injection_class = None
    
    def __init__(self, unbound_method, scope=None):
        m = unbound_method
        
        if not hasattr(m, 'im_class') or \
           not hasattr(m, 'im_func') or \
           not hasattr(m, 'im_self') or \
           m.im_self is not None:
            raise TypeError('Unbound method required, got %s.' % m)
        
        self.method = m
        self.injection = self.injection_class(m.im_class, scope=scope)
        self._hash = None
    
    def __call__(self, *args, **kwargs):
        '''Invoke the unbound method, return the result.'''
        inst = self.injection.get_instance()
        return self.method(inst, *args, **kwargs)


from inject.injection import Injection
Invoker.injection_class = Injection