import inject
#from inject import scopes


class Provider(object):
    
    def __init__(self):
        pass
    
    def __call__(self):
        return 'asdf'


class A(object):
    
    def asdf(self):
        return 'asdf'


class B(object):
    
    a = inject.attr('a', A)
    a2 = inject.attr('a2', A.asdf)
    a3 = inject.attr('a3', A)
    a4 = inject.attr('a4', A)


b = B()
print b.a2
b2 = B()


class AFactory(object):
    
    a_class = A
    
    def get(self):
        return self.a_class()


class C(object):
    
    def __init__(self):
        self.a = A()


class C2(object):
    
    afactory = AFactory()
    
    def __init__(self):
        self.a = self.afactory.get()


class D(object):
    
    @inject.param('a', A)
    def __init__(self, a):
        self.a = a


d = D()
d2 = D()


#import cProfile
#
#def run(n, D=D):
#    for x in xrange(n):
#        d = D()
#cProfile.run('run(100000)', sort=1)

import timeit
n = 10**5
print timeit.Timer('C().a', 'from __main__ import C').timeit(n)
print timeit.Timer('C2().a', 'from __main__ import C2').timeit(n)
print timeit.Timer('B().a;', 'from __main__ import B').timeit(n)
print timeit.Timer('B().a2;', 'from __main__ import B').timeit(n)
print timeit.Timer('D()', 'from __main__ import D').timeit(n)