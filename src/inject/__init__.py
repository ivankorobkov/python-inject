'''C{python-inject} is a fast and simple to use python dependency injection
framework. It uses decorators and descriptors to reference external
dependencies, and scopes to specify objects life-cycles.

C{python-inject} has been created to provide the I{pythonic} way of dependency 
injection, utilizing specific Python functionality.

Links
=====

    - Project's site: U{http://code.google.com/p/python-inject}
    - User's Guide: U{http://code.google.com/p/python-inject/wiki/UsersGuide}
    - Tutorial: U{http://code.google.com/p/python-inject/wiki/Tutorial}
    - API: U{http://api.python-inject.googlecode.com/hg/html/index.html}
    - Source code: U{http://github.com/ivan-korobkov/python-inject}


Short Tutorial
==============
See the I{examples} directory and I{User's Guide} for more information.
You can find this file in I{examples/simple.py}::
    
    """Basic python-inject example, execute it to see the output.
    
    All memcached, redis and mail classes are dummy classes that do not connect
    to anything. They are only used to demonstrate the dependency injection
    principle and python-inject functionality.
    """
    import inject    
    
    class Memcached(object):
        """Dummy memcached backend, always returns None."""
        def __init__(self, host, port):
            print 'Connected memcached to %s:%s' % (host, port)
        
        def get(self, key):
            """Always return None."""
            return None
    
    class Redis(object):
        """Redis backend, always returns a new User instance for any key."""
        def __init__(self, host, port):
            print 'Connected redis to %s:%s' % (host, port)
        
        def get(self, key):
            return User("Ivan Korobkov", "ivan.korobkov@gmail.com")
    
    class MailService(object):
        """Sends emails."""
        def send(self, email, text):
            """send an email."""
            print "Sent an email to %s, text=%s." % (email, text)
    
    
    class User(object):
    
        """Example model."""
    
        # Both Redis and Memcached are injected as class attributes
        # so they can be accessed from the classmethods.
        redis = inject.class_attr(Redis)
        memcached = inject.class_attr(Memcached)
        
        # MailService is injected as a normal attribute, it can be accessed
        # only from the normal (bound) methods, not classmethods.
        mail_service = inject.attr(MailService)
        
        @classmethod
        def get_by_id(cls, id):
            """Get a user from memcached, if not present fallback to redis."""
            key = 'user-%s' % id
            user = cls.memcached.get(key)
            if user:
                return user
            user = cls.redis.get(key)
            print 'Loaded %s from redis.' % user
            return user
        
        def __init__(self, name, email):
            self.name = name
            self.email = email
        
        def __str__(self):
            return '<User "%s">' % self.name
        
        @inject.param("hello_text")
        def greet(self, hello_text):
            """Send a greeting email to the user.
            
            @param hello_text: Demonstrates injecting params into functions. 
            """
            text = hello_text % self.name
            self.mail_service.send(self.email, text)
    
    
    if __name__ == '__main__':
        """Register an injector, configure the bindings and send a greeting
        email to a user. Usually, you should store your bindings in another
        function (or functions) in another module.
        
        For example:
            # bindings.py
            def config(injector):
                config_redis(injector)
                config_memcached(injector)
                # etc.
            
            def config_redis(injector)
                redis = Redis('myhost', 1234)
                injector.bind(Redis, redis)
            
            def config_memached(injector):
                memcached = Memcached('myhost', 2345)
                injector.bind(Memcached, memcached)
        
        """
        injector = inject.Injector()
        injector.register()
        
        memcached = Memcached('localhost', 2345)
        redis = Redis('localhost', 1234)
        
        injector.bind(Redis, redis)
        injector.bind(Memcached, memcached)
        injector.bind("hello_text", "Hello, %s!")
        
        user = User.get_by_id(10)
        user.greet()


@author: Ivan Korobkov <ivan.korobkov@gmail.com>
@copyright: 2010, 2011 Ivan Korobkov
@license: MIT License, see LICENSE
@version: 2.0-beta
'''
__version__ = '2.0-beta'


from inject import exc
from inject.injections import attr, named_attr, class_attr, param, \
    super_param as super
from inject.imports import lazy
from inject.injectors import Injector, create, get_instance, register, \
    unregister, is_registered
from inject.scopes import appscope, noscope, threadscope, reqscope
