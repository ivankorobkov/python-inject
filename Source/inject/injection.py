'''Injection connects injection descriptors and decorators with an injector.'''


class Injection(object):
    
    '''Injection serves injection requests.'''
    
    __slots__ = ('type', 'injector')
    
    injector = None
    
    def __init__(self, type):
        self.type = type
    
    def get_instance(self):
        '''Return an instance, or raise NoProviderError.'''
        return self.injector.get_instance(self.type)
