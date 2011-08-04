import unittest

import inject
from inject.middleware import DjangoInjectMiddleware, WsgiInjectMiddleware


class WsgiTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = inject.Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def test(self):
        class User(object):
            i = 0
            def __init__(self):
                self.__class__.i += 1
                self.name = 'user%s' % self.i 
        
        @inject.param('scope', inject.reqscope)
        def app(environ, start_response, scope):
            @inject.param('user', User)
            def greet_user(user):
                return u'Hello, %s' % user.name
            
            @inject.param('user', User)
            def foo(user):
                return
            
            user = User()
            scope.bind(User, user)
            
            foo() # So that the same user is injected twice.
            yield greet_user()
        
        app = WsgiInjectMiddleware(app)
        
        greet1 = list(app({}, None))[0]
        greet2 = list(app({}, None))[0]
        greet3 = list(app({}, None))[0]
        
        self.assertEqual(User.i, 3)
        
        self.assertEqual(greet1, u'Hello, user1')
        self.assertEqual(greet2, u'Hello, user2')
        self.assertEqual(greet3, u'Hello, user3')


class DjangoTestCase(unittest.TestCase):
    
    middleware_class = DjangoInjectMiddleware
    
    def setUp(self):
        self.injector = inject.Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def test(self):
        '''Test Django middleware.'''
        request = None
        
        m = DjangoInjectMiddleware()
        m.process_request(request)        
        m.process_response(request, None)
        
        raise AssertionError()
    
    def test_response(self):
        '''Test Django middleware response.'''
        m = DjangoInjectMiddleware()
        
        response = object()
        self.assertTrue(m.process_response(None, response) is response)
