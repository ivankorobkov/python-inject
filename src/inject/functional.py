'''Functools not preset in Python2.4.'''
try:
    from functools import update_wrapper #@UnusedImport
except ImportError:
    # Python2.5-
    def update_wrapper(wrapper, wrapped):
        '''Set wrappers's name, module, doc and update its dict.'''
        wrapper.__name__ = wrapped.__name__
        wrapper.__module__ = wrapped.__module__
        wrapper.__doc__ = wrapped.__doc__        
        wrapper.__dict__.update(wrapped.__dict__)
        return wrapper