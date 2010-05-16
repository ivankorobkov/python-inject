'''Injection serves injection requests.'''
from inject import errors
from inject.key import Key


class Injection(object):
    
    '''Injection serves injection requests.
    
    Resolving flow:
        
        1. If an injector is registered, try to get an instance from it.
            - If an annotation exists, try to get an instance for Key(type, 
              annotation).
            - If no instance is returned, try to get an instance for type.
            - Return an instance, or continue.
        2. If the injection has a provider (either from a callable type,
           or from a bindto argument), use it to get an instance and return it.
        3. Otherwise, raise NoProviderError.
    
    '''
    
    __slots__ = ('key', 'type', 'provider')
    
    injector = None
    key_class = Key
    
    def __init__(self, type, annotation=None):
        self.key = self.key_class(type, annotation)
        self.type = type
    
    def get_instance(self):
        '''Return an instance, or raise NoProviderError.'''
        key = self.key
        type = self.type
        injector = self.injector
        
        bindings = injector.bindings
        if key in bindings:
            return bindings[key]()
        if type in bindings:
            return bindings[type]()
        
        raise errors.NoProviderError(type)
