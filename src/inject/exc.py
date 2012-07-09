'''Dependency injection exceptions.'''


class NoInjectorRegistered(Exception):
    
    '''No injector registered.'''
    
    def __init__(self):
        msg = 'Injector must be registered.' \
            'Use injector=Injector.create(), or injector=Injector(); ' \
            'injector.register().'
        super(NoInjectorRegistered, self).__init__(msg)


class InjectorAlreadyRegistered(Exception):
    
    '''Injector cannot override another registered one.'''
    
    def __init__(self, another):
        msg = 'Another injector %r is already registered. ' % another
        msg += 'There can be only one registered injector. '
        msg += 'Please, unregister the first one.'
        super(InjectorAlreadyRegistered, self).__init__(msg)


class NotBoundError(Exception):
    
    '''No binding for a given type (and autobinding is turned off).'''
    
    def __init__(self, key):
        msg = 'No binding for %s, use injector.bind to bind it, '\
            'or set injector.autobind to true.' % str(key)
        super(NotBoundError, self).__init__(msg)


class FactoryNotCallable(Exception):
    
    '''Factory is not a callable.'''
    
    def __init__(self, factory):
        msg = 'Factory must be callable, got: %r.' % factory
        super(FactoryNotCallable, self).__init__(msg) 


class AutobindingFailed(Exception):
    
    '''Injector has failed to autobind a type.''' 
    
    def __init__(self, type, caused_by):
        msg = 'Autobinding of %r failed because of %r' % (type, caused_by)
        return super(AutobindingFailed, self).__init__(msg)


class NoRequestError(Exception):
    
    '''No request has been started.'''
    
    def __init__(self):
        msg = 'No request has been started, use reqscope.start() to init a new request.'
        super(NoRequestError, self).__init__(msg)


class MultipleAttrsFound(Exception):
    
    '''Multiple instance attributes are found for the same value.
    
    It is raised by L{inject.attr} when it finds multiple attributes for
    its property.
    '''


class NoAttrFound(Exception):
    
    '''No attribute is found for a given value.
    
    It is raised by L{inject.attr} when it does not find an attribute
    for it property.
    '''


class NoParamError(Exception):
    
    '''Function does not accept an injected param.
    
    For example::
        
        @inject.param('key', dict) # No param "key".
        def func(arg):
            pass
    
    '''
