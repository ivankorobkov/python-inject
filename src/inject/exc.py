'''All inject exceptions.'''


class NoInjectorRegistered(Exception):
    
    '''NoInjectorRegistered is raised when there is no injector registered,
    and the injections try to use it.
    '''
    
    def __init__(self):
        msg = 'Injector must be instantiated and registered.' \
            'Use injector=Injector.create(), or injector=Injector(); ' \
            'injector.register().'
        super(NoInjectorRegistered, self).__init__(msg)


class InjectorAlreadyRegistered(Exception):
    
    '''InjectorAlreadyRegistered is raised when the second injector
    is registered. It prevets one injector from overriding another.
    '''
    
    def __init__(self, another):
        msg = 'Another injector %r is already registered. ' % another
        msg += 'There can be only one registered injector.'
        super(InjectorAlreadyRegistered, self).__init__(msg)


class NotBoundError(KeyError):
    
    '''NotBoundError extends KeyError, is raised when there is no binding
    for a given type.
    '''
    
    def __init__(self, key):
        msg = 'No binding for %s, use injector.bind to bind it.' \
            % str(key)
        super(NotBoundError, self).__init__(msg)


class FactoryNotBoundError(Exception):
    
    '''FactoryNotBound is raised when a not bound factory is accessed.'''
    
    def __init__(self, type):
        msg = 'No factory is bound for %r.' % type
        super(FactoryNotBoundError, self).__init__(msg)


class FactoryNotCallable(Exception):
    
    '''FactoryNotCallable is raised when a non-callable is bound as a factory.'''
    
    def __init__(self, factory):
        msg = 'Factory must be callable, got: %r.' % factory
        super(FactoryNotCallable, self).__init__(msg)


class AutobindingFailed(Exception):
    
    '''AutobindingFailed is raised when an injector has failed
    to autobind a type.
    ''' 
    
    def __init__(self, type, caused_by):
        msg = u'Autobinding of %r failed because of %r' % (type, caused_by)
        return super(AutobindingFailed, self).__init__(msg)


class NoRequestError(Exception):
    
    '''NoRequestError is raised when a request scope is accessed
    but no request is present.
    '''
    
    def __init__(self):
        msg = 'No request is started, use reqscope.start() to init a new request.'
        super(NoRequestError, self).__init__(msg)


class MultipleAttrsFound(Exception):
    
    '''MultipleAttrsFound is raised when multiple attributes are found
    for the same value.
    
    This exception is raised by AttributeInjection when it finds multiple
    attributes for its value.
    '''


class NoAttrFound(Exception):
    
    '''NoAttrFound is raised when no attribute is found for a given value.
    
    This exception is raised by AttributeInjection when it fails to find
    an attribute with its value.
    '''


class NoParamError(Exception):
    
    '''NoParamError is raised when you inject a param into a function,
    but the function does not accept such a param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''
