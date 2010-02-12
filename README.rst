``Inject`` is a fast python dependency injection tool. It uses decorators and 
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

License
=======
MIT License, see LICENSE.

Links
=====
- Project's site: http://code.google.com/p/python-inject
- User's Guide:   http://code.google.com/p/python-inject/wiki/UsersGuide
- Tutorial:       http://code.google.com/p/python-inject/wiki/Tutorial
- API:            http://api.python-inject.googlecode.com/hg/html/index.html
- Source code:    http://github.com/ivan-korobkov/python-inject

Example
=======
::

    import inject
    
    @inject.appscope
    class Config(object): pass
    class A(object): pass
    class B(object): pass
    
    class C(object):
        
        config = inject.attr('config', Config)
        a = inject.attr('a', A)
    
        @inject.param('b', B):
        def __init__(self, b):
            self.b = b
    
    c = C()

Key features
============
- Fast, only 2-3 times slower that direct instantiation.
- Normal way of instantiating objects, ``Class(*args, **kwargs)``.
- Injecting arguments into functions and methods.
- Referencing dependencies by types and optional annotations.
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