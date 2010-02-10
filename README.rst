Overview
========
``Inject`` is a python dependency injection tool. It is created specifically 
for Python and tries to utilize its advantages. ``Inject`` aims at:

- Simplifying complex projects development.
- Providing loose-coupling for components.
- Instantiating and reusing objects according to their scopes.
- Testability.
- Advanced in-code configuration.

**Requirements:**
Python 2.4+, and Python2.5+ for request middleware. Python 3+ is not supported.

**Links:**

- Project's site: http://code.google.com/p/python-inject
- User's Guide: http://code.google.com/p/python-inject/wiki/UsersGuide
- Source code: http://github.com/ivan-korobkov/python-inject

Example
=======
::

    import inject
    
    class A(object): pass
    class B(object): pass
    
    class C(object):
    
        a = inject.attr('a', A)
    
        @inject.param('b', B):
        def __init__(self, b):
            self.b = b
    
    c = C()

Key features
============
- Fast, comparable to direct object instantiation.
- Normal way of instantiating objects, ``Class(*args, **kwargs)``.
- Injecting arguments into functions and methods.
- Binding to callables, instances and unbound methods (see [nvokers).
- Request scope middleware for WSGI and Django applications (requires 
  Python2.5+).
- No configuration required at all.
- Advanced flexible configuration possible::
    
    injector.bind(Class, to=Class2)
    injector.bind(Database, annotation='user', to=UsersDatabase,
                  scope=appscope)
    injector.bind('app_started_at', to=datetime.now())
    injector.bind('some_var', to=Class.unbound_method)

- Two injection methods, a descriptor and a decorator::
    
    class My(object):
        attr = inject.attr('attr', Class2)
    
    @inject.param('param', Class2):
    def myfunc(param):
        pass
       
- Support for inheritance by passing ``inject.super`` as the default kwarg 
  value::
    
    class My(object):
        @inject.param('param1', Class1)
        def __init__(self, param1):
            self.param1 = param1
    
    class My2(My):
        @inject.param('param2', Class2)
        def __init__(self, param2, param1=inject.super):
            super(My2, self).__init__(param1=param1)
            self.param2 = param2

- Invokers to call unbound methods (cool for listeners)::
    
    class My(object):
        def get_data(self):
            pass
    
    # Create an invoker, which calls an unbound method.
    invoker = inject.invoker(My.get_data)
    data = invoker()
    
    # Bind directly to an unbound method.
    @inject.param('data', My.get_data)
    def func(data):
        pass
       
- Partial injections, when only some arguments are injected::
    
    @inject.param('logger', Logger)
    def mylog(msg, logger):
        pass
    
    mylog('My message')
       
- Scopes: application (singleton), request, noscope::
    
    class Controller(object):
        session = inject.attr('session', Session, scope=reqscope)
    
    # or in configuration
    injector.bind(Session, to=Session, scope=reqscope)
    
    # or set the default scope
    @reqscope
    class Session(object):
        pass
    
    @appscope
    class DatabasePool(object):
        pass
       
- Easy integration into existing projects.