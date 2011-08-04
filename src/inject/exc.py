'''All inject exceptions.'''


class NoParamError(Exception):
    
    '''NoParamError is raised when you inject a param into a func,
    but the function does not accept such a param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''


class NoInjectorRegistered(Exception):
    
    '''NoInjectorRegistered is raised when there is no injector registered,
    and the injections try to use it.
    '''
    
    def __init__(self):
        msg = 'Injector must be instantiated and registered.' \
            'Use injector=Injector(); injector.register().'
        super(NoInjectorRegistered, self).__init__(msg)


class InjectorAlreadyRegistered(Exception):
    
    '''InjectorAlreadyRegistered is raised when the second injector
    is registered. It prevets one injector from overriding another.
    '''
    
    def __init__(self):
        msg = 'Another injector is already registered. ' \
            'There can be only one registered injector.'
        super(InjectorAlreadyRegistered, self).__init__(msg)


class NotBoundError(KeyError):
    
    '''NotBoundError extends KeyError, is raised when there is no bound
    provider for a given type.
    '''
    
    def __init__(self, key):
        msg = 'No binding for %s, use injector.bind to bind it.' \
            % str(key)
        KeyError.__init__(self, msg)


class MultipleAttrsFound(Exception):
    
    '''MultipleAttrsFound is raised when multiple attributes are found
    for the same value.
    '''


class NoAttrFound(Exception):
    
    '''NoAttrFound is raised when no attribute is found for a given value.'''


class NoRequestError(Exception):
    
    '''NoRequestError is raised when a request scope is accessed
    but no request is present.
    '''
