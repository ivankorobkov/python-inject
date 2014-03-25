python-inject
=============
Dependency injection the python way, the good way. Not a port of Guice or Spring.

Key features
------------
- Fast.
- Thread-safe.
- Simple to use.
- Does not steal class constructors.
- Does not try to manage your application object graph.
- Transparently integrates into tests.
- Supports Python 2.7 and Python 3.3+.


Usage
-----
Installation::

    pip install inject

Example::

    # Import the inject module.
    import inject
    
    # `inject.param` injects dependencies as keyword arguments.
    @inject.param('cache', Cache)
    def bar(foo, cache=None):
        cache.save('foo', foo)
    
    # `inject.instance` requests dependencies from the injector.
    def foo(bar):
        cache = inject.instance(Cache)
        cache.save('bar', bar)
    
    # `inject.attr` creates properties (descriptors) which request dependencies on access.
    class User(object):
        cache = inject.attr(Cache)
                
        def __init__(self, id):
            self.id = id

        def save(self):
            self.cache.save('users', self)
        
        @classmethod
        def load(cls, id):
            return cls.cache.load('users', id)
    
    
    # Create an optional configuration.
    def my_config(binder):
        binder.install(my_config2)  # Add bindings from another config.
        binder.bind(Cache, RedisCache('localhost:1234'))
    
    # Configure a shared injector.
    inject.configure(my_config)
    
    
    # Instantiate User as a normal class. Its `cache` dependency is injected when accessed.
    user = User(10)
    user.save()
    
    # Call the functions, the dependencies are automatically injected.
    foo('Hello')
    bar('world')

Testing
-------
In tests use ``inject.clear_and_configure(callable)`` to create a new injector on setup,
and optionally ``inject.clear()`` to clean up on tear down::
    
    class MyTest(unittest.TestCase):
        def setUp(self):
            inject.clear_and_configure(lambda binder: binder
                .bind(Cache, Mock() \
                .bind(Validator, TestValidator())
        
        def tearDown(self):
            inject.clear()


Thread-safety
-------------
After configuration the injector is thread-safe and can be safely reused by multiple threads.

Binding types
-------------
- Instance bindings always return the same instance::
    
    redis = RedisCache(address='localhost:1234')
    def config(binder):
        binder.bind(Cache, redis)
    
- Constructor bindings create a singleton on injection::
    
    def config(binder):
        # Creates a redis cache singleton on first injection.
        binder.bind_to_constructor(Cache, lambda: RedisCache(address='localhost:1234'))

- Provider bindings call the provider on injection::

    def get_my_thread_local_cache():
        pass

    def config(binder):
        # Executes the provider on each injection.
        binder.bind_to_provider(Cache, get_my_thread_local_cache) 

- Runtime bindings automatically create singletons on injection, require no configuration.
  For example, only the ``Config`` class binding is present, other bindings are runtime::

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
     
    inject.configure(lambda binder: binder.bind(Config, load_config_file()))
    user = User.load(10)

Keys
----
It is possible to use any hashable object as a binding key.
For example::
    
    import inject
    
    inject.configure(lambda binder: \
        binder.bind('host', 'localhost') \
        binder.bind('port', 1234))


Why no scopes?
--------------
I've used Guice and Spring in Java for a lot of years, and I don't like their scopes.
``python-inject`` by default creates objects as singletons. It does not need a prototype scope
as in Spring or NO_SCOPE as in Guice because ``python-inject`` does not steal your class 
constructors. Create instances the way you like and then inject dependencies into them.

Other scopes such as a request scope or a session scope are fragile, introduce high coupling,
and are difficult to test. In ``python-inject`` write custom providers which can be thread-local, 
request-local, etc.

For example, a thread-local current user provider::

    import inject
    import threading
    
    # Given a user class.
    class User(object):
        pass
    
    # Create a thread-local current user storage.
    _LOCAL = threading.local()
    
    def get_current_user():
        return getattr(_LOCAL, 'user', None)
    
    def set_current_user(user):
        _LOCAL.user = user
    
    # Bind User to a custom provider.
    inject.configure(lambda binder: binder.bind_to_provider(User, get_current_user))
    
    # Inject the current user.
    @inject.param('user', User)
    def foo(user):
        pass


Links
-----
- Project: https://github.com/ivan-korobkov/python-inject
- Google Groups: https://groups.google.com/d/forum/python-inject

License
-------
Apache License 2.0
