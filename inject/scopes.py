import threading


class Interface(object):
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        pass
    
    def __call__(self, obj):
        '''Decorate an object so that it is instantiated using the scope.'''
        pass


class Abstract(Interface):
    
    def __call__(self, obj):
        '''Decorate an object so that it is instantiated using the scope.'''
        obj._inject_scope = self


class No(Abstract):
    
    '''NoScope is a dummy object which exists only to distinguish between
    None and "No Scope"
    '''
    
    pass


class App(dict, Abstract):
    
    def scope(self, provider):
        '''Return a scoped provider (a callable).'''
        def scopedprovider():
            if provider in self:
                return self[provider]
            
            inst = provider()
            self[provider] = inst
            return inst
        
        return scopedprovider


class NoRequestRegisteredError(Exception):
    
    '''NoRequestError is raised when request scope is accessed but not request
    is registered.
    '''
    

class Request(threading.local, Abstract):
    
    '''RequestScope is a request-local thread-local scope.'''
    
    cache = None
    
    def register(self, environ):
        self.cache = {}
    
    def unregister(self):
        del self.cache
    
    def get(self, provider):
        '''Return an instance for a provider.
        
        If the instance does not exist call the provider to get one.
        '''
        def scopedprovider():
            cache = self.cache
            if cache is None:
                raise NoRequestRegisteredError()
            
            if provider in cache:
                return cache[provider]
            
            inst = provider()
            cache[provider] = inst
            return inst
        
        return scopedprovider


no = No()
app = App()
request = Request()