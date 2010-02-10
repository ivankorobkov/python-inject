'''C{inject} is a python dependency injection tool. It is created specifically
for Python and tries to utilize its advantages. C{inject} aims at:

    - Simplifying complex projects development.
    - Providing loose-coupling for components.
    - Instantiating and reusing objects according to their scopes.
    - Testability.
    - Advanced in-code configuration.

B{Requirements:}
Python 2.4+, and Python2.5+ for request middleware. Python 3+ is not supported.

B{Links:}

    - Project's site: http://code.google.com/p/python-inject
    - User's Guide: http://code.google.com/p/python-inject/wiki/UsersGuide
    - Source code: http://github.com/ivan-korobkov/python-inject

B{Installation}
Run::
    setup.py install
Or, if you have setuptools, you can install it directly from PyPi::
    easy_install inject

Example
=======
Import C{inject} and use it to inject required object into other objects.
No configuration is required.::

    import inject
    
    @inject.appscope        # The default scope.
    class A(object): pass
    class B(object): pass
    
    class C(object):
    
        a = inject.attr('a', A)    # Inject a descriptor.
        
        # Inject a param into a function.
        @inject.param('b', B, scope=inject.reqscope):
        def __init__(self, b):
            self.b = b
    
    c = C()

If you need advanced configuration, create an instance of C{Injector},
register it using C{inject.register} and add bindings to it.:::
    
    import inject
    
    injector = inject.Injector()
    inject.register(injector)
    
    
    class A(object): pass
    class B(object): pass
    
    class C(object):
    
        a = inject.attr('a', A)
        
        @inject.param('b', B):
        def __init__(self, b):
            self.b = b
    
    c = C()
    
    
    injector.bind(A, to=A, scope=


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