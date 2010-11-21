'''Utility functions.'''
import inspect


class MultipleAttrsFound(Exception):
    
    pass


class NoAttrFound(Exception):
    
    pass


def get_attrname_by_value(obj, attrvalue):
    '''Return a name for an attribute by it value, or raise ValueError.
    
    The function iterates over instance's __dict__.
    '''
    def _get(items):
        attrname = None
        multiple = False
        
        for name, value in items:
            if value is not attrvalue:
                continue
            
            if attrname is not None:
                if not isinstance(attrname, list):
                    attrname = [attrname]
                    multiple = True
                attrname.append(name)
            else:
                attrname = name
        
        if multiple:
            raise MultipleAttrsFound('Multiple attributes %r found for '
                    'attrvalue %r in %r.' % (attrname, attrvalue, obj))
        
        return attrname
    
    attrname = _get(obj.__dict__.iteritems())
    if attrname is not None:
        return attrname
    
    # Fallback to a slow way.
    attrname = _get(inspect.getmembers(obj))
    if attrname is not None:
        return attrname
    
    raise NoAttrFound('Can\'t find an attribute in %r with the value %r.'
                      % (obj, attrvalue))
