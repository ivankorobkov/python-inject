'''Utilities for imports.'''
from inject.functional import update_wrapper


class LazyImport(object):
    
    '''LazyImport is a wrapper around the lazy_import method, which
    lazily imports objects on the hash and equality methods calls.
    
    It is used inside the InjectionPoint, so it executes imports only
    on injection requests.
    '''
    
    __slots__ = ('imp', '_obj')
    
    def __init__(self, name, globals=None):
        self.imp = lazy_import(name, globals)
        self._obj = None
    
    def __hash__(self):
        return hash(self.obj)
    
    def __eq__(self, other):
        return self.obj == other
    
    def __ne__(self, other):
        return self.obj != other
    
    def _get_obj(self):
        if self._obj is None:
            self._obj = self.imp()
        return self._obj
    
    obj = property(_get_obj)


def lazy_import(name, globals=None):
    '''Return a function which 1) lazily references a global object if the name
    starts with a dot, 2) lazily imports an object in the name contains a dot,
    3) otherwise returns a string.
    
    Examples::
        
        lazy_import('.MyClass', globals()) => lazy reference to a global object.
        lazy_import('..mymodule.MyClass') => from ..mymodule import MyClass
        lazy_import('span.eggs') => from spam import eggs.
        lazy_import('database_host') => a string "database_host".
    
    @raise ImportError: if a global reference or an imported object is not found.
    '''
    def func():
        obj = None
        if globals is not None and \
            name.startswith('.') and \
            not name.startswith('..'):
            # Lazy global reference.
            
            key = name.strip('.')
            if key in globals:
                obj = globals[key]
            else:
                raise ImportError('No object named %s.' % key)
        
        elif '.' in name:
            # Normal import.
            modname, objname = name.rsplit('.', 1)
            
            obj = __import__(modname, globals, {}, [], -1)
            try:
                attrs = modname.split('.')[1:]
                attrs.append(objname)
                
                for attr in attrs:
                    obj = getattr(obj, attr)
            
            except AttributeError:
                raise ImportError('No module named %s.' % name)
        
        else:
            # String without dots.
            obj = name
        
        func.obj = obj
        return func.obj
    
    update_wrapper(func, lazy_import)
    return func
