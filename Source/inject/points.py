'''InjectionPoint connects injection requests with an injector.'''


class NoInjectorRegistered(Exception):
    
    '''NoInjectorRegistered is raised when there is no injector registered,
    and the injections try to use it.
    '''


class InjectionPoint(object):
    
    '''InjectionPoint serves injection requests.'''
    
    __slots__ = ('type', 'injector')
    
    injector = None
    
    def __init__(self, type):
        self.type = type
    
    def get_instance(self):
        '''Return an instance from an injector.'''
        injector = self.injector
        if injector is None:
            raise NoInjectorRegistered()
        
        return self.injector.get_instance(self.type)
