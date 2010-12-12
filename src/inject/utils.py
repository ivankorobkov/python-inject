'''Utility functions.'''
import inspect
from inject.exc import MultipleAttrsFound, NoAttrFound


def get_attrname_by_value(obj, attrvalue):
    '''Return a name for an attribute by its value.
    
    The function is used to find an attribute name by an injection descriptor
    object. It first iterates over instance's __dict__, then fallbacks to
    {inspect.getmembers()}.
    
    For example:
    
        >>> class A(object):
        >>>    a = 'myvalue'
        >>> get_attrname_by_value('myvalue')
        'a'
        >>>
    
    @raise MultipleAttrsFound: If multiple attributes are found for a given value.
    @raise NoAttrFound: If not attribute is found for a given value.
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
