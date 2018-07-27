from unittest import TestCase

import inject


class TestFunctional(TestCase):
    def tearDown(self):
        inject.clear()

    def test(self):
        class Config(object):
            def __init__(self, greeting):
                self.greeting = greeting

        class Cache(object):
            config = inject.attr(Config)

            def load_greeting(self):
                return self.config.greeting

        class User(object):
            cache = inject.attr(Cache)

            def __init__(self, name):
                self.name = name

            def greet(self):
                return '%s, %s' % (self.cache.load_greeting(), self.name)

        def config(binder):
            binder.bind(Config, Config('Hello'))

        inject.configure(config)

        user = User('John Doe')
        greeting = user.greet()
        assert greeting == 'Hello, John Doe'
