'''C{inject} is a python dependency injection tool. It is created specifically
for Python and tries to utilize its advantages. C{inject} aims at:

    - Simplifying complex projects development.
    - Providing loose-coupling for components.
    - Instantiating and reusing objects according to their scopes.
    - Testability.
    - Advanced in-code configuration.

B{Requirements:}
Python 2.4+, and Python2.5+ for WSGI and Django middleware. Python 3+ is not 
supported.

B{Links:}

    - Project's site: http://code.google.com/p/python-inject
    - User's Guide: http://code.google.com/p/python-inject/wiki/UsersGuide
    - Source code: http://github.com/ivan-korobkov/python-inject

B{Installation}

Run::
    setup.py install
Or, if you have setuptools, you can install it directly from PyPi::
    easy_install inject

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
application, wrap your application with L{WsgiInjectMiddleware}

To use it with Django, insert L{DjangoInjectMiddleware} into the middleware
tuple in C{settings.py}. It is recommended to insert it as the first item.

See the documented code in the I{Examples} folder for a web tutorial.

'''


from inject.injections import Attr as attr, \
    Param as param, \
    super_param as super
from inject.injector import Injector, register, unregister
from inject.invoker_ import Invoker as invoker
from inject.scopes import \
    no as noscope, \
    app as appscope, \
    req as reqscope