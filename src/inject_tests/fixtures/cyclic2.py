import inject

from inject_tests.fixtures.cyclic1 import A, P, func


class B(object):
    
    a = inject.attr(A)


class Q(object):
    
    p = inject.named_attr('p', P)


class Z(object):
    
    get_z = staticmethod(func)
