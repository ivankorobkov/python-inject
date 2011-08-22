'''Lazy importing and referencing.'''
import sys
from functools import update_wrapper


def _get_caller_globals():
    '''Return an injection caller globals or an empty dict.
    
    This is an internal function which is used to get C{global} required
    by the L{lazy_import} function. It uses CPython C{sys._getframe} function,
    and can fail to work on other implementations.
    '''
    b_frame = sys._getframe(2)
    if b_frame:
        return b_frame.f_globals
    return {}


class LazyImport(object):
    
    '''LazyImport is a wrapper around the L{lazy_import} function, it delegates
    hash and equality methods to the imported object.
    
    It is guaranteed to work only with CPython.
    '''
    
    __slots__ = ('name', 'imp', '_obj')
    
    def __init__(self, name):
        globals = _get_caller_globals()
        
        self.name = name
        self.imp = lazy_import(name, globals)
        self._obj = None
    
    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, self.name)
    
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


def lazy_import(name, globals):
    '''Return a closure (function) which 1) lazily references a global object,
    or 2) lazily imports an object.
    
    Examples::
        
        lazy_import('MyClass', globals()) => a lazy reference to a global object.
        lazy_import('..mymodule.MyClass', None) => from ..mymodule import MyClass
        lazy_import('span.eggs', None) => from spam import eggs.
    
    @raise ImportError: if a global reference or an imported object is not found.
    '''
    def func():
        obj = None
        if '.' not in name:
            # Global reference.
            if globals and name in globals:
                obj = globals[name]
            else:
                raise ImportError('No local object named %s.' % name)
        
        else:
            # Import.
            modname, objname = name.rsplit('.', 1)
            
            obj = __import__(modname, globals, {}, [], -1)
            try:
                attrs = modname.split('.')[1:]
                attrs.append(objname)
                
                for attr in attrs:
                    obj = getattr(obj, attr)
            
            except AttributeError:
                raise ImportError('No module named %s.' % name)
        
        func.obj = obj
        return func.obj
    
    update_wrapper(func, lazy_import)
    return func


'''
@var lazy: L{LazyImport} alias.
'''
lazy = LazyImport
