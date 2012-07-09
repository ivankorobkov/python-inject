'''Injections fetch bindings from an injector.
L{inject.attr <AttributeInjection>}, L{inject.named_attr <NamedAttributeInjection>}
and L{inject.class_attr <ClassAttributeInjection>} are descriptors which can
be used inside classes, while L{inject.param <ParamInjection>} is a function
decorator.

Injections comparison
=====================

C{inject.attr}
--------------
L{AttributeInjection} can be accessed B{only inside bound methods}, it gets 
a binding once for each instance, then finds its attribute name,
and sets instance's attribute to the binding. All subsequent accesses
of the instance's attribute does not require dependency injection.

B{This injection can be affected by scope-widening problems}, i.e. when
a request-scoped (or other narrow-scoped) object is injected into
an application-scoped object. For example, when a request-scoped C{User}
is injected into some application-scoped C{MailService}.

To prevent such problems never inject narrow-scoped objects into wide-scoped
objects or (if you have to) use L{inject.class_attr <ClassAttributeInjection>}
or L{inject.param <ParamInjection>}.

Example::
    
    class A(object): pass
    class B(object):
        a = inject.attr(A)
    
    b = B()
    b.a # A is fetched from the injector and set as b's attribute.
    b.a # Only an attribute is accessed, no injection is performed.


C{inject.named_attr}
--------------------
L{NamedAttributeInjection} subclasses L{AttributeInjection} and requires
an attribute name. It can be useful when metaclasses or other magic prevents
L{AttributeInjection} from autodetecting its attribute name.

B{This injection can be affected by scope-widening problems}. 

Example::
    
    class A(object): pass
    class B(object):
        a = inject.named_attr('a', A)


C{inject.class_attr}
--------------------
L{ClassAttributeInjection} can be accessed both inside B{class and}
B{bound methods}. It does not set any class's or instance's attribute
so every time it is accessed an injection is performed.

This injection is not affected by scope-widening problems because
it injects a binding every time it is accessed.

Example::

    class A(object): pass
    class B(object):
        a = inject.class_attr(A)
        
        @classmethod
        def cls_print_a(cls):
            a = cls.a
            print a
        
        def print_a(self):
            a = cls.a
            print
    
    B.cls_print_a()
    b = B()
    b.print_a()


C{inject.param}
---------------
L{ParamInjection} injects a binding into a function or a method every time
it is called.

This injection is not affected by scope-widening problems.

Example::
    
    class A(object): pass
    class B(object): pass
    
    @inject.param('a', A)
    @inject.param('b', B)
    def my_func(a, b):
        print a, b
    
    my_func()

'''
from functools import update_wrapper

from inject.exc import NoParamError
from inject.injectors import get_instance as _get_instance
from inject.utils import get_attrname_by_value


'''
@var super_param: empty object which is used to specify that a param 
    is injected in a super class.
'''
super_param = object()


class InjectionPoint(object):
    
    '''InjectionPoint serves injection requests.'''
    
    __slots__ = ('type', 'none')
    
    def __init__(self, type, none=False):
        self.type = type
        self.none = none
    
    def get_instance(self):
        '''Return an instance for the injection point type.'''
        return _get_instance(self.type, none=self.none)


class AttributeInjection(object):
    
    '''AttributeInjection is a descriptor, which injects an instance into
    an attribute.
    
    B{Alias}: C{attr}.
    
    Example::
        
        class A(object): pass
        class B(object):
            a = attr(A)
    
    @see: L{inject.injections} for injections comparisons and detailed
        description.
    
    '''
    
    def __init__(self, type, none=False):
        '''Create an injection for an attribute.'''
        self.attr = None
        self.injection = InjectionPoint(type, none)
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        attr = self.attr
        if attr is None:
            attr = self._get_set_attr(owner)
        
        obj = self.injection.get_instance()
        setattr(instance, attr, obj)
        return obj
    
    def _get_set_attr(self, owner):
        attr = get_attrname_by_value(owner, self)
        self.attr = attr
        return attr


class NamedAttributeInjection(AttributeInjection):
    
    '''NamedAttributeInjection is a descriptor, which injects a dependency into
    a specified instance attribute.
    
    B{Alias}: C{named_attr}.
    
    Example::
        
        class A(object): pass
        class B(object):
            a = named_attr('a', A)
    
    @see: L{inject.injections} for injections comparisons and detailed
        description.
    
    '''
    
    def __init__(self, attr, type, none=False):
        '''Create an injection for an attribute.'''
        super(NamedAttributeInjection, self).__init__(type, none)
        self.attr = attr


class ClassAttributeInjection(object):
    
    '''ClassAttributeInjection is a class descriptor, which resolves
    a dependency every time it is accessed.
    
    B{Alias}: C{class_attr}.
    
    @see: L{inject.injections} for injections comparisons and detailed
        description.
    
    '''
    
    point_class = InjectionPoint
    
    def __init__(self, type, none=False):
        self.injection = InjectionPoint(type, none)
    
    def __get__(self, instance, owner):
        return self.injection.get_instance()


class ParamInjection(object):
    
    '''ParamInjection is a function decorator, which injects the required
    non-given params directly into a function, passing them as keyword args.
    
    B{Alias}: C{param}
    
    Set an argument to C{super_param} to indicate that it is injected in
    a super class.
    
    Example::
        
        class A(object): pass
        class B(object):
            @param('a', A)
            def __init__(self, a):
                self.a = a
        
        class C(B):
            @param('a2', A):
            def __init__(self, a2, a=super_param):
                super(C, self).__init__(a)
                self.a2 = a2
    
    @see: L{inject.injections} for injections comparisons and detailed
        description.
    
    '''
    
    def __new__(cls, name, type=None, none=False):
        '''Create a decorator injection for a param.'''
        if type is None:
            type = name
        
        injection = InjectionPoint(type, none)
        
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
            '''InjectionPoint wrapper gets non-existent keyword arguments
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
        func_code = func.__code__
        flags = func_code.co_flags
        
        if not flags & 0x04 and not flags & 0x08:
            # 0x04 func uses args
            # 0x08 func uses kwargs
            varnames = func_code.co_varnames
            if name not in varnames:
                raise NoParamError(
                    '%s does not accept an injected param "%s".' % 
                    (func, name))
        
        wrapper.injections[name] = injection


attr = AttributeInjection
named_attr = NamedAttributeInjection
class_attr = ClassAttributeInjection
param = ParamInjection
