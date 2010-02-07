import unittest

import inject
from inject import errors
from inject.middleware import WsgiInjectMiddleware, DjangoInjectMiddleware


class WsgiTestCase(unittest.TestCase):
    
    middleware_class = WsgiInjectMiddleware
    
    def test(self):
        '''Test WSGI middleware.'''
        class Counter(object):
            
            i = 0
            def __init__(self):
                self.__class__.i += 1
            
            def __str__(self):
                return str(self.i)
        
        
        class Response(object):
            
            @inject.param('counter', Counter, scope=inject.reqscope)
            def __init__(self, counter):
                self.counter = counter
            
            def __iter__(self):
                yield 'Start'
                yield 'Request #%s' % self.counter
                yield 'End'
        
        
        class Application(object):
            
            @inject.param('counter', Counter, scope=inject.reqscope)
            def __init__(self, environ, start_response, counter):
                self.counter = counter
            
            def __iter__(self):
                return iter(Response())
        
        app = self.middleware_class(Application)
        
        response = list(app({}, None))
        response2 = list(app({}, None))
        response3 = list(app({}, None))
        self.assertEqual(response, ['Start', 'Request #1', 'End'])
        self.assertEqual(response2, ['Start', 'Request #2', 'End'])
        self.assertEqual(response3, ['Start', 'Request #3', 'End'])


class DjangoTestCase(unittest.TestCase):
    
    middleware_class = DjangoInjectMiddleware
    
    def test(self):
        '''Test Django middleware.'''
        class Counter(object):
            
            i = 0
            def __init__(self):
                self.__class__.i += 1
            
            def __str__(self):
                return str(self.i)
        
        class Request(object):
            def __init__(self):
                self.META = {}
            
            @inject.param('counter', Counter, scope=inject.reqscope)
            def do(self, counter):
                return str(counter)
            
            @inject.param('counter', Counter, scope=inject.reqscope)
            def do2(self, counter):
                return str(counter)
            
            @inject.param('counter', Counter, scope=inject.reqscope)
            def do3(self, counter):
                return str(counter)
            
        request = Request()
        
        m = self.middleware_class()
        mresponse = m.process_request(request)
        self.assertTrue(mresponse is None)
        
        c1 = request.do()
        c2 = request.do()
        self.assertEqual(c1, '1')
        self.assertEqual(c2, '1')
        
        response = object()
        response2 = m.process_response(request, response)
        self.assertTrue(response2 is response)
        
        self.assertRaises(errors.NoRequestRegisteredError, request.do3)