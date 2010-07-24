'''Utility functions.'''


def get_attrname_by_value(obj, attrvalue):
    '''Return a name for an attribute by it value, or raise ValueError.
    
    The function iterates over instance's __dict__.
    '''
    for name, value in obj.__dict__.iteritems():
        if value is attrvalue:
            return name
    
    raise ValueError('Can\'t find an attribute in %r with the value %r.'
                      % (obj, value))
