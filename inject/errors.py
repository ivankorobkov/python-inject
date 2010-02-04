

class NoProviderError(Exception):
    
    '''NoProviderError is raised when there is no provider bound to a key.'''
    
    def __init__(self, key):
        self.key = key
        msg = 'There is no provider for key %s.' % key
        Exception.__init__(msg)


class NoParamError(Exception):
    
    '''NoParamError is raised when you inject a param into a func,
    but the function does not accept such a param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''
    
    pass