import unittest

import inject
from inject.middleware import DjangoInjectMiddleware, WsgiInjectMiddleware
from inject.exc import CantGetInstanceError


class WsgiTestCase(unittest.TestCase):
    
    def setUp(self):
        self.injector = inject.Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def test(self):
        '''Test WSGI middleware.'''
        class Object(object):
            
            count = 0
            
            def __new__(cls):
                cls.count += 1
                return super(Object, cls).__new__(cls)
            
            def __init__(self):
                self.i = self.count
        
        self.injector.bind(Object, scope=inject.RequestScope)
        
        class Application(object):
            
            @inject.param('obj', Object)
            def __init__(self, environ, start_response, obj):
                pass
            
            @inject.param('obj', Object)
            def __iter__(self, obj):
                yield obj
        
        app = WsgiInjectMiddleware(Application)
        
        obj = list(app({}, None))[0]
        obj2 = list(app({}, None))[0]
        obj3 = list(app({}, None))[0]
        
        # Only 3 instances should be created - one for each request.
        self.assertEqual(Object.count, 3)
        
        self.assertEqual(obj.i, 1)
        
        self.assertTrue(obj2 is not obj)
        self.assertEqual(obj2.i, 2)
        
        self.assertTrue(obj3 is not obj2)
        self.assertEqual(obj3.i, 3)


class DjangoTestCase(unittest.TestCase):
    
    middleware_class = DjangoInjectMiddleware
    
    def setUp(self):
        self.injector = inject.Injector()
        self.injector.register()
    
    def tearDown(self):
        self.injector.unregister()
    
    def test(self):
        '''Test Django middleware.'''
        class Object(object):
            
            count = 0
            
            def __new__(cls):
                cls.count += 1
                return super(Object, cls).__new__(cls)
            
            def __init__(self):
                self.i = self.count
        
        self.injector.bind(Object, scope=inject.RequestScope)
        
        class Request(object):
            
            @inject.param('obj', Object)
            def get_obj(self, obj):
                return obj
            
        request = Request()
        
        m = DjangoInjectMiddleware()
        self.assertRaises(CantGetInstanceError, request.get_obj)
        
        m.process_request(request)
        
        self.assertEqual(request.get_obj().i, 1)
        self.assertEqual(request.get_obj().i, 1)
        self.assertTrue(request.get_obj() is request.get_obj())
        
        m.process_response(request, None)
        self.assertRaises(CantGetInstanceError, request.get_obj)
    
    def test_response(self):
        '''Test Django middleware response.'''
        m = DjangoInjectMiddleware()
        
        response = object()
        self.assertTrue(m.process_response(None, response) is response)
