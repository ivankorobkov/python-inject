'''C{inject} is a fast python dependency injection tool. It uses decorators and 
descriptors to reference external dependencies, and scopes (Guice-inspired) to 
specify how to reuse objects. Dependencies can be referenced by types and 
optional annotations. No configuration is required, but advanced in-code 
configuration is possible.

Most other python dependency injection tools, such as PyContainer or Spring 
Python, are ports from other languages (Java). So they are based on dependency 
injection ways specific for statically typed languages, described by Martin 
Fowler.

Python is not Java. Patterns and programming techniques, which seem proper and 
usable in one language, can be awkward in another. `Inject` has been created to 
provide a _pythonic_ way of dependency injection, utilizing specific Python 
functionality. Terminology used in `inject` has been intentionally made similar
to Guice, however the internal architecture is different.

Links
=====

    - Project's site: U{http://code.google.com/p/python-inject}
    - User's Guide: U{http://code.google.com/p/python-inject/wiki/UsersGuide}
    - Tutorial: U{http://code.google.com/p/python-inject/wiki/Tutorial}
    - API: U{http://api.python-inject.googlecode.com/hg/html/index.html}
    - Source code: U{http://github.com/ivan-korobkov/python-inject}


Short Tutorial
==============
See the I{Examples} directory and I{User's Guide} for more information.

Import C{inject} and use it to inject an class instance into other objects.
No configuration is required.::

    import inject
    
    @inject.appscope        # The default scope.
    class A(object): pass
    class B(object): pass
    
    class C(object):
    
        a = inject.attr('a', A)    # Inject a descriptor.
        
        # Inject a param into a function.
        @inject.param('b', B, scope=inject.appscope):
        def __init__(self, b):
            self.b = b
    
    c = C()

If you need advanced configuration, create an instance of L{Injector},
B{register} it using L{inject.register} and add bindings to it.::
    
    import inject
    
    injector = inject.Injector()
    inject.register(injector)    # Register the injector!!!
    
    
    class A(object): pass
    class B(object): pass
    class C(object): pass
    
    class D(object):
    
        a = inject.attr('a', A)
        b = inject.attr('b', B, annotation='some_text')
        
        @inject.param('b', B)
        @inject.param('c', C):
        def __init__(self, b, c):
            self.b = b
            self.c = c
    
    class B2(object): pass
    @inject.appscope
    class C2(object): pass
    
    injector.bind(A, scope=inject.appscope)
    # Inject B2 when B is required only when it is annotated with "some_text".  
    injector.bind(B, annotation='some_text', to=B2)
    injector.bind(C, to=C2, scope=inject.noscope) # Override the default scope.
    
    d = D()
    
    
Use C{inject.super} as the default value, if it is injected in a super class.
Always pass the super injected params as keyword arguments.::
    
    class Z(object): pass
    
    class D2(object):
        
        @inject.param('z', Z)
        def __init__(self, z, b=inject.super, c=inject.super):
            super(D2, self).__init__(b=b, c=c)
            self.z = z
    
    d2 = D2()


Request scope (L{scopes.Request}) is a thread-local request-local scope. 
It allows to instantiate classes only once per request. To use it in a WSGI 
application, wrap your application with L{WsgiInjectMiddleware}.

To use it with Django, insert L{DjangoInjectMiddleware} into the middleware
tuple in C{settings.py}. It is recommended to insert it as the first item.


@author: Ivan Korobkov <ivan.korobkov@gmail.com>
@copyright: 2010 Ivan Korobkov
@license: MIT License, see LICENSE
@version: 1.0
'''
__version__ = '1.0'


from inject.injections import Attr as attr, \
    Param as param, \
    super_param as super
from inject.injector import Injector, register, unregister
from inject.invoker_ import Invoker as invoker
from inject.scopes import \
    no as noscope, \
    app as appscope, \
    req as reqscope