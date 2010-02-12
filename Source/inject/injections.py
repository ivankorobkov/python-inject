'''Injections are real dependency injection methods: an attribute descriptor,
and a function decorator.
'''
from inject import errors
from inject.injection import Injection
from inject.functional import update_wrapper


'''
@var super_param: empty object which is used to specify that a param 
    is injected in a super class.
'''
super_param = object()


class Attr(object):
    
    '''Attribute injection is a descriptor, which injects an instance into
    a specified class attribute.
    
    Example::
        
        class A(object): pass
        class B(object):
            a = Attr('a', A)
    
    '''
    
    injection_class = Injection
    
    def __init__(self, attr, type=None, annotation=None, bindto=None,
                 scope=None):
        '''Create an injection for an attribute.
        
        If type is not given (None), type = attr.
        '''
        if type is None:
            type = attr
        self.attr = attr
        self.injection = self.injection_class(type, annotation, bindto=bindto,
                                              scope=scope)
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        obj = self.injection.get_instance()
        
        setattr(instance, self.attr, obj)
        return obj


class Param(object):
    
    '''Param injection is a function decorator, which injects the required
    non-given params directly into a function, passing them as keyword args.
    
    Set an argument to C{super_param} to indicate that it is injected in
    a super class.
    
    Example::
        
        class A(object): pass
        class B(object):
            @Param('a', A)
            def __init__(self, a):
                self.a = a
        
        class C(B):
            @Param('a2', A):
            def __init__(self, a2, a=super_param):
                super(C, self).__init__(a)
                self.a2 = a2
        
    '''
    
    injection_class = Injection
    
    def __new__(cls, name, type=None, annotation=None, bindto=None,
                scope=None):
        '''Create an injection for a param.
        
        If type is not given (None), type = name.
        '''
        if type is None:
            type = name
        
        injection = cls.injection_class(type, annotation, scope=scope,
                                        bindto=bindto)
        
        def decorator(func):
            if getattr(func, 'injection_wrapper', False):
                # It is already a wrapper.
                wrapper = func
            else:
                wrapper = cls.create_wrapper(func)
            cls.add_injection(wrapper, name, injection)
            return wrapper
        
        return decorator
    
    @classmethod
    def create_wrapper(cls, func):
        injections = {}
        
        def injection_wrapper(*args, **kwargs):
            '''Injection wrapper gets non-existent keyword arguments
            from injections, combines them with kwargs, and passes to
            the wrapped function.
            '''
            for name in injections:
                if name in kwargs and kwargs[name] is not super_param:
                    continue
                
                injection = injections[name]
                kwargs[name] = injection.get_instance()
            
            return func(*args, **kwargs)
        
        # Store the attributes in a wrapper for other functions.
        # Inside the wrapper access them from the closure.
        # It is about 10% faster.
        injection_wrapper.func = func
        injection_wrapper.injections = injections
        injection_wrapper.injection_wrapper = True
        update_wrapper(injection_wrapper, func)
        
        return injection_wrapper
    
    @classmethod
    def add_injection(cls, wrapper, name, injection):
        func = wrapper.func
        func_code = func.func_code
        flags = func_code.co_flags
        
        if not flags & 0x04 and not flags & 0x08:
            # 0x04 func uses args
            # 0x08 func uses kwargs
            varnames = func_code.co_varnames
            if name not in varnames:
                raise errors.NoParamError(
                    '%s does not accept an injected Param "%s".' %
                    (func, name))
        
        wrapper.injections[name] = injection