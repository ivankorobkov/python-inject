Dependency injection the python way, the good way. Not a port of Guice or Spring.

Key features
============
- Simple to use.
- Extremely fast.
- Thread-safe.
- Does not steal class constructors.
- Does not try to manage your application object graph.
- Injects dependencies everywhere via ``inject.instance(MyClass)``.
- Injects dependencies as class attributes via ``inject.attr(MyClass)``.
- Transparently integrates into tests.
- Supports Python 2.7 and Python 3.3+.

Usage
=====
Install from PyPI::

    pip install inject

Create an optional configuration::

    def my_config(binder):
        binder.bind(Cache, RedisCache('localhost:1234'))
        binder.bind_to_provider(CurrentUser, get_current_user)

Create a shared injector::

    inject.configure(my_config)

Use ``inject.instance`` or ``inject.attr`` to inject dependencies::

    class User(object):
        cache = inject.attr(Cache)

        @classmethod
        def load(cls, id):
            return cls.cache.load('user', id)

        def save(self):
            self.cache.save(self)

    def foo(bar):
        cache = inject.instance(Cache)
        cache.save('bar', bar)

Testing
=======
In tests use ``inject.clear_and_configure(callable)`` to create a new injector on setup,
and optionally ``inject.clear()`` to clean-up on tear down::
    
    class MyTest(unittest.TestCase):
        def setUp(self):
            inject.clear_and_configure(lambda binder: binder
                .bind(Cache, Mock() \
                .bind(Validator, TestValidator())
        
        def tearDown(self):
            inject.clear()


Thread-safety
=============
After configuration the injector is thread-safe and can be safely reused by multiple threads.

Binding types
=============
- Instance bindings configured via `bind(cls, instance) which always return the same instance.
- Constructor bindings `bind_to_constructor(cls, callable)` which create a singleton
  on first access.
- Provider bindings `bind_to_provider(cls, callable)` which call the provider
  for each injection.
- Runtime bindings which automatically create class singletons.

Runtime bindings
================
Runtime bindings greatly reduce the required configuration by automatically creating singletons
on first access. For example, below only the ``Config`` class requires binding configuration, 
all other classes are runtime bindings::

    class Config(object):
        pass
    
    class Cache(object):
        config = inject.attr(Config)
    
    class Db(object):
        config = inject.attr(Config)
    
    class User(object):
        cache = inject.attr(Cache)
        db = inject.attr(Db)
        
        @classmethod
        def load(cls, user_id):
            return cls.cache.load('users', user_id) or cls.db.load('users', user_id)
     
    def my_config(binder):
        binder.bind(Config, load_config_file())
    
    inject.configure(my_config)
    user = User.load(10)

Why no scopes?
==============
I've used Guice and Spring in Java for a lot of years, and I don't like their scopes.
``python-inject`` by default creates objects as singletons. It does not need a prototype scope
as in Spring or NO_SCOPE as in Guice because ``python-inject`` does not steal your class 
constructors. Create instances the way you like and then inject dependencies into them.

Other scopes such as a request scope or a session scope are fragile, introduce high coupling,
and are difficult to test. In ``python-inject`` write custom providers which can be thread-local, 
request-local, etc.

License
=======
Apache License 2.0
