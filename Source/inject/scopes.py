'''Scopes configure how objects are instantiated and reused.

By default, a new instance is injected every time. Application scope creates
only one instance of a class (a provider) for the whole application. Request 
scope creates unique instances for each HTTP request. Request scope stores
values in a thread-local request-local manner.

C{noscope} can be used to explicitly specify creating new instances for every
injection request.
'''
import threading

from inject import errors
from inject.injections import Attr, Param
from inject.invoker_ import Invoker

'''
@var SCOPE_ATTR: Constant, an attribute name which is used to store a scope 
    in a decorated object.
'''
SCOPE_ATTR = '_inject_scope'


class Interface(object):
    
    '''Scope interface.'''
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        pass
    
    def __call__(self, obj):
        '''Decorate an object so that it is instantiated inside the scope.'''
        pass


class Abstract(Interface):
    
    '''Abstract scope which implements the __call__ method (decorator)
    and scoped injections.
    '''
    
    attr_class = Attr 
    param_class = Param
    invoker_class = Invoker
    
    def __call__(self, obj):
        '''Decorate an object so that it is instantiated inside the scope.'''
        setattr(obj, SCOPE_ATTR, self)
        return obj
    
    def inject_attr(self, attr, type=None, annotation=None, bindto=None):
        '''Create a scoped injection descriptor for an attribute.
        
        If type is not given (None), type = attr.
        '''
        return self.attr_class(attr=attr, type=type, annotation=annotation,
                               bindto=bindto, scope=self)
    
    def inject_param(self, name, type=None, annotation=None, bindto=None):
        '''Create a scoped injection for a param.
        
        If type is not given (None), type = name.
        '''
        return self.param_class(name=name, type=type, annotation=annotation,
                                bindto=bindto, scope=self)
    
    def invoker(self, func):
        '''Create a scoped invoker.'''
        return self.invoker_class(func, scope=self)


class No(Abstract):
    
    '''NoScope is a dummy object which exists only to distinguish between
    None and "No Scope"
    '''
    
    pass


class Application(dict, Abstract):
    
    '''Application scope caches instances for the whole application,
    in other injectors it is usually called a singleton.
    '''
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        def scopedprovider():
            if provider in self:
                return self[provider]
            
            inst = provider()
            self[provider] = inst
            return inst
        
        return scopedprovider
    
    def __repr__(self):
        return '<%s at %s>' % (self.__class__.__name__, hex(id(self)))
    

class Request(threading.local, Abstract):
    
    '''RequestScope is a request-local thread-local scope which caches
    instances for each WSGI request.
    
    To use it register and unregister the requests, usually using try/finally.
    For example::
    
        def myapp(environ, startresponse):
            reqscope.register(environ)
            try:
                startresponse()
                return 'Response'
            finally:
                reqscope.unregister(environ)
    
    '''
    
    cache = None
    
    def register(self):
        '''Register a request using a wsgi environment.'''
        self.cache = {}
    
    def unregister(self):
        '''Unregister a request.'''
        del self.cache
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        def scopedprovider():
            cache = self.cache
            if cache is None:
                raise errors.NoRequestRegisteredError()
            
            if provider in cache:
                return cache[provider]
            
            inst = provider()
            cache[provider] = inst
            return inst
        
        return scopedprovider


no = No()
app = Application()
req = Request()