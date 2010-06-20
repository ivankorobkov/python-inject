'''Injection errors.'''


class NoInjectorRegistered(Exception):
    
    '''NoInjectorRegistered is raised when there is no injector registered,
    and the injections try to use it.
    '''    


class NoProviderError(Exception):
    
    '''NoProviderError is raised when there is no provider bound to a key.'''
    
    def __init__(self, key):
        msg = 'There is no provider for %s.' % str(key)
        Exception.__init__(self, msg)


class NoParamError(Exception):
    
    '''NoParamError is raised when you inject a param into a func,
    but the function does not accept such a param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''


class CantCreateProviderError(Exception):
    
    '''CantCreateProviderError is raised when to is not given and type is
    not callable.
    '''
    
    def __init__(self, type):
        msg = 'Can\'t create a provider for %r.' % type
        Exception.__init__(self, msg)


class CantBeScopedError(Exception):
    
    '''CanBeScopedError is raised when a provider cannot be scoped.
    For example, the instance provider cannot be scoped.
    '''


class NoRequestRegisteredError(Exception):
    
    '''NoRequestError is raised when a request scoped provider is accessed but 
    no request is registered.
    '''
