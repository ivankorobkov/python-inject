'''InjectionPoint connects injection requests with an injector.'''


class InjectionPoint(object):
    
    '''InjectionPoint serves injection requests.'''
    
    __slots__ = ('type', 'injector')
    
    injector = None
    
    def __init__(self, type):
        self.type = type
    
    def get_instance(self):
        '''Return an instance from an injector.'''
        return self.injector.get_instance(self.type)
