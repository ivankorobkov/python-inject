'''Injection errors.'''


class NoProviderError(Exception):
    
    '''NoProviderError is raised when there is no provider bound to a key.'''
    
    def __init__(self, key):
        self.key = key
        msg = 'There is no provider for %s.' % key
        Exception.__init__(self, msg)


class NoParamError(Exception):
    
    '''NoParamError is raised when you inject a param into a func,
    but the function does not accept such a param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''


class CantBeScopedError(Exception):
    
    '''CanBeScopedError is raised when a provider cannot be scoped.
    For example, the instance provider cannot be scoped.
    '''


class NoRequestRegisteredError(Exception):
    
    '''NoRequestError is raised when a request scoped provider is accessed but 
    no request is registered.
    '''
    